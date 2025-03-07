import streamlit as st
from typing import Dict, Any
import plotly.graph_objects as go
from datetime import datetime

class ProfileDashboard:
    def __init__(self, user_context: Dict[str, Any]):
        self.user_context = user_context
        
    def calculate_profile_completion(self) -> float:
        """Calculate profile completion percentage"""
        required_fields = [
            'current_role', 'experience', 'skills',
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
            
        for activity in activities[-5:]:  # Show last 5 activities
            with st.expander(
                f"{activity['type']} - {activity['date']}"
            ):
                st.write(activity['description'])
    
    def render(self):
        """Render the complete dashboard"""
        st.title("Career Profile Dashboard")
        
        # Profile completion and basic info
        col1, col2 = st.columns([2, 1])
        with col1:
            self.display_progress_chart()
        with col2:
            st.subheader("Quick Stats")
            st.metric(
                "Current Role",
                self.user_context.get('current_role', 'Not specified')
            )
            st.metric(
                "Experience",
                self.user_context.get('experience', 'Not specified')
            )
        
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
        
        # Recent activity
        self.display_recent_activity()
        
        # Action items
        st.subheader("Suggested Actions")
        completion = self.calculate_profile_completion()
        if completion < 100:
            missing_items = []
            if not self.user_context.get('skills'):
                missing_items.append("Add your skills")
            if not self.user_context.get('education'):
                missing_items.append("Add education details")
            if not self.user_context.get('interests'):
                missing_items.append("Add your interests")
            
            for item in missing_items:
                st.warning(item) 