import streamlit as st
from agents.career_navigator import CareerNavigatorAgent
from datetime import datetime

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
    
    # Define plan_button variable with default value
    plan_button = False
    
    # Display existing career path if it exists in session state
    if st.session_state.get("career_path"):
        career_path = st.session_state.career_path
        
        st.success("Your Career Roadmap is Ready!")
        
        # Display basic information at the top
        st.header("Your Career Path Overview")
        
        if isinstance(career_path, dict):
            # Current and target state
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Current State")
                st.info(career_path.get("current_state", "Not specified"))
            
            with col2:
                st.subheader("Target State")
                st.info(career_path.get("target_state", "Not specified"))
            
            # Milestones with direct display (no dropdowns)
            if "milestones" in career_path and career_path["milestones"]:
                st.subheader("Career Milestones")
                for i, milestone in enumerate(career_path["milestones"]):
                    # Extract title and description for each milestone
                    milestone_title = milestone.get('title', f'Milestone {i+1}')
                    milestone_description = milestone.get('description', 'No description available')
                    
                    # Clean up the milestone title and description
                    # Remove "Milestone X" from title
                    title = milestone_title
                    if "milestone" in title.lower() and any(char.isdigit() for char in title):
                        title = " ".join([word for word in title.split() if not (word.lower() == "milestone" or word.isdigit())])
                    
                    # Extract time period indicators but keep them as bold headers
                    time_period = ""
                    time_periods = {"short-term": "Short-term (0-2 years)", 
                                   "medium-term": "Medium-term (2-5 years)", 
                                   "long-term": "Long-term (5+ years)"}
                    
                    for period_key, period_text in time_periods.items():
                        if period_key in title.lower():
                            time_period = period_text
                            title = ""
                    
                    # Remove any HTML tags from milestone description if present
                    clean_description = milestone_description
                    if "<p" in clean_description and "</p>" in clean_description:
                        # Extract text between HTML tags
                        import re
                        clean_description = re.sub(r'<[^>]*>', '', clean_description)
                    
                    # Display as styled divs similar to app.py
                    st.markdown(f"""
                    <div style="
                        background-color: #3c4758;
                        border-radius: 8px;
                        padding: 1rem;
                        margin-bottom: 0.75rem;
                        border-left: 3px solid #4299e1;
                    ">
                        {f'<p style="color: white; font-weight: 600; margin-bottom: 0.5rem;">{time_period}</p>' if time_period else ''}
                        <p style="color: #e2e8f0;">{clean_description}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # If we also have structured data from career navigation
            if "structured_data" in career_path:
                # Display paths
                st.header("🎯 Potential Career Paths")
                structured_data = career_path.get("structured_data", {})
                
                # Path options
                path_options = structured_data.get("path_options", [])
                if path_options and path_options[0] != "Career path information not available":
                    for i, path in enumerate(path_options, 1):
                        st.subheader(f"Path {i}: {path}")
                
                # Display challenges and solutions
                challenges = structured_data.get("challenges", [])
                solutions = structured_data.get("solutions", [])
                
                if challenges and solutions and challenges[0] != "Challenge information not available":
                    st.header("🔄 Challenges and Solutions")
                    for challenge, solution in zip(challenges, solutions):
                        with st.expander(f"Challenge: {challenge}"):
                            st.write("**Solution:**")
                            st.write(solution)
                
                # Display trends
                trends = structured_data.get("trends", [])
                if trends and trends[0] != "Industry trend information not available":
                    st.header("📈 Industry Trends")
                    for trend in trends:
                        st.success(trend)
                
                # Skills section
                skills_data = structured_data.get("required_skills", {})
                if skills_data:
                    st.header("🔧 Required Skills")
                    
                    # Technical skills
                    tech_skills = skills_data.get("technical", [])
                    if tech_skills and tech_skills[0] != "Technical skills information not available":
                        st.subheader("Technical Skills")
                        for skill in tech_skills:
                            st.write(f"• {skill}")
                    
                    # Soft skills
                    soft_skills = skills_data.get("soft", [])
                    if soft_skills and soft_skills[0] != "Soft skills information not available":
                        st.subheader("Soft Skills")
                        for skill in soft_skills:
                            st.write(f"• {skill}")
                    
                    # Certifications
                    certifications = skills_data.get("certifications", [])
                    if certifications and certifications[0] != "Certification information not available":
                        st.subheader("Recommended Certifications")
                        for cert in certifications:
                            st.write(f"• {cert}")
            
            # Save current plan if not already saved
            save_col1, save_col2 = st.columns([1, 3])
            with save_col1:
                if st.button("Save This Career Plan"):
                    if "saved_career_plans" not in st.session_state:
                        st.session_state.saved_career_plans = []
                    
                    # Check if plan is already saved
                    already_saved = False
                    for plan in st.session_state.saved_career_plans:
                        if plan.get("path") == career_path:
                            already_saved = True
                            break
                    
                    if not already_saved:
                        st.session_state.saved_career_plans.append({
                            "path": career_path,
                            "industry": career_path.get("target_state", "").split("Industry: ")[1].split(" with")[0] if "Industry:" in career_path.get("target_state", "") else "Technology",
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        st.success("Career plan saved to your profile!")
                    else:
                        st.info("This plan is already saved to your profile.")
            
            with save_col2:
                if st.button("Create New Career Plan", use_container_width=True):
                    # Clear current plan to allow creating a new one
                    st.session_state.career_path = None
                    st.rerun()
        
        # Add a horizontal divider
        st.markdown("---")
    
    # Display the form to create a new career plan if none exists or user wants to create a new one
    if not st.session_state.get("career_path") or st.session_state.get("create_new_plan", False):
        st.write("""
        Plan your career journey with our AI-powered Career Navigator.
        Get personalized career paths, industry insights, and transition strategies
        based on your experience, skills, and goals.
        """)
    
        # Career planning form
        with st.form("career_plan_form"):
            # Current status
            st.header("Current Status")
            current_role = st.text_input(
                "Current Role",
                value=st.session_state.user_context.get("user_role", "")
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
                
                # Create formatted career path data that app.py expects
                formatted_career_path = {
                    "current_state": f"Current Role: {current_role} with {experience} years of experience",
                    "target_state": f"Target Industry: {industry} with focus on {', '.join([g for g in goals if g.strip()])[:3] if goals and any(g.strip() for g in goals) else 'career advancement'}",
                    "milestones": [],
                    "structured_data": career_path["structured_data"]
                }
                
                # Convert timeline entries to milestones
                for i, milestone in enumerate(career_path["structured_data"]["timeline"]):
                    milestone_title = f"Milestone {i+1}"
                    
                    # If the milestone text contains a title pattern like "Short-term:" or "Medium-term:"
                    # use that as the title
                    milestone_parts = milestone.split(":", 1)
                    if len(milestone_parts) > 1 and any(term in milestone_parts[0].lower() 
                                                    for term in ["short-term", "medium-term", "long-term"]):
                        milestone_title = milestone_parts[0].strip()
                        milestone_description = milestone_parts[1].strip()
                    else:
                        milestone_description = milestone
                    
                    formatted_career_path["milestones"].append({
                        "title": milestone_title,
                        "description": milestone_description
                    })
                
                # Store the reformatted career path in session state
                st.session_state.career_path = formatted_career_path
                
                # Add an activity record
                if "user_context" in st.session_state and "activities" in st.session_state.user_context:
                    from datetime import datetime
                    st.session_state.user_context["activities"].insert(0, {
                        "type": "Career Plan",
                        "description": f"Created career plan for {industry}",
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                
                # Rerun to show the new career path
                st.rerun()
                
                # The following code is now redundant and won't be executed after the rerun
                # But keeping it commented for reference
                """
                # Display results
                st.success("Career Plan Created!")
                
                # Career paths with improved display
                st.header("🎯 Potential Career Paths")
                for i, path in enumerate(career_path["structured_data"]["path_options"], 1):
                    # Extract just the path name without any "Path X:" prefix if it exists
                    if ":" in path:
                        # If the path already includes a label like "Path 1:", extract just the content after that
                        path_name = path.split(":", 1)[1].strip()
                    else:
                        path_name = path
                    
                    st.subheader(f"Path {i}: {path_name}")
                    
                    # Analyze role for each path
                    role_analysis = navigator.analyze_role(
                        target_role=path_name,  # Use the cleaned path name
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
                    
                    st.divider()
                
                # Timeline with improved display
                st.header("📅 Career Development Timeline")
                timeline = career_path["structured_data"]["timeline"]
                if timeline:
                    for milestone in timeline:
                        st.info(milestone)
                else:
                    st.warning("No timeline information available")
                
                # Challenges and Solutions with improved display
                st.header("🎯 Challenges and Solutions")
                challenges = career_path["structured_data"]["challenges"]
                solutions = career_path["structured_data"]["solutions"]
                if challenges and solutions:
                    for challenge, solution in zip(challenges, solutions):
                        with st.expander(f"Challenge: {challenge}"):
                            st.write("**Solution:**")
                            st.write(solution)
                else:
                    st.warning("No challenges and solutions available")
                
                # Industry Trends with improved display
                st.header("📈 Industry Trends")
                trends = career_path["structured_data"]["trends"]
                if trends:
                    for trend in trends:
                        st.success(trend)
                else:
                    st.warning("No industry trends available")
                
                # Required Skills with improved display
                st.header("🔧 Required Skills")
                skills_data = career_path["structured_data"]["required_skills"]
                
                # Display only technical skills in a single column
                st.subheader("Technical Skills")
                for skill in skills_data["technical"]:
                    if skill != "Technical skills information not available":
                        st.write(f"• {skill}")
                    else:
                        st.info("Technical skills information not available. Try creating a more specific career plan.")
                """
            
            except Exception as e:
                st.error(f"Error creating career plan: {str(e)}")
    
    # Saved plans section - move from sidebar to main content for better visibility
    if "saved_career_plans" in st.session_state and st.session_state.saved_career_plans:
        st.markdown("---")
        st.header("📋 Your Saved Career Plans")
        st.write("Click on a plan to view its details.")
        
        # Create a grid layout for saved plans
        cols = st.columns(3)
        for i, plan in enumerate(st.session_state.saved_career_plans):
            with cols[i % 3]:
                with st.container(border=True):
                    plan_industry = plan.get('industry', 'Unknown Industry')
                    plan_date = plan.get('date', 'Unknown Date')
                    
                    st.markdown(f"### {plan_industry}")
                    st.caption(f"Created: {plan_date}")
                    
                    # Show a preview of the paths
                    if "path" in plan and isinstance(plan["path"], dict):
                        # Show current/target state preview
                        if "current_state" in plan["path"]:
                            st.markdown(f"**From:** {plan['path']['current_state'][:30]}..." if len(plan['path']['current_state']) > 30 else f"**From:** {plan['path']['current_state']}")
                        
                        if "target_state" in plan["path"]:
                            st.markdown(f"**To:** {plan['path']['target_state'][:30]}..." if len(plan['path']['target_state']) > 30 else f"**To:** {plan['path']['target_state']}")
                        
                        # Show milestone preview
                        if "milestones" in plan["path"] and plan["path"]["milestones"]:
                            st.markdown("**Milestones:**")
                            for milestone in plan["path"]["milestones"][:1]:  # Show only first milestone
                                st.markdown(f"• {milestone.get('title', 'Milestone')}")
                            
                            if len(plan["path"]["milestones"]) > 1:
                                st.caption(f"+ {len(plan['path']['milestones']) - 1} more milestones")
                        
                        # Or show paths if structured data is available
                        elif "structured_data" in plan["path"] and plan["path"]["structured_data"]:
                            path_options = plan["path"]["structured_data"].get("path_options", [])
                            if path_options and path_options[0] != "Career path information not available":
                                st.markdown("**Career Paths:**")
                                for j, path in enumerate(path_options[:1]):  # Show only first path
                                    st.markdown(f"• {path[:40]}..." if len(path) > 40 else f"• {path}")
                                if len(path_options) > 1:
                                    st.caption(f"+ {len(path_options) - 1} more paths")
                    
                    # View/Load this plan button
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.button("View This Plan", key=f"view_{i}", use_container_width=True):
                            st.session_state.career_path = plan["path"]
                            st.rerun()
                    
                    with col2:
                        # Remove plan button
                        if st.button("❌", key=f"remove_{i}", help="Remove this plan"):
                            st.session_state.saved_career_plans.remove(plan)
                            st.rerun()
    
    # Add helpful tips in the sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Tips for Career Planning")
        st.info("Be specific about your goals and target industry to get the most relevant career advice.")
        st.markdown("### How It Works")
        st.markdown("""
        1. **Enter your current role** and experience
        2. **Select your skills** and interests
        3. **Set your career goals** and target industry
        4. Get a **personalized career roadmap**
        5. **Save multiple plans** to compare different paths
        """)

if __name__ == "__main__":
    main() 