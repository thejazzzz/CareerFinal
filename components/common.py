import streamlit as st
from components.styling import apply_custom_styling, custom_hero_section, feature_card

def initialize_page(title, subtitle=None, show_profile_warning=True):
    """
    Initialize a page with consistent styling and check for user profile completion.
    
    Args:
        title: Page title
        subtitle: Optional subtitle for the hero section
        show_profile_warning: Whether to show a warning if the profile is not completed
        
    Returns:
        bool: True if profile is completed or warning is not shown, False otherwise
    """
    # Apply styling
    apply_custom_styling()
    
    # Display hero section
    custom_hero_section(title, subtitle, "", "")
    
    # Check profile completion if needed
    if show_profile_warning and "user_context" in st.session_state:
        # If profile not complete and warning is enabled
        if not any(st.session_state.user_context.values()):
            st.warning("Please complete your profile in the home page first!")
            st.markdown("""
            <div style="
                background-color: #2d3748; 
                border-radius: 12px; 
                padding: 2rem; 
                text-align: center; 
                border: 1px dashed #4a5568;
                margin-top: 2rem;
            ">
                <img src="https://cdn.iconscout.com/icon/free/png-256/free-user-profile-2938005-2421637.png" width="80" style="opacity: 0.6; margin-bottom: 1rem;">
                <h3 style="margin-bottom: 1rem; color: white;">Profile Required</h3>
                <p style="color: #e2e8f0; margin-bottom: 1.5rem;">Go to the home page and fill out your profile information to get personalized advice.</p>
                <a href="/" style="
                    display: inline-block;
                    background-color: #4299e1;
                    color: white;
                    padding: 0.5rem 1.5rem;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 600;
                ">Complete Profile</a>
            </div>
            """, unsafe_allow_html=True)
            return False
    
    return True

def display_user_profile(user_context, collapsed=False):
    """
    Display user profile information in a consistent format.
    
    Args:
        user_context: The user context dictionary
        collapsed: Whether to display as a collapsed expander
    """
    if collapsed:
        with st.expander("Your Profile", expanded=False):
            _render_profile_content(user_context)
    else:
        st.markdown("""
        <div style="
            background-color: #2d3748; 
            border-radius: 12px; 
            padding: 1.5rem; 
            border: 1px solid #4a5568;
            margin-bottom: 1.5rem;
        ">
            <h3 style="margin-top: 0; color: white;">Your Profile</h3>
        """, unsafe_allow_html=True)
        
        _render_profile_content(user_context)
        
        st.markdown("</div>", unsafe_allow_html=True)

def _render_profile_content(user_context):
    """Internal function to render profile content consistently"""
    st.markdown(f"<span style='color: white;'><strong>Current Role:</strong> {user_context.get('user_role', 'Not specified')}</span>", unsafe_allow_html=True)
    
    # Display target role if it exists
    target_role = user_context.get('target_role', '')
    if target_role:
        st.markdown(f"<span style='color: white;'><strong>Target Role:</strong> {target_role}</span>", unsafe_allow_html=True)
    
    st.markdown(f"<span style='color: white;'><strong>Experience:</strong> {user_context.get('experience', 'Not specified')}</span>", unsafe_allow_html=True)
    
    # Display skills as tags
    skills = user_context.get('skills', [])
    if skills:
        st.markdown("<span style='color: white;'><strong>Skills:</strong></span>", unsafe_allow_html=True)
        skill_html = "<div style='display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;'>"
        for skill in skills[:10]:  # Show up to 10 skills
            skill_html += f"""
            <span style='
                background-color: #4299e1; 
                color: white; 
                padding: 0.25rem 0.75rem; 
                border-radius: 999px; 
                font-size: 0.875rem;
                display: inline-block;
            '>{skill}</span>
            """
        skill_html += "</div>"
        st.markdown(skill_html, unsafe_allow_html=True)
    
    # Display career goals
    career_goals = user_context.get('career_goals', '')
    if career_goals:
        st.markdown("<span style='color: white;'><strong>Career Goals:</strong></span>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #e2e8f0;'>{career_goals}</p>", unsafe_allow_html=True)

def display_quick_action_buttons(actions):
    """
    Display a row of quick action buttons.
    
    Args:
        actions: List of dictionaries with keys 'label' and 'page'
    """
    cols = st.columns(len(actions))
    
    for i, action in enumerate(actions):
        with cols[i]:
            if st.button(action['label'], use_container_width=True):
                st.switch_page(action['page'])

def styled_container(title, content=None):
    """
    Create a styled container with a title.
    
    Args:
        title: Container title
        content: Optional HTML content to include
        
    Returns:
        The container for further content addition
    """
    container = st.container()
    
    with container:
        st.markdown(f"""
        <div style="
            background-color: #2d3748; 
            border-radius: 12px; 
            padding: 1.5rem; 
            border: 1px solid #4a5568;
            margin-bottom: 1.5rem;
        ">
            <h3 style="margin-top: 0; color: white;">{title}</h3>
        """, unsafe_allow_html=True)
        
        if content:
            st.markdown(content, unsafe_allow_html=True)
    
    return container

def end_styled_container():
    """End a styled container"""
    st.markdown("</div>", unsafe_allow_html=True)

def display_empty_state(title, description, icon_url=None, action_label=None, action_url=None):
    """
    Display an empty state with an icon and description.
    
    Args:
        title: Empty state title
        description: Empty state description
        icon_url: URL to an icon image
        action_label: Optional action button label
        action_url: Optional action button URL
    """
    icon_html = ""
    if icon_url:
        icon_html = f'<img src="{icon_url}" width="80" style="opacity: 0.6; margin-bottom: 1rem;">'
    
    action_html = ""
    if action_label and action_url:
        action_html = f"""
        <a href="{action_url}" style="
            display: inline-block;
            background-color: #4299e1;
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            margin-top: 1rem;
        ">{action_label}</a>
        """
    
    st.markdown(f"""
    <div style="
        background-color: #2d3748; 
        border-radius: 12px; 
        padding: 2rem; 
        text-align: center; 
        border: 1px dashed #4a5568;
        margin-top: 2rem;
    ">
        {icon_html}
        <h3 style="margin-bottom: 1rem; color: white;">{title}</h3>
        <p style="color: #e2e8f0; margin-bottom: 1.5rem;">{description}</p>
        {action_html}
    </div>
    """, unsafe_allow_html=True)

def profile_completion_indicator(completion_percentage):
    """
    Displays a visual progress indicator for profile completion
    
    Args:
        completion_percentage: Integer percentage of profile completion (0-100)
    """
    # Ensure percentage is within bounds
    completion_percentage = max(0, min(100, completion_percentage))
    
    # Determine status color based on completion percentage
    if completion_percentage < 40:
        status_color = "#f56565"  # Red
        message = "Just getting started"
    elif completion_percentage < 70:
        status_color = "#ed8936"  # Orange
        message = "Making good progress"
    else:
        status_color = "#48bb78"  # Green
        message = "Almost there!"
    
    # Display progress bar with percentage
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="color: white; font-size: 0.875rem; font-weight: 500;">Profile Completion</span>
            <span style="color: {status_color}; font-weight: 600;">{completion_percentage}%</span>
        </div>
        <div style="background-color: #4a5568; border-radius: 9999px; height: 8px; overflow: hidden;">
            <div style="width: {completion_percentage}%; height: 100%; background-color: {status_color};"></div>
        </div>
        <div style="text-align: right; margin-top: 0.25rem;">
            <span style="color: #e2e8f0; font-size: 0.75rem;">{message}</span>
        </div>
    </div>
    """, unsafe_allow_html=True) 