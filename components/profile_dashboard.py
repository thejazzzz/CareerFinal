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
            
        skills = self.user_context['skills']
        levels = {
            'beginner': 0,
            'intermediate': 0,
            'advanced': 0,
            'expert': 0
        }
        
        for skill in skills:
            level = skill.get('level', 'beginner').lower()
            if level in levels:
                levels[level] += 1
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(levels.keys()),
                y=list(levels.values()),
                marker_color=['#ffcdd2', '#90caf9', '#a5d6a7', '#4caf50']
            )
        ])
        
        fig.update_layout(
            title="Skill Level Distribution",
            xaxis_title="Skill Level",
            yaxis_title="Number of Skills"
        )
        
        st.plotly_chart(fig)
    
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
        
        # Skills breakdown
        st.subheader("Skills Analysis")
        self.display_skill_breakdown()
        
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