import os
from supabase import create_client, Client
from dotenv import load_dotenv
import streamlit as st
import json
import traceback

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

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
        supabase = get_supabase_client()
        
        # Convert any non-serializable data to a JSON string
        user_data_json = json.dumps(user_data, default=str)
        
        # Prepare data for Supabase with the user_data column
        data_to_save = {
            "id": user_id,
            "user_data": user_data_json
        }
        
        print(f"Attempting to save data for user {user_id} to Supabase")
        
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
        supabase = get_supabase_client()
        
        print(f"Attempting to load data for user {user_id} from Supabase")
        
        response = supabase.table('users').select("*").eq("id", user_id).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Supabase error: {response.error}")
            return None
        
        if response.data and len(response.data) > 0:
            print(f"Found data for user {user_id} in Supabase")
            # Parse the JSON data from the user_data column
            try:
                user_data = json.loads(response.data[0].get("user_data", "{}"))
                return user_data
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON data for user {user_id}: {str(e)}")
                return {}
        
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
        
        # Ensure learning_path has an ID and user_id
        if "id" not in learning_path:
            raise ValueError("Learning path must have an 'id' field")
        
        data_to_save = {
            "user_id": user_id,
            **learning_path
        }
        
        # Convert any non-serializable data
        data_to_save = json.loads(json.dumps(data_to_save, default=str))
        
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
    supabase = get_supabase_client()
    
    response = supabase.table('learning_paths').select("*").eq("user_id", user_id).execute()
    
    return response.data if response.data else []

def update_learning_path_progress(learning_path_id, progress_data):
    """
    Update the progress of a learning path in Supabase.
    
    Args:
        learning_path_id (str): The unique identifier for the learning path
        progress_data (dict): The progress data to update
    
    Returns:
        dict: The response from Supabase
    """
    supabase = get_supabase_client()
    
    # Get the current learning path
    response = supabase.table('learning_paths').select("*").eq("id", learning_path_id).execute()
    
    if not response.data or len(response.data) == 0:
        raise ValueError(f"Learning path with ID {learning_path_id} not found")
    
    learning_path = response.data[0]
    
    # Update the progress field
    learning_path["progress"] = {
        **(learning_path.get("progress", {})),
        **progress_data
    }
    
    # Save the updated learning path
    update_response = supabase.table('learning_paths').update(learning_path).eq("id", learning_path_id).execute()
    
    return update_response.data

# Skill analysis operations
def save_skill_analysis(user_id, analysis_data):
    """
    Save skill analysis results to Supabase.
    
    Args:
        user_id (str): The unique identifier for the user
        analysis_data (dict): The analysis data to save
    
    Returns:
        dict: The response from Supabase
    """
    supabase = get_supabase_client()
    
    data_to_save = {
        "user_id": user_id,
        "created_at": analysis_data.get("created_at", None),
        "target_role": analysis_data.get("target_role", ""),
        "structured_data": analysis_data.get("structured_data", {}),
        "raw_analysis": analysis_data.get("raw_analysis", "")
    }
    
    response = supabase.table('skill_analyses').insert(data_to_save).execute()
    
    return response.data

def get_user_skill_analyses(user_id, limit=5):
    """
    Get skill analyses for a user from Supabase.
    
    Args:
        user_id (str): The unique identifier for the user
        limit (int): The maximum number of analyses to return
    
    Returns:
        list: The skill analyses for the user
    """
    supabase = get_supabase_client()
    
    response = supabase.table('skill_analyses').select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
    
    return response.data if response.data else [] 