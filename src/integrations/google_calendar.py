import os
import datetime
import datetime
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PyQt6.QtWidgets import QMessageBox, QInputDialog

from .base import Integration

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarIntegration(Integration):
    def __init__(self, manager):
        super().__init__(manager)
        self.service = None
        self.creds = None

    @property
    def id(self):
        return "google_calendar"

    @property
    def name(self):
        return "Google Calendar"

    def is_configured(self):
        return os.path.exists(self.manager.token_path)

    def check_connection(self):
        try:
            self.get_service()
            return True
        except Exception as e:
            print(f"Google Calendar Connection Check Failed: {e}")
            return False

    def get_service(self):
        if self.service:
            return self.service

        creds = None
        token_path = self.manager.token_path
        
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            except Exception:
                os.remove(token_path)
                creds = None

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                     creds = None
            
            if not creds:
                # 1. Check AppData (User Override)
                creds_path = self.manager.credentials_path
                
                # 2. Check Bundled Assets (Default)
                if not os.path.exists(creds_path):
                    from src.utils.assets import resource_path
                    bundled_path = resource_path("assets/credentials.json")
                    if os.path.exists(bundled_path):
                        creds_path = bundled_path

                # 3. Check Encrypted Assets (Fallback for public repo)
                if not os.path.exists(creds_path):
                    from src.utils.assets import resource_path
                    from src.utils.security import decrypt_credentials
                    import json
                    import tempfile
                    
                    enc_path = resource_path("assets/credentials.enc")
                    if os.path.exists(enc_path):
                        print(f"Loading credentials from encrypted storage: {enc_path}")
                        decrypted_data = decrypt_credentials(enc_path)
                        if decrypted_data:
                            # We must provide a path to InstalledAppFlow, or use from_client_config
                            # from_client_config is cleaner but requires changing how we call it.
                            # Existing code uses from_client_secrets_file(creds_path...)
                            
                            # Let's create a temporary file to keep logic simple and compatible
                            # The file should be deleted immediately after use
                            try:
                                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
                                    json.dump(decrypted_data, tmp)
                                    tmp_creds_path = tmp.name
                                
                                flow = InstalledAppFlow.from_client_secrets_file(tmp_creds_path, SCOPES)
                                creds = flow.run_local_server(port=0)
                                
                                # Cleanup temp file
                                os.unlink(tmp_creds_path)
                                
                                # Skip the normal flow below since we just did it
                                # Save the credentials for the next run
                                with open(token_path, 'w') as token:
                                    token.write(creds.to_json())
                                    
                                self.creds = creds
                                self.service = build('calendar', 'v3', credentials=creds)
                                return self.service
                                
                            except Exception as e:
                                print(f"Failed to load from encrypted credentials: {e}")

                if not os.path.exists(creds_path):
                    raise FileNotFoundError(f"Credentials file not found. Please place 'credentials.json' in {self.manager.credentials_path} or ensure it is bundled in assets.")

                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        self.creds = creds
        self.service = build('calendar', 'v3', credentials=creds)
        return self.service

    def create_event(self, summary="New Event", description="Created via Smart DAG", start_time=None, end_time=None):
        service = self.get_service()
        if not service:
            return None

        if not start_time:
            start_time = datetime.datetime.utcnow()
        
        if not end_time:
            end_time = start_time + datetime.timedelta(hours=1)

        # Ensure we have datetime objects
        if isinstance(start_time, str):
             # Assume ISO format if string passed (though usually we pass objects now)
             pass 
        else:
             start_time = start_time.isoformat() + 'Z'
             
        if not isinstance(end_time, str):
             end_time = end_time.isoformat() + 'Z'

        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        return event.get('htmlLink')

    def list_upcoming_events(self, max_results=10):
        """Fetches the upcoming events from the user's primary calendar."""
        service = self.get_service()
        if not service:
            return []

        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=max_results, singleEvents=True,
                                              orderBy='startTime').execute()
        return events_result.get('items', [])

    def get_actions(self):
        return [
            {
                "id": "create_event_custom",
                "label": "📅 Create Custom Event...",
                "callback": self.action_create_custom_event
            },
            {
                "id": "create_event_now",
                "label": "⚡ Create 1hr Event Now",
                "callback": self.action_create_event_now
            }
        ]

    def action_create_event_now(self, node):
        """Callback to create an event for the given node starting now."""
        try:
            now = datetime.datetime.utcnow()
            end = now + datetime.timedelta(hours=1)
            
            summary = node.name
            description = node.notes if node.notes else f"Task from SmartDAG: {node.name}"
            
            link = self.create_event(summary, description, now, end)
            
            QMessageBox.information(None, "Success", f"Event created!")
            
            if not node.watch_path:
                 node.set_attachment(link, "Link")
                 
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to create event: {e}")

    def action_create_custom_event(self, node):
        from src.ui.event_dialog import EventDialog
        
        dialog = EventDialog()
        dialog.txt_summary.setText(node.name)
        dialog.txt_description.setPlainText(node.notes)
        
        if dialog.exec():
            data = dialog.get_data()
            try:
                # QDateTime to Python datetime
                # QDateTime.toPyDateTime returns a naive datetime (local time usually)
                # Google API expects ISO formatted string with timezone or UTC 'Z'
                
                # Simple approach: Treat selected time as local, convert to UTC for API
                # But our create_event expects objects and converts them to UTC Z.
                # Let's start by passing the raw python datetime objects (which are naive local from QDateTime)
                # We need to be careful about timezone.
                
                # Actually, let's keep it simple. We pass the objects.
                # In create_event, we do .isoformat() + 'Z'. 
                # If the object is naive, isoformat() is naive. + 'Z' implies UTC.
                # So we must ensure the datetime object IS in UTC before passing it, 
                # OR we adjust create_event to handle local time.
                
                # Let's convert to UTC here.
                start_local = data['start_time']
                end_local = data['end_time']
                
                # Assuming system local time
                start_utc = start_local.astimezone(datetime.timezone.utc)
                end_utc = end_local.astimezone(datetime.timezone.utc)

                link = self.create_event(
                    summary=data['summary'],
                    description=data['description'],
                    start_time=start_utc,
                    end_time=end_utc
                )
                
                QMessageBox.information(None, "Success", f"Event created!")
                
                if not node.watch_path:
                     node.set_attachment(link, "Link")

            except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to create event: {e}")
