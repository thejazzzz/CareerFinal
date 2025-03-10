import streamlit as st
import os
from typing import Dict, List
from config.config import Config
from agents.resume_analyzer import ResumeAnalyzerAgent
from agents.job_searcher import JobSearchAgent
from agents.skills_advisor import SkillsAdvisorAgent
from agents.career_navigator import CareerNavigatorAgent
from agents.interview_coach import InterviewCoachAgent
from agents.career_chatbot import CareerChatbotAgent
from agents.cover_letter_generator import CoverLetterGeneratorAgent
from utils.form_validation import FormValidation
from utils.data_persistence import DataPersistence
from components.profile_dashboard import ProfileDashboard

# Page configuration
st.set_page_config(
    page_title="Career Assistant MAS",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data persistence
data_persistence = DataPersistence()

# Initialize session state with default values
def init_session_state():
    """Initialize session state variables with default values"""
    # Try to load saved session state
    saved_state = data_persistence.load_session_state()
    
    # Default session variables
    session_vars = {
        "user_context": {
            "current_role": "",
            "experience": "",
            "skills": [],
            "interests": [],
            "career_goals": "",
            "activities": []  # New field for tracking activities
        },
        "chat_history": [],
        "resume_analysis": None,
        "job_search_results": None,
        "skills_analysis": None,
        "career_path": None,
        "saved_jobs": [],
        "saved_interviews": [],
        "saved_career_plans": [],
        "current_interview": None,
        "profile_completed": False
    }
    
    # Update defaults with saved state if available
    if saved_state:
        for key, value in saved_state.items():
            session_vars[key] = value
    
    # Initialize session state variables
    for var, default_value in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value

# Initialize session state
init_session_state()

# Function to save session state
def save_current_state():
    """Save current session state"""
    data_persistence.save_session_state(dict(st.session_state))

# Initialize agents
@st.cache_resource
def initialize_agents():
    return {
        "resume_analyzer": ResumeAnalyzerAgent(verbose=True),
        "job_searcher": JobSearchAgent(verbose=True),
        "skills_advisor": SkillsAdvisorAgent(verbose=True),
        "career_navigator": CareerNavigatorAgent(verbose=True),
        "interview_coach": InterviewCoachAgent(verbose=True),
        "career_chatbot": CareerChatbotAgent(verbose=True),
        "cover_letter_generator": CoverLetterGeneratorAgent(verbose=True)
    }

agents = initialize_agents()

def update_user_activity(activity_type: str, description: str):
    """Add a new activity to the user's activity history"""
    from datetime import datetime
    activity = {
        "type": activity_type,
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if "activities" not in st.session_state.user_context:
        st.session_state.user_context["activities"] = []
    st.session_state.user_context["activities"].insert(0, activity)
    # Save updated state with session_state argument
    data_persistence.save_session_state(dict(st.session_state))

def main():
    st.title("🚀 Career Assistant Multi-Agent System")
    
    # Top navigation
    if not st.session_state.profile_completed:
        tab1, tab2 = st.tabs(["Create Profile", "About"])
        
        with tab1:
            st.write("""
            Welcome to your AI-powered career development platform! To get started, please complete your profile.
            This will help us provide personalized career guidance and recommendations.
            """)
            
            # Profile creation form
            with st.container():
                st.header("Create Your Profile")
                
                # Add resume upload option
                st.write("**Upload Resume (Optional)**")
                st.write("Upload your resume to automatically extract your skills and experience.")
                uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
                
                extracted_skills = []
                if uploaded_file:
                    with st.spinner("Analyzing resume..."):
                        # Save uploaded file temporarily
                        temp_path = f"temp_{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getvalue())
                        
                        try:
                            # Analyze resume
                            analyzer = agents["resume_analyzer"]
                            analysis = analyzer.process_resume(temp_path)
                            
                            # Extract skills and experience
                            extracted_skills = analysis["structured_data"].get("skills", [])
                            extracted_experience = next(
                                (exp for exp in analysis["structured_data"].get("work_experience", [])
                                if "years" in exp.lower()),
                                ""
                            )
                            
                            st.success("Resume analyzed successfully!")
                            
                            # Store analysis in session state
                            st.session_state.resume_analysis = analysis
                            
                            # Display extracted information
                            with st.expander("View Extracted Information"):
                                st.write("**Extracted Skills:**")
                                for skill in extracted_skills:
                                    skill_name = skill['name']
                                    skill_confidence = skill['confidence']
                                    skill_category = skill['category']
                                    
                                    # Now use these variables to display the skill information
                                    st.write(f"• {skill_name} ({skill_category}, confidence: {skill_confidence})")
                                if extracted_experience:
                                    st.write("**Extracted Experience:**")
                                    st.write(extracted_experience)
                        
                        except Exception as e:
                            st.error(f"Error analyzing resume: {str(e)}")
                        
                        finally:
                            # Cleanup temporary file
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                
                with st.form("user_profile"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        current_role = st.text_input("Current Role")
                        experience = st.text_input("Years of Experience")
                        
                        # Skills input with option to use extracted skills
                        st.write("**Skills**")
                        use_extracted = False
                        if extracted_skills:
                            use_extracted = st.checkbox("Use skills extracted from resume")
                        
                        if use_extracted:
                            skills_text = ", ".join([skill['name'] for skill in extracted_skills])
                            skills = skills_text  # Assign to skills variable
                            st.text_area("Skills (comma-separated)", value=skills_text, disabled=True)
                        else:
                            skills = st.text_area(
                                "Skills (comma-separated)",
                                help="Enter your skills manually or upload a resume to extract them automatically"
                            )
                    
                    with col2:
                        interests = st.text_area("Interests (comma-separated)")
                        career_goals = st.text_area("Career Goals")
                    
                    if st.form_submit_button("Save Profile"):
                        # Validate form inputs
                        is_valid, errors = FormValidation.validate_profile_form(
                            current_role, experience, skills, interests, career_goals
                        )
                        
                        if is_valid:
                            # Update user context
                            st.session_state.user_context.update({
                                "current_role": current_role,
                                "experience": experience,
                                "skills": FormValidation.format_skills(skills),
                                "interests": FormValidation.format_skills(interests),
                                "career_goals": FormValidation.sanitize_input(career_goals)
                            })
                            st.session_state.profile_completed = True
                            update_user_activity(
                                "Profile Update",
                                "Updated career profile information"
                            )
                            save_current_state()  # Save state after update
                            st.rerun()
                        else:
                            for error in errors:
                                st.error(error)
        
        with tab2:
            st.write("""
            Welcome to your AI-powered career development platform! This system combines multiple 
            specialized agents to help you navigate your career journey effectively.
            """)
            st.write("Please complete your profile to access all features.")
    
    else:
        tab1, tab2, tab3 = st.tabs(["Profile", "Dashboard", "Services"])
        
        with tab1:
            st.header("Your Profile")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Current Role:** ", st.session_state.user_context["current_role"])
                st.write("**Experience:** ", st.session_state.user_context["experience"])
                st.write("**Skills:** ", ", ".join(st.session_state.user_context["skills"]))
            
            with col2:
                st.write("**Interests:** ", ", ".join(st.session_state.user_context["interests"]))
                st.write("**Career Goals:** ", st.session_state.user_context["career_goals"])
            
            if st.button("Edit Profile"):
                st.session_state.profile_completed = False
                st.rerun()
        
        with tab2:
            # Display profile dashboard
            dashboard = ProfileDashboard(st.session_state.user_context)
            dashboard.render()
        
        with tab3:
            st.write("""
            Welcome to your AI-powered career development platform! This system combines multiple 
            specialized agents to help you navigate your career journey effectively.
            """)
            
            # Display available agents in a grid
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.header("Career Development")
                st.markdown("""
                💬 [Career Chatbot](/Career_Chatbot)
                - Get instant answers to career questions
                - Personalized career advice
                - Resource recommendations
                
                📝 [Resume Analyzer](/Resume_Analyzer)
                - Detailed resume feedback
                - Skills extraction
                - ATS compatibility check
                
                ✉️ [Cover Letter Generator](/Cover_Letter_Generator)
                - Customized cover letters
                - Multiple styles
                - Real-time improvements
                """)
            
            with col2:
                st.header("Job Search & Skills")
                st.markdown("""
                🔍 [Job Search](/Job_Search)
                - AI-powered job matching
                - Skill fit analysis
                - Save interesting positions
                
                📚 [Skills Development](/Skills_Development)
                - Skill gap analysis
                - Learning path creation
                - Progress tracking
                
                🌟 [Skills Advisor](/Skills_Advisor)
                - Personalized recommendations
                - Industry-specific skills
                - Learning resources
                """)
            
            with col3:
                st.header("Career Growth")
                st.markdown("""
                🧭 [Career Navigator](/Career_Navigator)
                - Career path planning
                - Industry insights
                - Transition strategies
                
                🎤 [Interview Coach](/Interview_Coach)
                - Mock interviews
                - Real-time feedback
                - Performance tracking
                
                🎯 [Career Planning](/Career_Planning)
                - Goal setting
                - Action plans
                - Progress monitoring
                """)
            
            # Display recent activity if available
            if (st.session_state.chat_history or 
                st.session_state.resume_analysis or 
                st.session_state.job_search_results or 
                st.session_state.saved_jobs):
                
                st.header("Recent Activity")
                
                activity_col1, activity_col2 = st.columns(2)
                
                with activity_col1:
                    if st.session_state.chat_history:
                        with st.expander("Recent Conversations"):
                            for chat in st.session_state.chat_history[-3:]:
                                st.write(f"**You:** {chat['user']}")
                                st.write(f"**Assistant:** {chat['bot']}")
                                st.divider()
                    
                    if st.session_state.resume_analysis:
                        with st.expander("Latest Resume Analysis"):
                            st.write("**Key Skills:**")
                            for skill in st.session_state.resume_analysis["structured_data"].get("skills", [])[:5]:
                                st.write(f"• {skill}")
                
                with activity_col2:
                    if st.session_state.saved_jobs:
                        with st.expander("Saved Jobs"):
                            for job in st.session_state.saved_jobs[-3:]:
                                st.write(f"**{job['title']}** at {job['company']}")
                                st.write(f"Location: {job['location']}")
                                st.divider()
                    
                    if st.session_state.career_path:
                        with st.expander("Career Plan"):
                            for path in st.session_state.career_path["structured_data"]["path_options"][:3]:
                                st.write(f"• {path}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    Made with ❤️ using:
    - Streamlit
    - LangChain
    - OpenAI
    - Adzuna API
    """
)

if __name__ == "__main__":
    # Validate configuration
    Config.validate_config()
    
    # Run the app
    main() 