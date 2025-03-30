import streamlit as st
from typing import Dict, Any
import plotly.graph_objects as go
from datetime import datetime
from components.learning_path_progress import display_learning_path_progress

class ProfileDashboard:
    def __init__(self, user_context: Dict[str, Any]):
        """Initialize the profile dashboard with user context"""
        self.required_fields = [
            'user_role', 'experience', 'skills',
            'interests', 'career_goals'
        ]
        self.user_context = user_context
        self.completion_percentage = self._calculate_completion_percentage()
        
    def _calculate_completion_percentage(self) -> float:
        """Calculate the profile completion percentage"""
        filled_fields = sum(1 for field in self.required_fields 
                          if self.user_context.get(field) not in [None, "", [], {}])
        return (filled_fields / len(self.required_fields)) * 100
    
    def calculate_profile_completion(self) -> float:
        """Calculate profile completion percentage"""
        required_fields = [
            'user_role', 'experience', 'skills',
            'career_goals', 'education'
        ]
        optional_fields = ['interests', 'certifications', 'achievements']
        
        completed = sum(1 for field in required_fields 
                       if self.user_context.get(field))
        optional_completed = sum(1 for field in optional_fields 
                               if self.user_context.get(field))
        
        # Required fields count more towards completion
        completion = (completed / len(required_fields) * 0.8 +
                     optional_completed / len(optional_fields) * 0.2) * 100
        return round(completion, 1)
    
    def display_progress_chart(self):
        """Display profile completion progress chart"""
        completion = self.calculate_profile_completion()
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=completion,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Profile Completion"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#1f77b4"},
                'steps': [
                    {'range': [0, 33], 'color': "#ffebee"},
                    {'range': [33, 66], 'color': "#e3f2fd"},
                    {'range': [66, 100], 'color': "#e8f5e9"}
                ]
            }
        ))
        
        st.plotly_chart(fig)
    
    def display_skill_breakdown(self):
        """Display skill level breakdown"""
        if not self.user_context.get('skills'):
            st.warning("No skills added yet")
            return
            
        # Count total number of skills
        total_skills = len(self.user_context['skills'])
        
        # For now, we'll consider all skills as intermediate level
        # until we implement proper skill level tracking
        levels = {
            'beginner': 0,
            'intermediate': total_skills,  # Temporarily assign all skills as intermediate
            'advanced': 0,
            'expert': 0
        }
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(levels.keys()),
                y=list(levels.values()),
                marker_color=['#ffcdd2', '#90caf9', '#a5d6a7', '#4caf50']
            )
        ])
        
        fig.update_layout(
            title="Skill Distribution",
            xaxis_title="Skill Level",
            yaxis_title="Number of Skills",
            height=300  # Reduced height for better layout
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_skills_section(self):
        """Render the skills section with improved layout"""
        st.subheader("Skills Management")
        
        # Single column layout for skills
        with st.container():
            # Add new skills
            with st.form("add_skills", clear_on_submit=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    new_skill = st.text_input("Add New Skill", placeholder="Enter a skill...")
                with col2:
                    submit_button = st.form_submit_button("Add", use_container_width=True)
                
                if submit_button and new_skill:
                    if "skills" not in self.user_context:
                        self.user_context["skills"] = []
                    if new_skill not in self.user_context["skills"]:
                        self.user_context["skills"].append(new_skill)
                        st.success("✅ Skill added!")
                    else:
                        st.warning("⚠️ Skill already exists")
            
            # Display skills in a grid
            if self.user_context.get('skills'):
                st.markdown("##### Current Skills")
                skills_list = self.user_context['skills']
                cols = st.columns(3)
                for i, skill in enumerate(skills_list):
                    with cols[i % 3]:
                        # Create a container for each skill with better visibility
                        st.markdown(
                            f"""
                            <div style='
                                background-color: #e6e6e6;
                                padding: 8px 15px;
                                border-radius: 5px;
                                margin: 5px 0;
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                                color: #333333;
                                font-size: 0.9em;
                            '>
                                <span>{skill}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        if st.button("🗑️", key=f"remove_skill_{i}", help="Remove skill"):
                            self.user_context["skills"].pop(i)
                            st.rerun()
            else:
                st.info("No skills added yet. Add your skills to get started!")
    
    def display_recent_activity(self):
        """Display recent activity timeline"""
        st.subheader("Recent Activity")
        
        activities = self.user_context.get('activities', [])
        if not activities:
            st.info("No recent activities to display")
            return
            
        for activity in activities[:5]:  # Show last 5 activities
            with st.expander(
                f"{activity['type']} - {activity['date']}"
            ):
                st.write(activity['description'])

    def display_all_activities(self):
        """Display all activities in a categorized manner"""
        # Get activities count for the title
        activities = self.user_context.get('activities', [])
        activity_count = len(activities)
        
        st.title(f"All Activities ({activity_count})")
        
        # We're removing this display since it's already shown in the profile
        # display_learning_path_progress()
        
        st.markdown("---")
        st.subheader("Activity History")
        
        if not activities:
            st.info("No activities to display yet")
            return
        
        # Create categories for different types of activities
        activity_categories = {
            "Skill Development": [],
            "Career Options": [],
            "Learning Path": [],
            "Interview": [],
            "Networking": [],
            "Profile Update": [],
            "Other": []
        }
        
        # Sort activities into categories
        for activity in activities:
            activity_type = activity['type']
            if "skill" in activity_type.lower():
                activity_categories["Skill Development"].append(activity)
            elif "career" in activity_type.lower() or "job" in activity_type.lower():
                activity_categories["Career Options"].append(activity)
            elif "learning" in activity_type.lower() or "path" in activity_type.lower():
                activity_categories["Learning Path"].append(activity)
            elif "interview" in activity_type.lower():
                activity_categories["Interview"].append(activity)
            elif "network" in activity_type.lower():
                activity_categories["Networking"].append(activity)
            elif "profile" in activity_type.lower() or "update" in activity_type.lower():
                activity_categories["Profile Update"].append(activity)
            else:
                activity_categories["Other"].append(activity)
        
        # Create tabs for categories that have activities
        tabs = []
        for category, category_activities in activity_categories.items():
            if category_activities:
                tabs.append(category)
        
        if tabs:
            selected_tab = st.tabs(tabs)
            
            for i, tab in enumerate(tabs):
                with selected_tab[i]:
                    category_activities = activity_categories[tab]
                    for activity in sorted(category_activities, key=lambda x: x['date'], reverse=True):
                        # Use a container with better color contrast
                        with st.container():
                            st.markdown(f"""
                            <div style="
                                background-color: #2d3748; 
                                border-radius: 8px; 
                                padding: 10px 15px; 
                                margin-bottom: 10px;
                                border-left: 3px solid #4299e1;
                            ">
                                <p style="font-weight: bold; margin-bottom: 5px; color: #e2e8f0;">{activity['date']} - {activity['type']}</p>
                                <p style="color: #e2e8f0;">{activity['description']}</p>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("No activities categorized yet")
    
    def render(self):
        """Render the complete dashboard"""
        st.title("Career Profile Dashboard")
        
        # Debug session state contents
        print("Profile Dashboard - Session State Contents:")
        if "user_context" in st.session_state:
            print(f"  User Context: {st.session_state.user_context.keys()}")
        if "current_learning_path" in st.session_state:
            print(f"  Current Learning Path: {st.session_state.current_learning_path}")
        if "skill_progress" in st.session_state:
            print(f"  Skills in Progress: {len(st.session_state.skill_progress)}")
        
        # Save the current session state to ensure data persistence
        try:
            from utils.data_persistence import DataPersistence
            data_persistence = DataPersistence()
            success = data_persistence.save_session_state(dict(st.session_state))
            if success:
                print("Session state saved automatically when viewing profile.")
            else:
                print("Warning: Failed to save session state automatically.")
        except Exception as e:
            print(f"Error saving session state automatically: {str(e)}")
        
        # Profile completion, basic info, and activities button
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            self.display_progress_chart()
        with col2:
            st.subheader("Quick Stats")
            st.metric(
                "Current Role",
                self.user_context.get('user_role', 'Not specified')
            )
            st.metric(
                "Experience",
                self.user_context.get('experience', 'Not specified')
            )
        with col3:
            st.markdown("<br><br>", unsafe_allow_html=True)  # Add spacing to align with other columns
            if st.button("📋 View All Activities", use_container_width=True):
                st.session_state["show_all_activities"] = True
                st.rerun()
                
        # Display the all activities view when the button is clicked
        if st.session_state.get("show_all_activities", False):
            st.markdown("---")
            self.display_all_activities()
            if st.button("Close Activities View"):
                st.session_state["show_all_activities"] = False
                st.rerun()
            return  # Early return to only show the activities view
        
        # Skills Section with new layout
        st.markdown("---")
        self.render_skills_section()
        
        # Skills Analysis Chart
        st.markdown("---")
        self.display_skill_breakdown()
        
        # Education Section
        st.markdown("---")
        st.subheader("Education")
        with st.expander("Add/Edit Education", expanded=True):
            # Form for adding new education
            with st.form("add_education"):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    degree = st.text_input("Degree/Certificate")
                with col2:
                    institution = st.text_input("Institution")
                with col3:
                    year = st.text_input("Year of Completion")
                
                if st.form_submit_button("Add Education"):
                    if degree and institution and year:
                        new_education = {
                            "degree": degree,
                            "institution": institution,
                            "year": year
                        }
                        if "education" not in self.user_context:
                            self.user_context["education"] = []
                        self.user_context["education"].append(new_education)
                        st.success("Education added successfully!")
                    else:
                        st.error("Please fill all education fields")
            
            # Display and edit existing education
            if self.user_context.get("education"):
                st.write("Current Education:")
                for i, edu in enumerate(self.user_context["education"]):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"**{edu['degree']}** - {edu['institution']} ({edu['year']})")
                    with col2:
                        if st.button("Remove", key=f"remove_edu_{i}"):
                            self.user_context["education"].pop(i)
                            st.rerun()
        
        # Career goals and interests
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Career Goals")
            goals = self.user_context.get('career_goals', 'Not specified')
            st.write(goals)
        
        with col4:
            st.subheader("Interests")
            interests = self.user_context.get('interests', [])
            if interests:
                st.write(", ".join(interests))
            else:
                st.write("No interests specified") 