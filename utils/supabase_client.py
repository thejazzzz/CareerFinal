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

# Initialize Supabase client
@st.cache_resource
def get_supabase_client():
    """
    Initialize and return a Supabase client.
    Uses caching to avoid creating multiple clients.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY in your .env file."
        )
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"Successfully connected to Supabase at {SUPABASE_URL}")
        return client
    except Exception as e:
        print(f"Error connecting to Supabase: {str(e)}")
        traceback.print_exc()
        raise

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
        print(f"Error loading user data from Supabase: {str(e)}")
        traceback.print_exc()
        return None

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
        
        data_to_save = {
            "id": path_id,
            "user_id": user_id,
            "path_data": learning_path  # Supabase handles JSONB conversion
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
        
        # Extract path_data from each record
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
        
        # Get the current learning path
        response = supabase.table('learning_paths').select("*").eq("id", learning_path_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise ValueError(f"Learning path with ID {learning_path_id} not found")
        
        # Get the path_data
        path_data = response.data[0].get("path_data", {})
        if isinstance(path_data, str):
            path_data = json.loads(path_data)
        
        # Update the progress field
        if "progress" not in path_data:
            path_data["progress"] = {}
        
        path_data["progress"].update(progress_data)
        
        # Save the updated path_data
        update_data = {
            "path_data": path_data
        }
        
        response = supabase.table('learning_paths').update(update_data).eq("id", learning_path_id).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Supabase error: {response.error}")
            return None
        
        return response.data
    except Exception as e:
        print(f"Error updating learning path progress: {str(e)}")
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