import os
import sys
import json
import traceback
import uuid
import re
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# UUID validation regex pattern
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)

def is_valid_uuid(val):
    """Check if a string is a valid UUID"""
    if not val:
        return False
    return bool(UUID_PATTERN.match(val))

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client():
    """Returns the Supabase client instance"""
    return supabase

# Authentication functions
def sign_up(email, password, metadata=None):
    """
    Register a new user with email and password.
    
    Args:
        email (str): User's email address
        password (str): User's password
        metadata (dict, optional): Additional user metadata
    
    Returns:
        tuple: (user, error) where user is the user data if successful, otherwise None,
               and error is None if successful, otherwise the error message
    """
    try:
        supabase = get_supabase_client()
        if metadata is None:
            metadata = {}
        
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": metadata,
                "email_confirmation": False, # Disable email confirmation
                "auto_confirm": True  # Auto confirm the user's email
            }
        })
        
        # Extract user data if available
        user = response.user if hasattr(response, 'user') else None
        
        # Extract error if available
        error = response.error if hasattr(response, 'error') else None
        
        if user:
            print(f"Successfully signed up user with email: {email}")
            return user, None
        else:
            print(f"Failed to sign up user with email: {email}")
            return None, error or "Unknown error during sign up"
        
    except Exception as e:
        print(f"Error during sign up: {str(e)}")
        traceback.print_exc()
        return None, str(e)

def sign_in(email, password):
    """
    Sign in a user with email and password.
    
    Args:
        email (str): User's email address
        password (str): User's password
    
    Returns:
        tuple: (session, error) where session is the session data if successful, otherwise None,
               and error is None if successful, otherwise the error message
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        # Extract session data if available
        session = response.session if hasattr(response, 'session') else None
        
        # Extract error if available
        error = response.error if hasattr(response, 'error') else None
        
        if session:
            print(f"Successfully signed in user with email: {email}")
            # Store user session in Streamlit session state
            if "user" not in st.session_state:
                st.session_state.user = response.user
            if "auth_session" not in st.session_state:
                st.session_state.auth_session = session
            
            return session, None
        else:
            print(f"Failed to sign in user with email: {email}")
            return None, error or "Unknown error during sign in"
        
    except Exception as e:
        print(f"Error during sign in: {str(e)}")
        traceback.print_exc()
        return None, str(e)

def sign_out():
    """
    Sign out the currently signed in user.
    
    Returns:
        bool: True if sign out was successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        supabase.auth.sign_out()
        
        # Clear user session from Streamlit session state
        if "user" in st.session_state:
            del st.session_state.user
        if "auth_session" in st.session_state:
            del st.session_state.auth_session
        
        print("Successfully signed out user")
        return True
        
    except Exception as e:
        print(f"Error during sign out: {str(e)}")
        traceback.print_exc()
        return False

def reset_password(email):
    """
    Send a password reset email to the user.
    
    Args:
        email (str): User's email address
    
    Returns:
        tuple: (success, error) where success is True if the email was sent, otherwise False,
               and error is None if successful, otherwise the error message
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.auth.reset_password_for_email(email)
        
        # Extract error if available
        error = response.error if hasattr(response, 'error') else None
        
        if not error:
            print(f"Successfully sent password reset email to: {email}")
            return True, None
        else:
            print(f"Failed to send password reset email to: {email}")
            return False, error
        
    except Exception as e:
        print(f"Error sending password reset email: {str(e)}")
        traceback.print_exc()
        return False, str(e)

def get_current_user():
    """
    Get the currently signed in user.
    
    Returns:
        dict: The current user data or None if no user is signed in
    """
    try:
        # Check if user exists in session state
        if "user" in st.session_state:
            return st.session_state.user
        
        supabase = get_supabase_client()
        
        # Get current user session
        response = supabase.auth.get_user()
        
        # Extract user data if available
        user = response.user if hasattr(response, 'user') else None
        
        if user:
            print(f"Current user: {user.email}")
            # Store user in session state
            st.session_state.user = user
            return user
        else:
            print("No current user found")
            return None
        
    except Exception as e:
        # If the error is about invalid JWT, consider the user not signed in
        if "invalid JWT" in str(e):
            return None
        print(f"Error getting current user: {str(e)}")
        traceback.print_exc()
        return None

def is_authenticated():
    """
    Check if a user is currently authenticated.
    
    Returns:
        bool: True if a user is authenticated, False otherwise
    """
    return get_current_user() is not None

# User data operations
def save_user_data(user_id, user_data):
    """
    Save user data to Supabase.
    
    Args:
        user_id (str): The unique identifier for the user
        user_data (dict): The user data to save
    
    Returns:
        dict: The response from Supabase
    """
    try:
        # Validate UUID format
        if not is_valid_uuid(user_id):
            print(f"Invalid UUID format: {user_id}. Generating a new UUID.")
            user_id = str(uuid.uuid4())
            # If user_context exists in user_data, update the user_id
            if "user_context" in user_data:
                user_data["user_context"]["user_id"] = user_id
        
        supabase = get_supabase_client()
        
        # Prepare data for Supabase with the user_data column
        # Note: Supabase automatically handles JSON serialization for JSONB columns
        data_to_save = {
            "id": user_id,
            "user_data": user_data  # No need to convert to JSON string, Supabase handles this
        }
        
        print(f"Attempting to save data for user {user_id} to Supabase")
        print(f"Data structure being saved: {list(user_data.keys())}")
        
        # Use upsert to insert or update
        response = supabase.table('users').upsert(data_to_save).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Supabase error: {response.error}")
            return None
        
        print(f"Successfully saved data for user {user_id} to Supabase")
        return response.data
    except Exception as e:
        print(f"Error saving user data to Supabase: {str(e)}")
        traceback.print_exc()
        raise

def load_user_data(user_id):
    """
    Load user data from Supabase.
    
    Args:
        user_id (str): The unique identifier for the user
    
    Returns:
        dict: The user data or None if not found
    """
    try:
        # Validate UUID format
        if not is_valid_uuid(user_id):
            print(f"Invalid UUID format: {user_id}. Cannot load from Supabase.")
            return None
        
        supabase = get_supabase_client()
        
        print(f"Attempting to load data for user {user_id} from Supabase")
        
        try:
            response = supabase.table('users').select("*").eq("id", user_id).execute()
            
            if hasattr(response, 'error') and response.error:
                print(f"Supabase error: {response.error}")
                return None
            
            if response.data and len(response.data) > 0:
                print(f"Found data for user {user_id} in Supabase")
                # Get the user_data column which should already be parsed from JSONB
                user_data = response.data[0].get("user_data", {})
                
                # If it's still a string for some reason, parse it
                if isinstance(user_data, str):
                    try:
                        user_data = json.loads(user_data)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON data for user {user_id}: {str(e)}")
                        return {}
                
                return user_data
            
            print(f"No data found for user {user_id} in Supabase")
            return None
        except Exception as e:
            print(f"Database error when loading user data from Supabase: {str(e)}")
            # Return an empty dict instead of None to prevent further errors
            return {}
    except Exception as e:
        print(f"Error loading user data from Supabase: {str(e)}")
        traceback.print_exc()
        return {}

def delete_user_data(user_id):
    """
    Delete user data from Supabase.
    
    Args:
        user_id (str): The unique identifier for the user
    
    Returns:
        dict: The response from Supabase
    """
    try:
        supabase = get_supabase_client()
        
        print(f"Attempting to delete data for user {user_id} from Supabase")
        
        response = supabase.table('users').delete().eq("id", user_id).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Supabase error: {response.error}")
            return None
        
        print(f"Successfully deleted data for user {user_id} from Supabase")
        return response.data
    except Exception as e:
        print(f"Error deleting user data from Supabase: {str(e)}")
        traceback.print_exc()
        return None

# Learning path operations
def save_learning_path(user_id, learning_path):
    """
    Save a learning path to Supabase.
    
    Args:
        user_id (str): The unique identifier for the user
        learning_path (dict): The learning path data to save
    
    Returns:
        dict: The response from Supabase
    """
    try:
        supabase = get_supabase_client()
        
        # Generate an ID if not present
        path_id = learning_path.get("id", str(uuid.uuid4()))
        
        # Extract progress information if available
        progress = learning_path.pop("progress", {}) if isinstance(learning_path, dict) else {}
        is_complete = learning_path.pop("is_complete", False) if isinstance(learning_path, dict) else False
        
        data_to_save = {
            "id": path_id,
            "user_id": user_id,
            "path_data": learning_path,  # Supabase handles JSONB conversion
            "progress": progress,
            "is_complete": is_complete
        }
        
        print(f"Attempting to save learning path for user {user_id} to Supabase")
        
        response = supabase.table('learning_paths').upsert(data_to_save).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Supabase error: {response.error}")
            return None
        
        print(f"Successfully saved learning path for user {user_id} to Supabase")
        return response.data
    except Exception as e:
        print(f"Error saving learning path to Supabase: {str(e)}")
        traceback.print_exc()
        return None

def get_user_learning_paths(user_id):
    """
    Get all learning paths for a user from Supabase.
    
    Args:
        user_id (str): The unique identifier for the user
    
    Returns:
        list: The learning paths for the user
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table('learning_paths').select("*").eq("user_id", user_id).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Supabase error: {response.error}")
            return []
        
        # Process paths to combine path_data with progress information
        paths = []
        for record in response.data:
            path_data = record.get("path_data", {})
            if path_data:
                # If it's a string, parse it
                if isinstance(path_data, str):
                    try:
                        path_data = json.loads(path_data)
                    except json.JSONDecodeError:
                        continue
                
                # Add progress information to path data
                path_data["progress"] = record.get("progress", {})
                path_data["is_complete"] = record.get("is_complete", False)
                path_data["id"] = record.get("id")
                path_data["created_at"] = record.get("created_at")
                path_data["updated_at"] = record.get("updated_at")
                
                paths.append(path_data)
        
        return paths
    except Exception as e:
        print(f"Error getting learning paths from Supabase: {str(e)}")
        traceback.print_exc()
        return []

def update_learning_path_progress(learning_path_id, progress_data):
    """
    Update the progress of a learning path in Supabase.
    
    Args:
        learning_path_id (str): The unique identifier for the learning path
        progress_data (dict): The progress data to update
    
    Returns:
        dict: The response from Supabase
    """
    try:
        supabase = get_supabase_client()
        
        # Check if path exists
        response = supabase.table('learning_paths').select("*").eq("id", learning_path_id).execute()
        
        if not response.data:
            print(f"Learning path {learning_path_id} not found")
            return None
        
        # Calculate if the path is complete based on progress
        is_complete = progress_data.get("is_complete", False)
        if not is_complete and "steps" in progress_data:
            # Check if all steps are complete
            steps = progress_data.get("steps", [])
            if steps and all(step.get("complete", False) for step in steps):
                is_complete = True
        
        # Prepare update data
        update_data = {
            "progress": progress_data,
            "is_complete": is_complete
        }
        
        # Update the learning path
        response = supabase.table('learning_paths').update(update_data).eq("id", learning_path_id).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Supabase error: {response.error}")
            return None
        
        print(f"Successfully updated progress for learning path {learning_path_id}")
        return response.data
    except Exception as e:
        print(f"Error updating learning path progress: {str(e)}")
        traceback.print_exc()
        return None

# Career path operations
def save_career_path(user_id, career_path):
    """
    Save a career path to Supabase.
    
    Args:
        user_id (str): The unique identifier for the user
        career_path (dict): The career path data to save
    
    Returns:
        dict: The response from Supabase
    """
    try:
        supabase = get_supabase_client()
        
        # Generate an ID if not present
        path_id = career_path.get("id", str(uuid.uuid4()))
        
        # Extract progress information if available
        progress = career_path.pop("progress", {}) if isinstance(career_path, dict) else {}
        current_step = career_path.pop("current_step", 0) if isinstance(career_path, dict) else 0
        is_complete = career_path.pop("is_complete", False) if isinstance(career_path, dict) else False
        
        data_to_save = {
            "id": path_id,
            "user_id": user_id,
            "path_data": career_path,  # Supabase handles JSONB conversion
            "progress": progress,
            "current_step": current_step,
            "is_complete": is_complete
        }
        
        print(f"Attempting to save career path for user {user_id} to Supabase")
        
        response = supabase.table('career_paths').upsert(data_to_save).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Supabase error: {response.error}")
            return None
        
        print(f"Successfully saved career path for user {user_id} to Supabase")
        return response.data
    except Exception as e:
        print(f"Error saving career path to Supabase: {str(e)}")
        traceback.print_exc()
        return None

def get_user_career_paths(user_id):
    """
    Get all career paths for a user from Supabase.
    
    Args:
        user_id (str): The unique identifier for the user
    
    Returns:
        list: The career paths for the user
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table('career_paths').select("*").eq("user_id", user_id).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Supabase error: {response.error}")
            return []
        
        # Process paths to combine path_data with progress information
        paths = []
        for record in response.data:
            path_data = record.get("path_data", {})
            if path_data:
                # If it's a string, parse it
                if isinstance(path_data, str):
                    try:
                        path_data = json.loads(path_data)
                    except json.JSONDecodeError:
                        continue
                
                # Add progress information to path data
                path_data["progress"] = record.get("progress", {})
                path_data["current_step"] = record.get("current_step", 0)
                path_data["is_complete"] = record.get("is_complete", False)
                path_data["id"] = record.get("id")
                path_data["created_at"] = record.get("created_at")
                path_data["updated_at"] = record.get("updated_at")
                
                paths.append(path_data)
        
        return paths
    except Exception as e:
        print(f"Error getting career paths from Supabase: {str(e)}")
        traceback.print_exc()
        return []

def update_career_path_progress(career_path_id, progress_data, current_step=None):
    """
    Update the progress of a career path in Supabase.
    
    Args:
        career_path_id (str): The unique identifier for the career path
        progress_data (dict): The progress data to update
        current_step (int, optional): The current step in the career path
    
    Returns:
        dict: The response from Supabase
    """
    try:
        supabase = get_supabase_client()
        
        # Check if path exists
        response = supabase.table('career_paths').select("*").eq("id", career_path_id).execute()
        
        if not response.data:
            print(f"Career path {career_path_id} not found")
            return None
        
        path_data = response.data[0]
        
        # Determine current step if not provided
        if current_step is None:
            current_step = path_data.get("current_step", 0)
        
        # Calculate if the path is complete based on progress
        is_complete = progress_data.get("is_complete", False)
        
        # Prepare update data
        update_data = {
            "progress": progress_data,
            "current_step": current_step,
            "is_complete": is_complete
        }
        
        # Update the career path
        response = supabase.table('career_paths').update(update_data).eq("id", career_path_id).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Supabase error: {response.error}")
            return None
        
        print(f"Successfully updated progress for career path {career_path_id}")
        return response.data
    except Exception as e:
        print(f"Error updating career path progress: {str(e)}")
        traceback.print_exc()
        return None

# User skills operations
def save_user_skill(user_id, skill_data):
    """
    Save a user skill to Supabase.
    
    Args:
        user_id (str): The unique identifier for the user
        skill_data (dict): The skill data to save
        
    Returns:
        dict: The response from Supabase
    """
    try:
        supabase = get_supabase_client()
        
        # Generate an ID if not present
        skill_id = skill_data.get("id", str(uuid.uuid4()))
        
        # Extract skill information
        skill_name = skill_data.get("name", "")
        if not skill_name:
            print("Skill name is required")
            return None
        
        skill_category = skill_data.get("category", "")
        proficiency = skill_data.get("proficiency", 0)
        in_progress = skill_data.get("in_progress", False)
        learning_resources = skill_data.get("learning_resources", [])
        
        data_to_save = {
            "id": skill_id,
            "user_id": user_id,
            "skill_name": skill_name,
            "skill_category": skill_category,
            "proficiency": proficiency,
            "in_progress": in_progress,
            "learning_resources": learning_resources
        }
        
        print(f"Attempting to save skill '{skill_name}' for user {user_id} to Supabase")
        
        # Use upsert to handle the unique constraint on user_id and skill_name
        response = supabase.table('user_skills').upsert(data_to_save).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Supabase error: {response.error}")
            return None
        
        print(f"Successfully saved skill '{skill_name}' for user {user_id} to Supabase")
        return response.data
    except Exception as e:
        print(f"Error saving user skill to Supabase: {str(e)}")
        traceback.print_exc()
        return None

def get_user_skills(user_id):
    """
    Get all skills for a user from Supabase.
    
    Args:
        user_id (str): The unique identifier for the user
    
    Returns:
        list: The skills for the user
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table('user_skills').select("*").eq("user_id", user_id).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Supabase error: {response.error}")
            return []
        
        # Transform the data into a more usable format
        skills = []
        for record in response.data:
            skill = {
                "id": record.get("id"),
                "name": record.get("skill_name"),
                "category": record.get("skill_category"),
                "proficiency": record.get("proficiency", 0),
                "in_progress": record.get("in_progress", False),
                "learning_resources": record.get("learning_resources", []),
                "created_at": record.get("created_at"),
                "updated_at": record.get("updated_at")
            }
            skills.append(skill)
        
        return skills
    except Exception as e:
        print(f"Error getting user skills from Supabase: {str(e)}")
        traceback.print_exc()
        return []

def update_user_skill(user_id, skill_name, update_data):
    """
    Update a specific skill for a user in Supabase.
    
    Args:
        user_id (str): The unique identifier for the user
        skill_name (str): The name of the skill to update
        update_data (dict): The data to update
    
    Returns:
        dict: The response from Supabase
    """
    try:
        supabase = get_supabase_client()
        
        # Check if skill exists
        response = supabase.table('user_skills').select("*").eq("user_id", user_id).eq("skill_name", skill_name).execute()
        
        if not response.data:
            print(f"Skill '{skill_name}' not found for user {user_id}")
            return None
        
        # Update the skill
        response = supabase.table('user_skills').update(update_data).eq("user_id", user_id).eq("skill_name", skill_name).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Supabase error: {response.error}")
            return None
        
        print(f"Successfully updated skill '{skill_name}' for user {user_id}")
        return response.data
    except Exception as e:
        print(f"Error updating user skill in Supabase: {str(e)}")
        traceback.print_exc()
        return None

def delete_user_skill(user_id, skill_name):
    """
    Delete a specific skill for a user from Supabase.
    
    Args:
        user_id (str): The unique identifier for the user
        skill_name (str): The name of the skill to delete
    
    Returns:
        dict: The response from Supabase
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table('user_skills').delete().eq("user_id", user_id).eq("skill_name", skill_name).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Supabase error: {response.error}")
            return None
        
        print(f"Successfully deleted skill '{skill_name}' for user {user_id}")
        return response.data
    except Exception as e:
        print(f"Error deleting user skill from Supabase: {str(e)}")
        traceback.print_exc()
        return None

# Skill analysis operations
def save_skill_analysis(user_id, analysis_data):
    """
    Save a skill analysis to Supabase.
    
    Args:
        user_id (str): The unique identifier for the user
        analysis_data (dict): The skill analysis data to save
    
    Returns:
        dict: The response from Supabase
    """
    try:
        supabase = get_supabase_client()
        
        # Generate an ID if not present
        analysis_id = analysis_data.get("id", str(uuid.uuid4()))
        
        data_to_save = {
            "id": analysis_id,
            "user_id": user_id,
            "analysis_data": analysis_data  # Supabase handles JSONB conversion
        }
        
        print(f"Attempting to save skill analysis for user {user_id} to Supabase")
        
        response = supabase.table('skill_analyses').upsert(data_to_save).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Supabase error: {response.error}")
            return None
        
        print(f"Successfully saved skill analysis for user {user_id} to Supabase")
        return response.data
    except Exception as e:
        print(f"Error saving skill analysis to Supabase: {str(e)}")
        traceback.print_exc()
        return None

def get_user_skill_analyses(user_id):
    """
    Get all skill analyses for a user from Supabase.
    
    Args:
        user_id (str): The unique identifier for the user
    
    Returns:
        list: The skill analyses for the user
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table('skill_analyses').select("*").eq("user_id", user_id).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Supabase error: {response.error}")
            return []
        
        # Extract analysis_data from each record
        analyses = []
        for record in response.data:
            analysis_data = record.get("analysis_data", {})
            if analysis_data:
                # If it's a string, parse it
                if isinstance(analysis_data, str):
                    try:
                        analysis_data = json.loads(analysis_data)
                    except json.JSONDecodeError:
                        continue
                analyses.append(analysis_data)
        
        return analyses
    except Exception as e:
        print(f"Error getting skill analyses from Supabase: {str(e)}")
        traceback.print_exc()
        return [] 