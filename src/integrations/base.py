from abc import ABC, abstractmethod

class Integration(ABC):
    """
    Abstract Base Class for all integrations.
    """
    def __init__(self, manager):
        self.manager = manager

    @property
    @abstractmethod
    def id(self):
        """Unique identifier for the integration (e.g., 'google_calendar')."""
        pass

    @property
    @abstractmethod
    def name(self):
        """Display name for the integration (e.g., 'Google Calendar')."""
        pass

    @abstractmethod
    def is_configured(self):
        """Returns True if the integration is fully configured (e.g., has valid tokens)."""
        pass

    @abstractmethod
    def check_connection(self):
        """Checks if the integration is working correctly. Returns True/False."""
        pass
    
    @abstractmethod
    def get_actions(self):
        """
        Returns a list of actions available for a node.
        Each action is a dict: {'id': 'create_event', 'label': 'Create Event', 'callback': func}
        """
        pass
