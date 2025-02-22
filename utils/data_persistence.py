import json
import os
from typing import Dict, Any
from datetime import datetime

class DataPersistence:
    def __init__(self, data_dir: str = "data"):
        """Initialize data persistence with a data directory"""
        self.data_dir = data_dir
        self.default_user_id = "anonymous"
        os.makedirs(data_dir, exist_ok=True)
    
    def save_user_data(self, data: Dict[str, Any], user_id: str = None) -> bool:
        """Save user data to a JSON file"""
        try:
            # Use default user ID if none provided
            user_id = user_id or self.default_user_id
            
            # Add timestamp
            data["last_updated"] = datetime.now().isoformat()
            
            # Save to file
            file_path = os.path.join(self.data_dir, f"user_{user_id}.json")
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving user data: {str(e)}")
            return False
    
    def load_user_data(self, user_id: str = None) -> Dict[str, Any]:
        """Load user data from JSON file"""
        try:
            # Use default user ID if none provided
            user_id = user_id or self.default_user_id
            
            file_path = os.path.join(self.data_dir, f"user_{user_id}.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading user data: {str(e)}")
            return {}
    
    def save_session_state(self, session_state: Dict[str, Any], user_id: str = None) -> bool:
        """Save specific session state variables"""
        try:
            # Filter out non-serializable objects and save important state
            save_vars = {
                "user_context": session_state.get("user_context", {}),
                "chat_history": session_state.get("chat_history", []),
                "saved_jobs": session_state.get("saved_jobs", []),
                "saved_interviews": session_state.get("saved_interviews", []),
                "saved_career_plans": session_state.get("saved_career_plans", []),
                "skill_progress": session_state.get("skill_progress", {}),
                "profile_completed": session_state.get("profile_completed", False)
            }
            return self.save_user_data(save_vars, user_id)
        except Exception as e:
            print(f"Error saving session state: {str(e)}")
            return False
    
    def load_session_state(self, user_id: str = None) -> Dict[str, Any]:
        """Load session state from saved data"""
        return self.load_user_data(user_id) 