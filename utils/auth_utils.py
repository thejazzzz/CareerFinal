import streamlit as st
import time
from typing import Optional

def is_authenticated() -> bool:
    """Check if a user is authenticated"""
    return st.session_state.get("authenticated", False)

def get_authenticated_user_id() -> Optional[str]:
    """Get the ID of the authenticated user"""
    if is_authenticated():
        return st.session_state.get("user_id")
    return None

def login_user(user_id: str, user_email: str = None):
    """Set user as authenticated in session state and load user data"""
    st.session_state.authenticated = True
    st.session_state.user_id = user_id
    if user_email:
        st.session_state.user_email = user_email
    st.session_state.login_time = time.time()
    
    # Load user data from database after login
    print(f"Loading data for authenticated user: {user_id}")
    # Import DataPersistence locally to avoid circular imports
    from utils.data_persistence import DataPersistence
    data_persistence = DataPersistence()
    user_data = data_persistence.load_session_state(user_id)
    
    if user_data:
        print(f"Found existing user data for {user_id}")
        
        # Update session state with the loaded data
        for key, value in user_data.items():
            if key not in ['authenticated', 'user_id', 'user_email', 'login_time']:
                st.session_state[key] = value
        
        # Ensure critical structures exist
        if "user_context" not in st.session_state:
            st.session_state.user_context = {"user_id": user_id}
        elif "user_id" not in st.session_state.user_context:
            st.session_state.user_context["user_id"] = user_id
            
        # Load learning paths, career paths and skills
        learning_paths = data_persistence.get_user_learning_paths(user_id)
        if learning_paths:
            st.session_state["learning_paths"] = learning_paths
            # Set current learning path to the most recently updated one
            sorted_paths = sorted(learning_paths, key=lambda x: x.get("updated_at", ""), reverse=True)
            if sorted_paths:
                st.session_state["current_learning_path"] = sorted_paths[0]
                print(f"Loaded current learning path: {sorted_paths[0].get('skill_name', 'Unknown')}")
        
        # Load skill analysis data
        from utils.supabase_client import get_user_skill_analyses
        skill_analyses = get_user_skill_analyses(user_id)
        if skill_analyses:
            print(f"Loaded {len(skill_analyses)} skill analyses for user")
            st.session_state["skill_analysis_results"] = skill_analyses[0] if skill_analyses else None
    else:
        print(f"No existing data found for user {user_id}")

def logout_user():
    """Remove authentication data from session state"""
    st.session_state.authenticated = False
    if "user_id" in st.session_state:
        del st.session_state.user_id
    if "user_email" in st.session_state:
        del st.session_state.user_email
    if "login_time" in st.session_state:
        del st.session_state.login_time 