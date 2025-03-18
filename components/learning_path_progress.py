import streamlit as st

def display_learning_path_progress():
    """Display the current learning path progress in the profile."""
    st.markdown("<h3 style='color: white;'>Current Learning Path</h3>", unsafe_allow_html=True)
    
    # Get the current learning path from session state
    current_path = st.session_state.get('current_learning_path', None)
    
    if current_path:
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
            st.markdown(f"<p style='color: white; font-weight: bold; margin-bottom: 5px;'>{current_path.get('title', 'Unnamed Path')}</p>", unsafe_allow_html=True)
            st.progress(current_path.get('progress', {}).get('completed', 0) / 100)
        
        with col2:
            progress_percent = current_path.get('progress', {}).get('completed', 0)
            st.markdown(f"<p style='color: white; text-align: center; font-size: 24px; font-weight: bold;'>{progress_percent}%</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
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
