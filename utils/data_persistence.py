import json
import os
import uuid
from typing import Dict, Any, List
from datetime import datetime
from utils.supabase_client import (
    save_user_data, load_user_data, 
    save_learning_path, get_user_learning_paths, update_learning_path_progress,
    save_career_path, get_user_career_paths, update_career_path_progress,
    save_user_skill, get_user_skills, update_user_skill, delete_user_skill,
    save_skill_progress, save_skill_analysis
)
import streamlit as st
import traceback

class DataPersistence:
    def __init__(self, data_dir: str = "data"):
        """Initialize data persistence with a data directory"""
        self.data_dir = data_dir
        # Use a valid UUID as default user ID instead of "anonymous"
        self.default_user_id = str(uuid.uuid4())
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
            
            # If we get here, try loading the anonymous file as a last resort
            legacy_file_path = os.path.join(self.data_dir, "user_anonymous.json")
            if os.path.exists(legacy_file_path):
                print(f"Loading legacy anonymous user data from {legacy_file_path}")
                with open(legacy_file_path, "r") as f:
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
            
            # Debug info about user ID
            print(f"Saving session state for user ID: {user_id}")
            
            # Filter out non-serializable objects and save important state
            save_vars = {
                "user_context": session_state.get("user_context", {}),
                "chat_history": session_state.get("chat_history", []),
                "saved_jobs": session_state.get("saved_jobs", []),
                "saved_interviews": session_state.get("saved_interviews", []),
                "saved_career_plans": session_state.get("saved_career_plans", []),
                "skill_progress": session_state.get("skill_progress", {}),
                "profile_completed": session_state.get("profile_completed", False),
                "current_learning_path": session_state.get("current_learning_path", {})
            }
            
            # Ensure the current_learning_path is properly structured before saving
            if "current_learning_path" in save_vars:
                current_learning_path = save_vars["current_learning_path"]
                
                # Debug output for current learning path
                print(f"DEBUG [data_persistence]: Saving current_learning_path: {current_learning_path}")
                
                # Ensure it has the required fields
                if current_learning_path and isinstance(current_learning_path, dict):
                    # Ensure title exists
                    if "title" not in current_learning_path:
                        print("WARNING [data_persistence]: current_learning_path missing title")
                        current_learning_path["title"] = "Unknown Path"
                    
                    # Ensure progress exists and is properly structured
                    if "progress" not in current_learning_path:
                        print("WARNING [data_persistence]: current_learning_path missing progress")
                        current_learning_path["progress"] = {"completed": 0, "total": 100}
                    elif not isinstance(current_learning_path["progress"], dict):
                        print(f"WARNING [data_persistence]: current_learning_path has invalid progress type: {type(current_learning_path['progress'])}")
                        current_learning_path["progress"] = {"completed": 0, "total": 100}
                    elif "completed" not in current_learning_path["progress"]:
                        print("WARNING [data_persistence]: current_learning_path progress missing completed field")
                        current_learning_path["progress"]["completed"] = 0
                    
                    # Ensure the progress field has numeric values
                    try:
                        progress_value = current_learning_path["progress"]["completed"]
                        if not isinstance(progress_value, (int, float)):
                            print(f"WARNING [data_persistence]: Non-numeric progress value: {progress_value}, attempting to convert")
                            current_learning_path["progress"]["completed"] = int(progress_value)
                    except (TypeError, ValueError):
                        print("WARNING [data_persistence]: Could not convert progress to numeric value, using 0")
                        current_learning_path["progress"]["completed"] = 0
                
                # Update the save_vars with the potentially fixed current_learning_path
                save_vars["current_learning_path"] = current_learning_path
            
            # Debug info about what's being saved
            print(f"Saving session state with the following keys: {save_vars.keys()}")
            if "current_learning_path" in save_vars and save_vars["current_learning_path"]:
                print(f"DEBUG [data_persistence]: current_learning_path progress: {save_vars['current_learning_path'].get('progress', {})}")
            if "skill_progress" in save_vars:
                print(f"DEBUG [data_persistence]: Saving {len(save_vars['skill_progress'])} skills in progress data")
            
            # Ensure user_id is in the saved data
            if "user_context" in save_vars and "user_id" not in save_vars["user_context"]:
                save_vars["user_context"]["user_id"] = user_id
            
            # Save learning paths and career paths if they exist
            if "current_learning_path" in save_vars and save_vars["current_learning_path"]:
                self.save_learning_path(user_id, save_vars["current_learning_path"])
            
            if "career_path" in session_state and session_state["career_path"]:
                self.save_career_path(user_id, session_state["career_path"])
            
            # Save skill progress data
            if "skill_progress" in save_vars and save_vars["skill_progress"]:
                for skill_name, progress_data in save_vars["skill_progress"].items():
                    try:
                        print(f"Saving progress data for skill: {skill_name}")
                        # Ensure progress_percentage is calculated
                        if "progress_percentage" not in progress_data and "learning_path" in progress_data and "objectives" in progress_data["learning_path"]:
                            total_objectives = len(progress_data["learning_path"]["objectives"])
                            completed = len(progress_data.get("completed_objectives", []))
                            progress_data["progress_percentage"] = int((completed / total_objectives) * 100) if total_objectives > 0 else 0
                            print(f"Calculated progress for {skill_name}: {progress_data['progress_percentage']}%")
                        
                        # Save the progress data
                        save_skill_progress(user_id, skill_name, progress_data)
                    except Exception as e:
                        print(f"Error saving progress for skill {skill_name}: {str(e)}")
            
            # Save user skills if they exist
            if "user_context" in save_vars and "skills" in save_vars["user_context"]:
                skills = save_vars["user_context"]["skills"]
                successful_skills = []
                failed_skills = []
                
                for skill in skills:
                    try:
                        # If it's just a string, convert to a dict
                        if isinstance(skill, str):
                            skill_data = {"name": skill, "category": "general"}
                        else:
                            skill_data = skill
                        
                        # Add proficiency information if available
                        if "skill_progress" in save_vars:
                            skill_name = skill_data.get("name", "")
                            if skill_name in save_vars["skill_progress"]:
                                skill_data["proficiency"] = save_vars["skill_progress"][skill_name].get("proficiency", 0)
                                skill_data["in_progress"] = save_vars["skill_progress"][skill_name].get("in_progress", False)
                        
                        # Save each skill
                        result = self.save_user_skill(user_id, skill_data)
                        if result:
                            successful_skills.append(skill_data.get("name", ""))
                        else:
                            failed_skills.append(skill_data.get("name", ""))
                    except Exception as e:
                        # Log the error but continue with other skills
                        print(f"Error saving skill {skill}: {str(e)}")
                        failed_skills.append(skill if isinstance(skill, str) else skill.get("name", "unknown"))
                
                if successful_skills:
                    print(f"Successfully saved {len(successful_skills)} skills: {', '.join(successful_skills)}")
                if failed_skills:
                    print(f"Failed to save {len(failed_skills)} skills: {', '.join(failed_skills)}")
            
            # Save skill analysis results if available
            if "skill_analysis_results" in session_state and session_state["skill_analysis_results"]:
                try:
                    print("Saving skill analysis results")
                    save_skill_analysis(user_id, session_state["skill_analysis_results"])
                except Exception as e:
                    print(f"Error saving skill analysis: {str(e)}")
            
            success = self.save_user_data(save_vars, user_id)
            if success:
                print(f"Successfully saved session state for user {user_id}")
            else:
                print(f"Failed to save session state for user {user_id}")
            
            return success
        except Exception as e:
            print(f"Error saving session state: {str(e)}")
            traceback.print_exc()
            return False
    
    def load_session_state(self, user_id: str = None) -> Dict[str, Any]:
        """Load session state from saved data"""
        session_state = self.load_user_data(user_id)
        
        # If the user is authenticated, load learning paths, career paths, and skills
        if user_id and user_id != self.default_user_id:
            print(f"Loading additional data for user {user_id}")
            
            # Load learning paths
            learning_paths = self.get_user_learning_paths(user_id)
            if learning_paths:
                print(f"Found {len(learning_paths)} learning paths for user {user_id}")
                session_state["learning_paths"] = learning_paths
                # Set current learning path to the most recently updated one
                sorted_paths = sorted(learning_paths, key=lambda x: x.get("updated_at", ""), reverse=True)
                if sorted_paths:
                    session_state["current_learning_path"] = sorted_paths[0]
                    print(f"Set current learning path to: {sorted_paths[0].get('skill_name', 'Unnamed Path')}")
            
            # Load career paths
            career_paths = self.get_user_career_paths(user_id)
            if career_paths:
                print(f"Found {len(career_paths)} career paths for user {user_id}")
                session_state["career_paths"] = career_paths
                # Set career path to the most recently updated one
                sorted_paths = sorted(career_paths, key=lambda x: x.get("updated_at", ""), reverse=True)
                if sorted_paths:
                    session_state["career_path"] = sorted_paths[0]
            
            # Load skill progress data
            try:
                from utils.supabase_client import get_user_skill_progress
                skill_progress_data = get_user_skill_progress(user_id)
                if skill_progress_data:
                    print(f"Found skill progress data for {len(skill_progress_data)} skills for user {user_id}")
                    # Create skill_progress dictionary if it doesn't exist
                    if "skill_progress" not in session_state:
                        session_state["skill_progress"] = {}
                    
                    # Update with data from database
                    for skill_name, progress_data in skill_progress_data.items():
                        # Merge with existing progress data if any
                        if skill_name in session_state["skill_progress"]:
                            print(f"Merging progress data for {skill_name}")
                            existing_data = session_state["skill_progress"][skill_name]
                            # Update with new data, preserving any existing fields not in the new data
                            for key, value in progress_data.items():
                                existing_data[key] = value
                        else:
                            print(f"Adding new progress data for {skill_name}")
                            session_state["skill_progress"][skill_name] = progress_data
                            
                            # Add to user skills list if not already there
                            if "user_context" not in session_state:
                                session_state["user_context"] = {}
                            if "skills" not in session_state["user_context"]:
                                session_state["user_context"]["skills"] = []
                            if skill_name not in session_state["user_context"]["skills"]:
                                session_state["user_context"]["skills"].append(skill_name)
                    
                    # Ensure all skill progress entries have required fields
                    for skill_name, progress_data in session_state["skill_progress"].items():
                        # Check for required fields and set defaults if missing
                        if "current_level" not in progress_data:
                            progress_data["current_level"] = progress_data.get("skill_level", "beginner")
                            print(f"Added missing current_level field for {skill_name}")
                        
                        if "target_level" not in progress_data:
                            progress_data["target_level"] = "advanced"
                            print(f"Added missing target_level field for {skill_name}")
                        
                        if "start_date" not in progress_data:
                            from datetime import datetime
                            progress_data["start_date"] = datetime.now().strftime("%Y-%m-%d")
                            print(f"Added missing start_date field for {skill_name}")
                        
                        if "learning_path" not in progress_data:
                            # Create minimal learning path structure
                            progress_data["learning_path"] = {
                                "objectives": [],
                                "resources": [],
                                "exercises": []
                            }
                            print(f"Added missing learning_path structure for {skill_name}")
                        
                        if "progress_percentage" not in progress_data:
                            progress_data["progress_percentage"] = 0
                            print(f"Added missing progress_percentage field for {skill_name}")
                    
                    # Update current_learning_path with the latest progress data if needed
                    if "current_learning_path" in session_state and session_state["current_learning_path"]:
                        current_path = session_state["current_learning_path"]
                        skill_name = current_path.get("skill_name", current_path.get("title", ""))
                        if skill_name in session_state["skill_progress"]:
                            progress_data = session_state["skill_progress"][skill_name]
                            progress_pct = progress_data.get("progress_percentage", 0)
                            
                            # Update progress field
                            if "progress" not in current_path:
                                current_path["progress"] = {}
                            current_path["progress"]["completed"] = progress_pct
                            current_path["progress"]["total"] = 100
                            print(f"Updated current_learning_path progress to {progress_pct}% from skill_progress data")
            except Exception as e:
                print(f"Error loading skill progress data: {str(e)}")
            
            # Load user skills
            skills = self.get_user_skills(user_id)
            if skills:
                print(f"Found {len(skills)} skills for user {user_id}")
                # Update user_context skills with the full skill objects
                if "user_context" not in session_state:
                    session_state["user_context"] = {}
                
                # Create skill_progress dictionary
                if "skill_progress" not in session_state:
                    session_state["skill_progress"] = {}
                
                # Update user skills with data from database
                skill_names = []
                for skill in skills:
                    skill_name = skill.get("name", "")
                    if skill_name:
                        skill_names.append(skill_name)
                        # Only add if not already loaded from skill_progress
                        if skill_name not in session_state["skill_progress"]:
                            session_state["skill_progress"][skill_name] = {
                                "proficiency": skill.get("proficiency", 0),
                                "in_progress": skill.get("in_progress", False),
                                "learning_resources": skill.get("learning_resources", [])
                            }
                
                # Only update skills if we found some in the database and they're not already in the list
                if skill_names:
                    if "skills" not in session_state["user_context"]:
                        session_state["user_context"]["skills"] = []
                    
                    # Add any missing skills
                    for skill_name in skill_names:
                        if skill_name not in session_state["user_context"]["skills"]:
                            session_state["user_context"]["skills"].append(skill_name)
            
            # Load skill analysis results
            try:
                from utils.supabase_client import get_user_skill_analyses
                skill_analyses = get_user_skill_analyses(user_id)
                if skill_analyses:
                    print(f"Found {len(skill_analyses)} skill analyses for user {user_id}")
                    # Store the most recent skill analysis
                    if skill_analyses:
                        # Sort by timestamp if available
                        sorted_analyses = sorted(
                            skill_analyses, 
                            key=lambda x: x.get("timestamp", ""), 
                            reverse=True
                        )
                        session_state["skill_analysis_results"] = sorted_analyses[0]
                        print(f"Set skill_analysis_results to most recent analysis")
            except Exception as e:
                print(f"Error loading skill analyses: {str(e)}")
        
        return session_state
    
    def _sanitize_session_data(self, session_data):
        """
        Create a sanitized copy of session data suitable for persistence.
        Removes large objects and non-serializable items.
        """
        try:
            # Create a copy to avoid modifying the original
            sanitized = {}
            
            # Keys to exclude from serialization
            exclude_keys = ['resume_file', '_uploaded_files']
            
            # Copy serializable items
            for key, value in session_data.items():
                # Skip excluded keys and None values
                if key in exclude_keys or value is None:
                    continue
                    
                try:
                    # Test if JSON serializable
                    json.dumps(value)
                    sanitized[key] = value
                except (TypeError, OverflowError):
                    # If not serializable, convert to string representation or skip
                    if isinstance(value, (list, dict)):
                        # For collections, try to save what we can
                        if isinstance(value, list):
                            sanitized[key] = [str(item) for item in value if self._is_simple_type(item)]
                        else:  # dict
                            sanitized[key] = {
                                str(k): str(v) for k, v in value.items() 
                                if self._is_simple_type(k) and self._is_simple_type(v)
                            }
                    else:
                        # Skip complex objects
                        print(f"Skipping non-serializable key: {key}")
            
            return sanitized
        except Exception as e:
            print(f"Error sanitizing session data: {str(e)}")
            traceback.print_exc()
            return {}
    
    def _is_simple_type(self, value):
        """Check if value is a simple type that can be easily converted to string"""
        return isinstance(value, (str, int, float, bool, type(None)))
    
    def save_learning_path(self, user_id: str, learning_path: Dict[str, Any]) -> bool:
        """Save a learning path to Supabase"""
        try:
            if self.use_supabase:
                result = save_learning_path(user_id, learning_path)
                return result is not None
            else:
                # Fallback to file storage if Supabase is not enabled
                file_path = os.path.join(self.data_dir, f"learning_path_{user_id}_{learning_path.get('id', str(uuid.uuid4()))}.json")
                with open(file_path, "w") as f:
                    json.dump(learning_path, f, indent=2)
                return True
        except Exception as e:
            print(f"Error saving learning path: {str(e)}")
            traceback.print_exc()
            return False
    
    def get_user_learning_paths(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all learning paths for a user"""
        try:
            if self.use_supabase:
                return get_user_learning_paths(user_id)
            else:
                # Fallback to file storage if Supabase is not enabled
                learning_paths = []
                prefix = f"learning_path_{user_id}_"
                for filename in os.listdir(self.data_dir):
                    if filename.startswith(prefix) and filename.endswith(".json"):
                        file_path = os.path.join(self.data_dir, filename)
                        with open(file_path, "r") as f:
                            learning_paths.append(json.load(f))
                return learning_paths
        except Exception as e:
            print(f"Error getting learning paths: {str(e)}")
            traceback.print_exc()
            return []
    
    def update_learning_path_progress(self, path_id: str, progress_data: Dict[str, Any]) -> bool:
        """Update the progress of a learning path"""
        try:
            if self.use_supabase:
                result = update_learning_path_progress(path_id, progress_data)
                return result is not None
            else:
                # This would require finding the specific file and updating it
                # For simplicity, we'll assume Supabase is enabled
                print("Learning path progress updates require Supabase")
                return False
        except Exception as e:
            print(f"Error updating learning path progress: {str(e)}")
            traceback.print_exc()
            return False
    
    def save_career_path(self, user_id: str, career_path: Dict[str, Any]) -> bool:
        """Save a career path to Supabase"""
        try:
            if self.use_supabase:
                result = save_career_path(user_id, career_path)
                return result is not None
            else:
                # Fallback to file storage if Supabase is not enabled
                file_path = os.path.join(self.data_dir, f"career_path_{user_id}_{career_path.get('id', str(uuid.uuid4()))}.json")
                with open(file_path, "w") as f:
                    json.dump(career_path, f, indent=2)
                return True
        except Exception as e:
            print(f"Error saving career path: {str(e)}")
            traceback.print_exc()
            return False
    
    def get_user_career_paths(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all career paths for a user"""
        try:
            if self.use_supabase:
                return get_user_career_paths(user_id)
            else:
                # Fallback to file storage if Supabase is not enabled
                career_paths = []
                prefix = f"career_path_{user_id}_"
                for filename in os.listdir(self.data_dir):
                    if filename.startswith(prefix) and filename.endswith(".json"):
                        file_path = os.path.join(self.data_dir, filename)
                        with open(file_path, "r") as f:
                            career_paths.append(json.load(f))
                return career_paths
        except Exception as e:
            print(f"Error getting career paths: {str(e)}")
            traceback.print_exc()
            return []
    
    def update_career_path_progress(self, path_id: str, progress_data: Dict[str, Any], current_step: int = None) -> bool:
        """Update the progress of a career path"""
        try:
            if self.use_supabase:
                result = update_career_path_progress(path_id, progress_data, current_step)
                return result is not None
            else:
                # This would require finding the specific file and updating it
                # For simplicity, we'll assume Supabase is enabled
                print("Career path progress updates require Supabase")
                return False
        except Exception as e:
            print(f"Error updating career path progress: {str(e)}")
            traceback.print_exc()
            return False
    
    def save_user_skill(self, user_id: str, skill_data: Dict[str, Any]) -> bool:
        """Save a user skill to Supabase"""
        try:
            if self.use_supabase:
                result = save_user_skill(user_id, skill_data)
                return result is not None
            else:
                # Fallback to file storage if Supabase is not enabled
                skill_name = skill_data.get("name", "unknown_skill")
                file_path = os.path.join(self.data_dir, f"skill_{user_id}_{skill_name}.json")
                with open(file_path, "w") as f:
                    json.dump(skill_data, f, indent=2)
                return True
        except Exception as e:
            print(f"Error saving user skill: {str(e)}")
            traceback.print_exc()
            return False
    
    def get_user_skills(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all skills for a user"""
        try:
            if self.use_supabase:
                return get_user_skills(user_id)
            else:
                # Fallback to file storage if Supabase is not enabled
                skills = []
                prefix = f"skill_{user_id}_"
                for filename in os.listdir(self.data_dir):
                    if filename.startswith(prefix) and filename.endswith(".json"):
                        file_path = os.path.join(self.data_dir, filename)
                        with open(file_path, "r") as f:
                            skills.append(json.load(f))
                return skills
        except Exception as e:
            print(f"Error getting user skills: {str(e)}")
            traceback.print_exc()
            return []
    
    def update_user_skill(self, user_id: str, skill_name: str, update_data: Dict[str, Any]) -> bool:
        """Update a specific skill for a user"""
        try:
            if self.use_supabase:
                result = update_user_skill(user_id, skill_name, update_data)
                return result is not None
            else:
                # This would require finding the specific file and updating it
                # For simplicity, we'll assume Supabase is enabled
                print("Skill updates require Supabase")
                return False
        except Exception as e:
            print(f"Error updating user skill: {str(e)}")
            traceback.print_exc()
            return False
    
    def delete_user_skill(self, user_id: str, skill_name: str) -> bool:
        """Delete a specific skill for a user"""
        try:
            if self.use_supabase:
                result = delete_user_skill(user_id, skill_name)
                return result is not None
            else:
                # Fallback to file storage if Supabase is not enabled
                file_path = os.path.join(self.data_dir, f"skill_{user_id}_{skill_name}.json")
                if os.path.exists(file_path):
                    os.remove(file_path)
                return True
        except Exception as e:
            print(f"Error deleting user skill: {str(e)}")
            traceback.print_exc()
            return False 