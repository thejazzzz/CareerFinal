import streamlit as st
import os
import time
import json
import pandas as pd
from typing import Dict, List
from config.config import Config
from agents.resume_analyzer import ResumeAnalyzerAgent
from agents.job_searcher import JobSearchAgent
from agents.skills_advisor import SkillsAdvisorAgent
from agents.career_navigator import CareerNavigatorAgent
from agents.interview_coach import InterviewCoachAgent
from agents.career_chatbot import CareerChatbotAgent
from agents.cover_letter_generator import CoverLetterGeneratorAgent
from agents.communication_agent import CommunicationAgent
from utils.form_validation import FormValidation
from utils.data_persistence import DataPersistence
from components.profile_dashboard import ProfileDashboard
from components.styling import custom_hero_section, feature_card, resume_upload_area, profile_completion_indicator, apply_custom_css
from components.learning_path_progress import display_learning_path_progress

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
            "user_role": "",
            "target_role": "",
            "experience": "",
            "skills": [],
            "interests": [],
            "career_goals": "",
            "activities": []
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
        # Handle the migration from current_role to user_role
        if "user_context" in saved_state and "current_role" in saved_state["user_context"]:
            saved_state["user_context"]["user_role"] = saved_state["user_context"].pop("current_role")
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
    """Save current session state and return success status"""
    try:
        success = data_persistence.save_session_state(dict(st.session_state))
        print(f"Save session state result: {success}")
        return success
    except Exception as e:
        print(f"Error saving session state: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

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
        "cover_letter_generator": CoverLetterGeneratorAgent(verbose=True),
        "communication_agent": CommunicationAgent(verbose=True)
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
    # Apply updated styling for a clean, modern UI
    apply_custom_css()
    
    if not st.session_state.profile_completed:
        # Hero section for new users
        custom_hero_section(
            "Career Assistant Multi-Agent System",
            "Your AI-powered platform for personalized career guidance and development",
            "Create Your Profile",
            "#profile-creation"
        )
        
        st.markdown('<div id="profile-creation"></div>', unsafe_allow_html=True)
        
        # Profile creation section with prominent resume upload
        st.markdown("""
        <div style="text-align: center; max-width: 800px; margin: 0 auto; padding: 1rem;">
            <h2 style="margin-bottom: 1.5rem; color: white;">The easiest way to get started is by uploading your resume</h2>
            <p style="color: #e2e8f0; margin-bottom: 2rem; font-size: 1.1rem;">
                Our AI will analyze your resume and automatically fill in your profile details.
                You can always edit the information afterward.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Centered resume upload section
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            uploaded_file = resume_upload_area(st.file_uploader)
        
        # Message for users without a resume
        if not uploaded_file:
            st.markdown("""
            <div style="text-align: center; max-width: 600px; margin: 0 auto 2rem auto;">
                <p style="color: #e2e8f0;">Don't have a resume? You can still 
                <a href="#manual-profile" style="color: #4299e1; text-decoration: none; font-weight: 500;">create your profile manually</a>.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Main tabs - only show if no resume is uploaded or after analysis
        extracted_skills = []
        resume_analyzed = False
        
        if uploaded_file:
            with st.spinner("Analyzing your resume..."):
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
                    
                    st.success("✅ Resume analyzed successfully!")
                    resume_analyzed = True
                    
                    # Store analysis in session state
                    st.session_state.resume_analysis = analysis
                    
                    # Display extracted information in a visually appealing way
                    st.markdown('<div style="max-width: 800px; margin: 0 auto;">', unsafe_allow_html=True)
                    with st.expander("View Extracted Information", expanded=True):
                        st.subheader("Resume Analysis Results")
                        
                        # Display skills in a visually appealing way
                        st.write("<span style='color: white;'><strong>Extracted Skills:</strong></span>", unsafe_allow_html=True)
                        
                        # Create columns for skills
                        skills_cols = st.columns(3)
                        for i, skill in enumerate(extracted_skills):
                            skill_name = skill['name']
                            skill_category = skill['category']
                            
                            with skills_cols[i % 3]:
                                st.markdown(f"""
                                <div style="
                                    background-color: #3182ce; 
                                    border-radius: 8px; 
                                    padding: 0.75rem; 
                                    margin-bottom: 0.75rem;
                                    border-left: 3px solid #2b6cb0;
                                ">
                                    <strong style="color: white;">{skill_name}</strong><br>
                                    <span style="color: #e2e8f0; font-size: 0.875rem;">{skill_category}</span>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if extracted_experience:
                            st.write("<span style='color: white;'><strong>Extracted Experience:</strong></span>", unsafe_allow_html=True)
                            st.markdown(f"""
                            <div style="
                                padding: 0.75rem; 
                                background-color: #2d3748; 
                                border-radius: 8px;
                                border-left: 3px solid #4299e1;
                                margin-bottom: 1rem;
                            ">
                                <span style="color: white;">{extracted_experience}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Add detailed resume analysis
                        st.write("<span style='color: white;'><strong>Resume Feedback:</strong></span>", unsafe_allow_html=True)
                        
                        feedback = analysis.get("feedback", {})
                        strengths = feedback.get("strengths", [])
                        weaknesses = feedback.get("weaknesses", [])
                        suggestions = feedback.get("suggestions", [])
                        
                        if strengths:
                            st.markdown("<span style='color: #48bb78;'><strong>Strengths:</strong></span>", unsafe_allow_html=True)
                            for strength in strengths:
                                st.markdown(f"<div style='color: #e2e8f0; margin-left: 1rem;'>• {strength}</div>", unsafe_allow_html=True)
                        
                        if weaknesses:
                            st.markdown("<span style='color: #f56565;'><strong>Areas for Improvement:</strong></span>", unsafe_allow_html=True)
                            for weakness in weaknesses:
                                st.markdown(f"<div style='color: #e2e8f0; margin-left: 1rem;'>• {weakness}</div>", unsafe_allow_html=True)
                        
                        if suggestions:
                            st.markdown("<span style='color: #4299e1;'><strong>Suggestions:</strong></span>", unsafe_allow_html=True)
                            for suggestion in suggestions:
                                st.markdown(f"<div style='color: #e2e8f0; margin-left: 1rem;'>• {suggestion}</div>", unsafe_allow_html=True)
                        
                    st.markdown('</div>', unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"Error analyzing resume: {str(e)}")
                
                finally:
                    # Cleanup temporary file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        
        # Display tabs after resume analysis or if no file uploaded
        if not uploaded_file or resume_analyzed:
            st.markdown('<div id="manual-profile"></div>', unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["Complete Your Profile", "About"])
            
            with tab1:
                # Profile form with a cleaner look
                if resume_analyzed:
                    st.markdown("""
                    <div style="max-width: 800px; margin: 0 auto 1.5rem auto;">
                        <h2 style="color: white;">Review and Complete Your Profile</h2>
                        <p style="color: #e2e8f0;">We've pre-filled your information based on your resume. Review and make any necessary changes.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="max-width: 800px; margin: 0 auto 1.5rem auto;">
                        <h2 style="color: white;">Complete Your Profile</h2>
                        <p style="color: #e2e8f0;">Fill in the information below to get personalized career guidance.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Center the form
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    with st.form("user_profile", clear_on_submit=False):
                        # Get values from resume analysis if available
                        current_role_default = ""
                        experience_default = ""
                        skills_default = []
                        
                        if 'resume_analysis' in st.session_state and st.session_state.resume_analysis:
                            analysis = st.session_state.resume_analysis
                            structured_data = analysis.get('structured_data', {})
                            
                            # Extract values from the analysis
                            current_role_default = structured_data.get('user_role', '')
                            experience_default = next(
                                (exp for exp in structured_data.get('work_experience', []) 
                                if 'years' in exp.lower()), '')
                            skills_default = [skill['name'] for skill in structured_data.get('skills', [])]
                        
                        # Form fields with defaults from resume
                        current_role = st.text_input("Current Role", value=current_role_default)
                        target_role = st.text_input("Target Role", value="")
                        experience = st.text_input("Years of Experience", value=experience_default)
                        
                        # Skills input with option to use extracted skills
                        st.write("<span style='color: white;'><strong>Skills</strong></span>", unsafe_allow_html=True)
                        use_extracted = False
                        if extracted_skills:
                            use_extracted = st.checkbox("Use skills extracted from resume", value=True)
                        
                        if use_extracted and extracted_skills:
                            skills_text = ", ".join([skill['name'] for skill in extracted_skills])
                            skills = skills_text
                            st.text_area("Skills (comma-separated)", value=skills_text, disabled=True)
                        else:
                            skills = st.text_area(
                                "Skills (comma-separated)",
                                value=", ".join(skills_default) if skills_default else "",
                                help="Enter your skills, separated by commas"
                            )
                        
                        interests = st.text_area("Interests (comma-separated)", 
                                                help="Enter your professional interests, separated by commas")
                        
                        career_goals = st.text_area("Career Goals",
                                                  help="What are your short and long-term career objectives?")
                        
                        # Show profile completion progress based on fields filled
                        completion = 0
                        if current_role:
                            completion += 20
                        if experience:
                            completion += 20
                        if skills:
                            completion += 20
                        if interests:
                            completion += 20
                        if career_goals:
                            completion += 20
                            
                        profile_completion_indicator(completion)
                        
                        submit_button = st.form_submit_button("Complete Profile", use_container_width=True)
                        
                        if submit_button:
                            validation = FormValidation()
                            errors = validation.validate_profile_form(
                                current_role, experience, skills, interests, career_goals
                            )
                            
                            if errors:
                                for error in errors:
                                    st.error(error)
                            else:
                                # Update session state
                                st.session_state.user_context["user_role"] = current_role
                                st.session_state.user_context["target_role"] = target_role
                                st.session_state.user_context["experience"] = experience
                                st.session_state.user_context["skills"] = [skill.strip() for skill in skills.split(",")]
                                st.session_state.user_context["interests"] = [interest.strip() for interest in interests.split(",")]
                                st.session_state.user_context["career_goals"] = career_goals
                                st.session_state.profile_completed = True
                                
                                # Ensure user has a unique ID
                                if "user_id" not in st.session_state.user_context:
                                    import uuid
                                    st.session_state.user_context["user_id"] = str(uuid.uuid4())
                                    print(f"Generated new user ID: {st.session_state.user_context['user_id']}")
                                
                                # Log activity
                                update_user_activity("profile", "Created profile")
                                
                                # Save state
                                save_success = save_current_state()
                                if save_success:
                                    st.success("Profile completed and saved successfully!")
                                    print("Profile data saved successfully to database")
                                else:
                                    st.warning("Profile completed but there was an issue saving your data. Some features may not work correctly.")
                                    print("Failed to save profile data to database")
                                
                                st.balloons()
                                
                                # Rerun to show dashboard
                                st.rerun()
            
            with tab2:
                st.header("About Career Assistant")
                
                st.markdown("""
                Career Assistant is an AI-powered multi-agent system designed to help you navigate your career journey.
                From resume analysis to job search, skill development, and interview preparation, our platform provides
                personalized guidance tailored to your skills, experience, and career goals.
                """)
                
                # Feature cards in a 2x2 grid
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(feature_card(
                        "📚", 
                        "Skills Development", 
                        "Discover skills you need to develop and get personalized learning recommendations.",
                        "Learn More", 
                        "/Skills_Development"
                    ), unsafe_allow_html=True)
                    
                    st.markdown(feature_card(
                        "🔍", 
                        "Job Search", 
                        "Find job opportunities that match your skills and career goals.",
                        "Learn More", 
                        "/Job_Search"
                    ), unsafe_allow_html=True)
                
                with col2:
                    st.markdown(feature_card(
                        "✉️", 
                        "Cover Letter Generator", 
                        "Create tailored cover letters for specific job applications.",
                        "Learn More", 
                        "/Cover_Letter_Generator"
                    ), unsafe_allow_html=True)
                    
                    st.markdown(feature_card(
                        "🧭", 
                        "Career Navigation", 
                        "Get a personalized career roadmap based on your goals and current skills.",
                        "Learn More", 
                        "/6_🧭_Career_Navigator"
                    ), unsafe_allow_html=True)
    
    else:
        # Display dashboard for returning users
        st.markdown("<h2 style='color: white;'>Welcome Back!</h2>", unsafe_allow_html=True)
        
        dashboard = ProfileDashboard(st.session_state.user_context)
        dashboard.render()
        
        # Current Learning Path Progress (only here, not later)
        display_learning_path_progress()
        
        # Quick actions section
        st.markdown("<h3 style='color: white;'>Quick Actions</h3>", unsafe_allow_html=True)
        
        # Add CSS for consistent button styling
        st.markdown("""
        <style>
        div[data-testid="column"] {
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: stretch;
        }
        
        div[data-testid="column"] > div {
            width: 100%;
        }
        
        div[data-testid="column"] button {
            width: 100% !important;
            min-height: 45px !important;
            height: 100% !important;
            white-space: nowrap !important;
            padding: 10px 15px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            background-color: #3B82F6 !important;
            border: none !important;
            border-radius: 6px !important;
            color: white !important;
            font-size: 14px !important;
            line-height: 1.2 !important;
            margin: 0 !important;
            transition: background-color 0.2s ease !important;
        }
        
        div[data-testid="column"] button:hover {
            background-color: #2563EB !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create columns with equal width
        cols = st.columns(5)
        
        # Define button configurations
        buttons = [
            ("✉️ Cover Letter", "pages/2_✉️_Cover_Letter_Generator.py"),
            ("🔍 Search Jobs", "pages/4_🔍_Job_Search.py"),
            ("💬 Career Chat", "pages/1_💬_Career_Chatbot.py"),
            ("🎯 Update Skills", "pages/5_📚_Skills_Development.py"),
            ("🎤 Interview Coach", "pages/7_🎤_Interview_Coach.py")
        ]
        
        # Create buttons in columns
        for i, (label, page) in enumerate(buttons):
            with cols[i]:
                if st.button(label, use_container_width=True, key=f"quick_{i}"):
                    st.switch_page(page)
        
        # Career Navigation section
        st.markdown("<h3 style='color: white;'>Career Navigation</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #e2e8f0;'>Your personalized career roadmap based on your skills and goals.</p>", unsafe_allow_html=True)
        
        # Check if career path data exists
        if st.session_state.get("career_path"):
            career_path = st.session_state.career_path
            
            # Create a styled container for the career path
            st.markdown("""
            <div style="
                background-color: #2d3748;
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                border: 1px solid #4a5568;
                cursor: pointer;
            ">
            """, unsafe_allow_html=True)
            
            # Display career path content
            if isinstance(career_path, dict):
                # If it's a structured career path
                if "current_state" in career_path:
                    st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <h4 style="color: white; margin-bottom: 0.5rem;">Current State</h4>
                        <p style="color: #e2e8f0;">{career_path["current_state"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                if "target_state" in career_path:
                    st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <h4 style="color: white; margin-bottom: 0.5rem;">Target State</h4>
                        <p style="color: #e2e8f0;">{career_path["target_state"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                if "milestones" in career_path and career_path["milestones"]:
                    st.markdown("""
                    <h4 style="color: white; margin-bottom: 0.5rem;">Milestones</h4>
                    """, unsafe_allow_html=True)
                    
                    # Show only first 2 milestones on main page
                    show_milestones = career_path["milestones"][:2]
                    for i, milestone in enumerate(show_milestones):
                        st.markdown(f"""
                        <div style="
                            background-color: #3c4758;
                            border-radius: 8px;
                            padding: 1rem;
                            margin-bottom: 0.75rem;
                            border-left: 3px solid #4299e1;
                        ">
                            <p style="color: white; font-weight: 600;">{milestone.get('title', f'Milestone {i+1}')}</p>
                            <p style="color: #e2e8f0;">{milestone.get('description', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # If there are more milestones, add a note
                    if len(career_path["milestones"]) > 2:
                        st.markdown(f"""
                        <div style="text-align: center; margin-top: 0.5rem; margin-bottom: 0.5rem;">
                            <p style="color: #a0aec0;">+ {len(career_path["milestones"]) - 2} more milestones</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Add a View Details button styled to match the container
                    st.markdown("""
                    <div style="text-align: center; margin-top: 1rem;">
                        <a href="6_🧭_Career_Navigator" style="text-decoration: none;">
                            <div style="
                                display: inline-block;
                                background-color: #3B82F6;
                                color: white;
                                font-weight: 500;
                                padding: 0.5rem 1rem;
                                border-radius: 0.375rem;
                                cursor: pointer;
                                text-align: center;
                                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                            ">View Full Details</div>
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # If it's just text content
                st.markdown(f"""
                <div style="color: #e2e8f0;">
                    {career_path}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Add button to navigate to full career navigator
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("View Full Career Roadmap", use_container_width=True):
                    st.switch_page("pages/6_🧭_Career_Navigator.py")
        else:
            # If no career path data exists yet
            st.info("You haven't created a career roadmap yet. Go to Career Navigator to create one!")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Create Career Roadmap", use_container_width=True):
                    st.switch_page("pages/6_🧭_Career_Navigator.py")

# Footer
st.sidebar.markdown("---")

# Add profile update section in sidebar
if st.session_state.profile_completed:
    st.sidebar.markdown("<h3 style='color: white;'>Update Your Profile</h3>", unsafe_allow_html=True)
    
    # Current Role
    current_role = st.sidebar.text_input(
        "Current Role", 
        value=st.session_state.user_context.get("user_role", ""),
        key="sidebar_current_role"
    )
    
    # Target Role (new field)
    target_role = st.sidebar.text_input(
        "Target Role", 
        value=st.session_state.user_context.get("target_role", ""),
        key="sidebar_target_role"
    )
    
    # Experience
    experience = st.sidebar.text_input(
        "Years of Experience", 
        value=st.session_state.user_context.get("experience", ""),
        key="sidebar_experience"
    )
    
    # Skills
    skills_text = ", ".join(st.session_state.user_context.get("skills", []))
    skills = st.sidebar.text_area(
        "Skills (comma-separated)",
        value=skills_text,
        key="sidebar_skills"
    )
    
    # Interests
    interests_text = ", ".join(st.session_state.user_context.get("interests", []))
    interests = st.sidebar.text_area(
        "Interests (comma-separated)",
        value=interests_text,
        key="sidebar_interests"
    )
    
    # Resume upload to extract skills
    st.sidebar.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='color:#e2e8f0; font-size:0.9rem;'>Or extract skills from your resume:</p>", unsafe_allow_html=True)

    # Custom styled resume uploader for sidebar
    st.sidebar.markdown("""
    <style>
    .sidebar-upload {
        background-color: #3c4758;
        border: 1px dashed #4299e1;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sidebar-upload-icon {
        font-size: 1.5rem;
        color: #4299e1;
        margin-bottom: 0.5rem;
    }
    .sidebar-upload-text {
        color: #e2e8f0;
        font-size: 0.85rem;
    }
    </style>

    <div class="sidebar-upload">
        <div class="sidebar-upload-icon">📄</div>
        <div class="sidebar-upload-text">Upload your resume</div>
    </div>
    """, unsafe_allow_html=True)

    sidebar_resume = st.sidebar.file_uploader(
        "Upload Resume", 
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
        key="sidebar_resume_upload"
    )
    
    # Process resume if uploaded
    if sidebar_resume:
        # Create a placeholder for status messages
        sidebar_status = st.sidebar.empty()
        sidebar_status.info("Extracting information...")
        
        # Save uploaded file temporarily
        temp_path = f"temp_sidebar_{sidebar_resume.name}"
        with open(temp_path, "wb") as f:
            f.write(sidebar_resume.getvalue())
        
        try:
            # Analyze resume
            analyzer = agents["resume_analyzer"]
            analysis = analyzer.process_resume(temp_path)
            
            # Extract skills and other information
            extracted_skills = [skill['name'] for skill in analysis["structured_data"].get("skills", [])]
            extracted_experience = next(
                (exp for exp in analysis["structured_data"].get("work_experience", [])
                if "years" in exp.lower()),
                st.session_state.user_context.get("experience", "")
            )
            extracted_current_role = analysis["structured_data"].get("user_role", 
                                                                     st.session_state.user_context.get("user_role", ""))
            
            # Update form fields
            skills = ", ".join(extracted_skills)
            experience = extracted_experience
            current_role = extracted_current_role
            
            # Ensure user has a unique ID
            if "user_id" not in st.session_state.user_context:
                import uuid
                st.session_state.user_context["user_id"] = str(uuid.uuid4())
                print(f"Generated new user ID from sidebar resume upload: {st.session_state.user_context['user_id']}")
            
            # Update status message
            sidebar_status.success("✅ Information extracted! Click 'Save Profile Updates' to apply changes.")
            
        except Exception as e:
            # Update status message with error
            sidebar_status.error(f"Error analyzing resume: {str(e)}")
        
        finally:
            # Cleanup temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    # Save button
    if st.sidebar.button("Save Profile Updates", use_container_width=True):
        # Update session state
        st.session_state.user_context["user_role"] = current_role
        st.session_state.user_context["target_role"] = target_role
        st.session_state.user_context["experience"] = experience
        st.session_state.user_context["skills"] = [skill.strip() for skill in skills.split(",") if skill.strip()]
        st.session_state.user_context["interests"] = [interest.strip() for interest in interests.split(",") if interest.strip()]
        
        # Ensure user has a unique ID
        if "user_id" not in st.session_state.user_context:
            import uuid
            st.session_state.user_context["user_id"] = str(uuid.uuid4())
            print(f"Generated new user ID from sidebar: {st.session_state.user_context['user_id']}")
        
        # Log activity
        update_user_activity("profile", "Updated profile information")
        
        # Save state
        save_success = save_current_state()
        if save_success:
            st.sidebar.success("Profile updated and saved successfully!")
            print("Profile data saved successfully to database from sidebar")
        else:
            st.sidebar.warning("Profile updated but there was an issue saving your data.")
            print("Failed to save profile data to database from sidebar")
        
        time.sleep(1)
        st.rerun()

# Add Resume Analyzer direct link
# Removed from sidebar to hide it completely

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="color: white;">
    Made with ❤️ using:
    <ul style="color: #e2e8f0;">
        <li>Streamlit</li>
        <li>LangChain</li>
        <li>OpenAI</li>
        <li>Adzuna API</li>
    </ul>
    </div>
    """, 
    unsafe_allow_html=True
)

if __name__ == "__main__":
    # Validate configuration
    Config.validate_config()
    
    # Run the app
    main() 