import json
import os
import uuid
from typing import Dict, Any
from datetime import datetime
from utils.supabase_client import save_user_data, load_user_data

class DataPersistence:
    def __init__(self, data_dir: str = "data"):
        """Initialize data persistence with a data directory"""
        self.data_dir = data_dir
        self.default_user_id = "anonymous"
        os.makedirs(data_dir, exist_ok=True)
        self.use_supabase = True  # Flag to determine whether to use Supabase or local files
    
    def save_user_data(self, data: Dict[str, Any], user_id: str = None) -> bool:
        """Save user data to Supabase or a JSON file"""
        try:
            # Use default user ID if none provided
            user_id = user_id or self.default_user_id
            
            # Add timestamp
            data["last_updated"] = datetime.now().isoformat()
            
            if self.use_supabase:
                # Save to Supabase
                try:
                    save_user_data(user_id, data)
                    print(f"Successfully saved data to Supabase for user {user_id}")
                except Exception as e:
                    print(f"Error saving to Supabase: {str(e)}, falling back to local file")
                    # Fall back to local file if Supabase fails
                    file_path = os.path.join(self.data_dir, f"user_{user_id}.json")
                    with open(file_path, "w") as f:
                        json.dump(data, f, indent=2)
            else:
                # Save to file (fallback)
                file_path = os.path.join(self.data_dir, f"user_{user_id}.json")
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving user data: {str(e)}")
            return False
    
    def load_user_data(self, user_id: str = None) -> Dict[str, Any]:
        """Load user data from Supabase or JSON file"""
        try:
            # Use default user ID if none provided
            user_id = user_id or self.default_user_id
            
            if self.use_supabase:
                # Load from Supabase
                try:
                    user_data = load_user_data(user_id)
                    if user_data:
                        print(f"Successfully loaded data from Supabase for user {user_id}")
                        return user_data
                    else:
                        print(f"No data found in Supabase for user {user_id}, checking local file")
                except Exception as e:
                    print(f"Error loading from Supabase: {str(e)}, falling back to local file")
            
            # Load from file (fallback)
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
            # Get user_id from session state if available, or generate a unique ID if not present
            if not user_id:
                if "user_context" in session_state and "user_id" in session_state["user_context"]:
                    user_id = session_state["user_context"]["user_id"]
                else:
                    # If no user_id exists, create one and add it to the user_context
                    if "user_context" not in session_state:
                        session_state["user_context"] = {}
                    
                    if "user_id" not in session_state["user_context"]:
                        user_id = str(uuid.uuid4())
                        session_state["user_context"]["user_id"] = user_id
                    else:
                        user_id = session_state["user_context"]["user_id"]
            
            # Ensure we have a user_id
            user_id = user_id or self.default_user_id
            
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
            
            # Ensure user_id is in the saved data
            if "user_context" in save_vars and "user_id" not in save_vars["user_context"]:
                save_vars["user_context"]["user_id"] = user_id
            
            success = self.save_user_data(save_vars, user_id)
            if success:
                print(f"Successfully saved session state for user {user_id}")
            else:
                print(f"Failed to save session state for user {user_id}")
            
            return success
        except Exception as e:
            print(f"Error saving session state: {str(e)}")
            return False
    
    def load_session_state(self, user_id: str = None) -> Dict[str, Any]:
        """Load session state from saved data"""
        return self.load_user_data(user_id) 