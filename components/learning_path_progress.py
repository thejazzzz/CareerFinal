import streamlit as st

def display_learning_path_progress():
    """Display the current learning path progress in the profile."""
    st.markdown("<h3 style='color: white; margin-bottom: 15px;'>Current Learning Path</h3>", unsafe_allow_html=True)
    
    # Get the current learning path from session state
    current_path = st.session_state.get('current_learning_path', None)
    
    # Debug info to help diagnose issues
    if current_path:
        # Detailed debug output to understand the learning path structure
        print(f"DEBUG [learning_path_progress]: Displaying learning path data: {current_path}")
        
        # First try to get progress from skill_progress if it exists
        skill_name = current_path.get('title', '') or current_path.get('skill_name', '')
        skill_progress_data = None
        
        # Look for exact match and fuzzy match in skill_progress
        if 'skill_progress' in st.session_state:
            # Try exact match first
            if skill_name in st.session_state.skill_progress:
                skill_progress_data = st.session_state.skill_progress[skill_name]
                print(f"DEBUG [learning_path_progress]: Found exact skill match in skill_progress: {skill_name}")
            else:
                # Try fuzzy match looking for partial name matches
                for progress_skill_name, progress_data in st.session_state.skill_progress.items():
                    if (skill_name and progress_skill_name and 
                        (skill_name.lower() in progress_skill_name.lower() or 
                         progress_skill_name.lower() in skill_name.lower())):
                        skill_progress_data = progress_data
                        print(f"DEBUG [learning_path_progress]: Found fuzzy skill match: {progress_skill_name}")
                        break
        
        # Get progress percentage from skill_progress if available
        if skill_progress_data:
            progress_pct = skill_progress_data.get('progress_percentage', 0)
            print(f"DEBUG [learning_path_progress]: Using progress from skill_progress: {progress_pct}%")
            
            # Ensure progress field exists and contains correct data
            if 'progress' not in current_path or not current_path['progress']:
                print(f"INFO [learning_path_progress]: Adding progress field from skill_progress: {progress_pct}%")
                current_path['progress'] = {
                    'completed': progress_pct,
                    'total': 100
                }
            elif isinstance(current_path['progress'], dict):
                # Update the progress value
                current_path['progress']['completed'] = progress_pct
                print(f"INFO [learning_path_progress]: Updated progress field to: {progress_pct}%")
            else:
                print(f"WARNING [learning_path_progress]: Progress field is not a dict: {type(current_path['progress'])}")
                current_path['progress'] = {
                    'completed': progress_pct,
                    'total': 100
                }
        
        # Check that all expected fields exist
        if 'title' not in current_path:
            print("WARNING [learning_path_progress]: current_learning_path missing 'title' field")
            current_path['title'] = current_path.get('skill_name', 'Unknown Path')
        
        # Ensure progress field exists and is properly structured
        if 'progress' not in current_path or not current_path['progress']:
            print("WARNING [learning_path_progress]: Setting default progress field")
            current_path['progress'] = {'completed': 0, 'total': 100}
        elif not isinstance(current_path['progress'], dict):
            print(f"WARNING [learning_path_progress]: progress is not a dictionary: {type(current_path['progress'])} - {current_path['progress']}")
            current_path['progress'] = {'completed': 0, 'total': 100}
        elif 'completed' not in current_path['progress']:
            print(f"WARNING [learning_path_progress]: current_learning_path progress missing 'completed' field")
            print(f"Available keys in progress: {current_path['progress'].keys()}")
            current_path['progress']['completed'] = 0
        
        # Extract progress percentage, ensuring it's a number
        progress_data = current_path.get('progress', {})
        if isinstance(progress_data, dict):
            progress_percent = progress_data.get('completed', 0)
            if not isinstance(progress_percent, (int, float)):
                print(f"WARNING [learning_path_progress]: progress percentage is not a number: {type(progress_percent)} - {progress_percent}")
                try:
                    progress_percent = int(progress_percent)
                except (ValueError, TypeError):
                    print(f"ERROR [learning_path_progress]: Could not convert progress to number: {progress_percent}")
                    progress_percent = 0
        else:
            print(f"WARNING [learning_path_progress]: progress data is not a dictionary: {type(progress_data)} - {progress_data}")
            progress_percent = 0
        
        # Always save the session state to ensure progress is persisted
        try:
            from utils.data_persistence import DataPersistence
            data_persistence = DataPersistence()
            save_success = data_persistence.save_session_state(dict(st.session_state))
            if save_success:
                print(f"INFO [learning_path_progress]: Successfully saved session with progress {progress_percent}%")
            else:
                print(f"WARNING [learning_path_progress]: Failed to save session state")
        except Exception as e:
            print(f"ERROR [learning_path_progress]: Error saving session: {str(e)}")
        
        # Print debug info
        title = current_path.get('title', 'Unnamed Path')
        print(f"INFO [learning_path_progress]: Displaying learning path: {title} - Progress: {progress_percent}%")
        
        # Create a container for the learning path progress
        st.markdown("""
        <div style="
            background-color: #2d3748;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid #4a5568;
        ">
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            title = current_path.get('title', 'Unnamed Path')
            st.markdown(f"<p style='color: white; font-weight: bold; margin-bottom: 5px;'>{title}</p>", unsafe_allow_html=True)
            # Ensure progress value is between 0 and 1
            progress_val = min(1.0, max(0.0, progress_percent / 100))
            st.progress(progress_val)
        
        with col2:
            st.markdown(f"<p style='color: white; text-align: center; font-size: 24px; font-weight: bold;'>{progress_percent}%</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Button to refresh progress
        if st.button("Refresh Progress"):
            st.experimental_rerun()
    else:
        # Print debug info
        print("INFO [learning_path_progress]: No current_learning_path found in session state")
        
        st.markdown("""
        <div style="
            background-color: #2d3748;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid #4a5568;
        ">
            <p style='color: #e2e8f0;'>No active learning path. Create one in the Skills Development section to start tracking your progress!</p>
        </div>
        """, unsafe_allow_html=True)
