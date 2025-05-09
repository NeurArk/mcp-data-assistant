from __future__ import annotations
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class SessionContext:
    """
    Stores context information for a chat session.
    """

    # History tracking
    messages: List[Dict[str, str]] = field(default_factory=list)

    # File tracking
    files: Dict[str, str] = field(default_factory=dict)

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """
    Manages conversation sessions and context for the agent.

    This class handles:
    - Creating and tracking session IDs
    - Storing conversation history per session
    - Managing file references
    - Providing context to the agent
    """

    def __init__(self):
        self.sessions: Dict[str, SessionContext] = {}

    def create_session(self) -> str:
        """
        Create a new session with a unique ID.

        Returns:
            str: The session ID
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = SessionContext()
        return session_id

    def get_session(self, session_id: str) -> Optional[SessionContext]:
        """
        Get the session context for a specific session ID.

        Args:
            session_id: The session ID to retrieve

        Returns:
            Optional[SessionContext]: The session context if found, None otherwise
        """
        return self.sessions.get(session_id)

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Add a message to the conversation history.

        Args:
            session_id: The session ID
            role: The role of the message sender (user/assistant)
            content: The message content
        """
        session = self.get_session(session_id)
        if session:
            session.messages.append({"role": role, "content": content})

    def get_messages(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get all messages for a session.

        Args:
            session_id: The session ID

        Returns:
            List[Dict[str, str]]: The conversation history
        """
        session = self.get_session(session_id)
        if session:
            return session.messages
        return []

    def remove_last_message(self, session_id: str) -> bool:
        """
        Remove the last message from the conversation history.

        Args:
            session_id: The session ID

        Returns:
            bool: True if a message was removed, False otherwise
        """
        session = self.get_session(session_id)
        if session and session.messages:
            removed = session.messages.pop()
            print(f"Removed last message: {removed.get('role', '?')}")
            return True
        return False

    def register_file(self, session_id: str, file_type: str, file_path: str) -> None:
        """
        Register a file with the session.

        Args:
            session_id: The session ID
            file_type: The type of file (e.g., 'csv', 'pdf')
            file_path: The path to the file
        """
        session = self.get_session(session_id)
        if session:
            session.files[file_type] = file_path

    def get_file(self, session_id: str, file_type: str) -> Optional[str]:
        """
        Get the registered file path for a specific type.

        Args:
            session_id: The session ID
            file_type: The type of file to retrieve

        Returns:
            Optional[str]: The file path if found, None otherwise
        """
        session = self.get_session(session_id)
        if session and file_type in session.files:
            return session.files[file_type]
        return None

    def get_file_references(self, session_id: str) -> Dict[str, str]:
        """
        Get all file references for a session.

        Args:
            session_id: The session ID

        Returns:
            Dict[str, str]: Dictionary of file types to file paths
        """
        session = self.get_session(session_id)
        if session:
            return session.files.copy()
        return {}

    def create_system_prompt(self, session_id: str, base_prompt: str) -> str:
        """
        Create a system prompt that includes file references.

        Args:
            session_id: The session ID
            base_prompt: The base system prompt

        Returns:
            str: Enhanced system prompt with file references
        """
        session = self.get_session(session_id)
        if not session:
            return base_prompt

        # If files are registered, add them to the prompt
        if session.files:
            file_info = "\n\nAvailable files:\n"
            for file_type, file_path in session.files.items():
                file_info += f"- {file_type.upper()}: {file_path}\n"

            return base_prompt + file_info

        return base_prompt

    def clear_session(self, session_id: str) -> bool:
        """
        Clear the conversation history for a session but keep file references.

        Args:
            session_id: The session ID

        Returns:
            bool: True if the session was cleared, False if not found
        """
        session = self.get_session(session_id)
        if session:
            # Clear messages but preserve file references
            files_copy = session.files.copy()  # Make a copy for debug reporting
            # No need to copy metadata for now, but might be useful in the future

            # Reset messages to empty list
            session.messages = []

            # Debug logging
            print(f"SessionManager: Cleared messages for session {session_id}")
            print(f"SessionManager: Preserved {len(files_copy)} file references")

            return True

        print(f"SessionManager: Session {session_id} not found")
        return False

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session completely.

        Args:
            session_id: The session ID to delete

        Returns:
            bool: True if the session was deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False


# Global instance
session_manager = SessionManager()
