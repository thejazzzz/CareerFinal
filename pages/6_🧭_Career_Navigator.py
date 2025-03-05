import streamlit as st
from agents.career_navigator import CareerNavigatorAgent

# Initialize the career navigator agent
@st.cache_resource
def get_career_navigator():
    return CareerNavigatorAgent(verbose=True)

def initialize_session_state():
    """Initialize required session state variables"""
    if "user_context" not in st.session_state:
        st.session_state.user_context = {
            "current_role": "",
            "experience": "",
            "skills": [],
            "interests": [],
            "career_goals": "",
            "activities": []
        }
    
    if "career_path" not in st.session_state:
        st.session_state.career_path = None
    
    if "saved_career_plans" not in st.session_state:
        st.session_state.saved_career_plans = []

def main():
    # Initialize session state first
    initialize_session_state()
    
    st.title("🧭 Career Navigator")
    
    # Initialize the agent
    navigator = get_career_navigator()
    
    # Check if user context exists and has any values
    if not any(st.session_state.user_context.values()):
        st.warning("Please complete your profile in the home page first!")
        st.write("Go to the home page and fill out your profile information to get personalized career guidance.")
        return
    
    st.write("""
    Plan your career journey with our AI-powered Career Navigator.
    Get personalized career paths, industry insights, and transition strategies
    based on your experience, skills, and goals.
    """)
    
    # Career planning form
    with st.form("career_planning_form"):
        # Current status
        st.header("Current Status")
        current_role = st.text_input(
            "Current Role",
            value=st.session_state.user_context.get("current_role", "")
        )
        experience = st.text_input(
            "Years of Experience",
            value=st.session_state.user_context.get("experience", "")
        )
        
        # Skills and interests
        skills = st.multiselect(
            "Key Skills",
            options=st.session_state.user_context.get("skills", []) + [
                "Leadership", "Project Management", "Strategy", "Communication",
                "Problem Solving", "Analytics", "Innovation"
            ],
            default=st.session_state.user_context.get("skills", [])
        )
        
        interests = st.multiselect(
            "Professional Interests",
            options=st.session_state.user_context.get("interests", []) + [
                "Technology", "Data Science", "Product Management",
                "Consulting", "Research", "Design", "Business Development"
            ],
            default=st.session_state.user_context.get("interests", [])
        )
        
        # Career goals
        st.header("Career Goals")
        goals = st.text_area(
            "What are your career goals?",
            value=st.session_state.user_context.get("career_goals", ""),
            help="Enter each goal on a new line"
        ).split("\n")
        
        # Industry preferences
        industry = st.selectbox(
            "Target Industry",
            ["Technology", "Finance", "Healthcare", "Education", "Manufacturing",
             "Retail", "Consulting", "Entertainment", "Energy", "Other"]
        )
        
        # Submit button
        plan_button = st.form_submit_button("Create Career Plan")
    
    # Generate career plan
    if plan_button:
        with st.spinner("Creating your career plan..."):
            try:
                # Get career path analysis
                career_path = navigator.create_career_path(
                    current_role=current_role,
                    experience=experience,
                    skills=skills,
                    interests=interests,
                    goals=goals
                )
                
                # Store in session state
                st.session_state.career_path = career_path
                
                # Display results
                st.success("Career Plan Created!")
                
                # Career paths
                st.header("Potential Career Paths")
                for i, path in enumerate(career_path["structured_data"]["path_options"], 1):
                    st.subheader(f"Path {i}: {path}")
                    
                    # Analyze role for each path
                    role_analysis = navigator.analyze_role(
                        target_role=path,
                        industry=industry
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Role Overview:**")
                        for item in role_analysis["structured_data"]["overview"]:
                            st.write(f"• {item}")
                        
                        st.write("**Required Skills:**")
                        for item in role_analysis["structured_data"]["requirements"]:
                            st.write(f"• {item}")
                    
                    with col2:
                        st.write("**Industry Outlook:**")
                        for item in role_analysis["structured_data"]["outlook"]:
                            st.write(f"• {item}")
                        
                        st.write("**Salary Range:**")
                        for item in role_analysis["structured_data"]["salary"]:
                            st.write(f"• {item}")
                    
                    # Display key companies for this path
                    st.write(f"**Key Companies for {path} in {industry}:**")
                    company_cols = st.columns(3)
                    for j, company in enumerate(role_analysis["structured_data"]["companies"]):
                        with company_cols[j % 3]:
                            st.write(f"• {company}")
                    
                    st.divider()  # Add a visual separator between paths
                
                # Timeline
                st.header("Career Development Timeline")
                for i, milestone in enumerate(career_path["structured_data"]["timeline"], 1):
                    st.write(f"{i}. {milestone}")
                
                # Challenges and solutions
                col3, col4 = st.columns(2)
                
                with col3:
                    st.header("Potential Challenges")
                    for challenge in career_path["structured_data"]["challenges"]:
                        st.warning(challenge)
                
                with col4:
                    st.header("Industry Trends")
                    for trend in career_path["structured_data"]["trends"]:
                        st.info(trend)
                
                # Save career plan
                if st.button("Save Career Plan"):
                    if "saved_career_plans" not in st.session_state:
                        st.session_state.saved_career_plans = []
                    st.session_state.saved_career_plans.append({
                        "path": career_path,
                        "industry": industry,
                        "date": st.session_state.get("current_date", "Today")
                    })
                    st.success("Career plan saved to your profile!")
            
            except Exception as e:
                st.error(f"Error creating career plan: {str(e)}")
    
    # Saved plans in sidebar
    with st.sidebar:
        if "saved_career_plans" in st.session_state and st.session_state.saved_career_plans:
            st.header("Saved Career Plans")
            for plan in st.session_state.saved_career_plans:
                with st.expander(f"Plan for {plan['industry']} - {plan['date']}"):
                    st.write("**Career Paths:**")
                    for path in plan["path"]["structured_data"]["path_options"]:
                        st.write(f"• {path}")
                    if st.button("Remove", key=f"remove_{st.session_state.saved_career_plans.index(plan)}"):
                        st.session_state.saved_career_plans.remove(plan)
                        st.rerun()

if __name__ == "__main__":
    main() 