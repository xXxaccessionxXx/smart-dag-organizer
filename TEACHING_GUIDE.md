# Teaching Your Neural Assistant

The Neural Assistant learns in three ways. This guide explains how to feed it data effectively.

## 1. Explicit Learning (Commands)
You can directly teach the AI Q&A pairs.

**Command:** `/learn Question : Answer`
- **Example:** `/learn What is the server IP? : 192.168.1.50`
- **Example:** `/learn Who is the lead dev? : Kasey`

> **Tip:** The AI ignores common noise words (is, the, a). So "What **is** the IP" is treated same as "What IP".

## 2. Opinions (Subjective)
You can give the AI opinions on topics. It will use these when you ask "What do you think?"

**Command:** `/opinion Topic : Thought`
- **Example:** `/opinion Python : Python is elegant and powerful.`
- **Example:** `/opinion Bugs : Bugs are just undocumented features.`

**Retrieval:**
- User: "What is your opinion on Python?"
- AI: "Here is my thought: Python is elegant and powerful."

## 3. Passive Learning (Implicit)
If you state a fact clearly (without a question mark), the AI notes it.

- **You:** "My favorite color is blue."
- **AI:** "I have noted that."
- **Later:** "What is my favorite color?" -> "I recall you saying: 'My favorite color is blue.'"

## 4. Bulk Editing (Advanced)
For faster training, you can edit the memory file directly.
**File:** `Directed Acyclic Graph (DAG)/brain_memory.json`

**Structure:**
```json
{
    "qa": [
        {"q": "keyword1 keyword2", "a": "Your defined answer."}
    ],
    "opinions": [
        {"topic": "topic_name", "thought": "The opinion text."}
    ],
    "facts": [
        "Any stored fact string."
    ]
}
```
**Note:** Changes to the file require restarting the Assistant to take effect.
