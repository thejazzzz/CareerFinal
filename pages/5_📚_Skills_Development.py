import streamlit as st
from agents.skills_advisor import SkillsAdvisorAgent
from datetime import datetime

# Initialize the skills advisor agent
@st.cache_resource
def get_skills_advisor():
    return SkillsAdvisorAgent(verbose=True)

def initialize_session_state():
    """Initialize required session state variables"""
    if "user_context" not in st.session_state:
        st.session_state.user_context = {
            "current_role": "",
            "experience": "",
            "skills": [],
            "interests": [],
            "career_goals": ""
        }
    if "skill_progress" not in st.session_state:
        st.session_state.skill_progress = {}

def main():
    st.title("📚 Skills Development")
    
    # Initialize session state and agent
    initialize_session_state()
    advisor = get_skills_advisor()
    
    # Check if profile is completed
    if not any(st.session_state.user_context.values()):
        st.warning("Please complete your profile in the home page first!")
        st.write("Go to the home page and fill out your profile information to get personalized skill recommendations.")
        return
    
    st.write("""
    Develop your professional skills with personalized learning paths and recommendations.
    Track your progress and get guidance on which skills to focus on next.
    """)
    
    # Skill analysis section
    st.header("Skill Gap Analysis")
    
    with st.form("skill_analysis_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            current_skills = st.multiselect(
                "Your Current Skills",
                options=st.session_state.user_context.get("skills", []) + [
                    "Problem Solving", "Communication", "Leadership",
                    "Technical Skills", "Project Management"
                ],
                default=st.session_state.user_context.get("skills", [])
            )
            
            target_role = st.text_input(
                "Target Role",
                value=st.session_state.user_context.get("career_goals", "").split("\n")[0] if st.session_state.user_context.get("career_goals") else ""
            )
        
        with col2:
            job_requirements = st.text_area(
                "Job Requirements (Optional)",
                help="Paste specific job requirements to get more targeted recommendations"
            )
        
        analyze_button = st.form_submit_button("Analyze Skills")
    
    # Process skill analysis
    if analyze_button:
        if not target_role:
            st.error("Please enter a target role for skill analysis.")
            return
            
        with st.spinner("Analyzing skill gaps..."):
            try:
                # Convert job requirements to list if provided
                requirements_list = [req.strip() for req in job_requirements.split("\n") if req.strip()] if job_requirements else []
                
                # Get skill gap analysis
                analysis = advisor.analyze_skill_gaps(
                    current_skills=current_skills,
                    target_role=target_role,
                    job_requirements=requirements_list
                )
                
                # Display results
                if "structured_data" in analysis:
                    st.success("Skill analysis complete!")
                    
                    # Create two columns for the display
                    col3, col4 = st.columns(2)
                    
                    with col3:
                        # Skill Gaps
                        st.subheader("🔍 Skill Gaps")
                        gaps = analysis["structured_data"]["skill_gaps"]
                        if gaps:
                            for gap in gaps:
                                st.warning(f"⚠️ {gap}")
                        else:
                            st.info("No significant skill gaps identified.")
                        
                        # Priority Skills
                        st.subheader("🎯 Priority Skills to Develop")
                        priorities = analysis["structured_data"]["priority_skills"]
                        if priorities:
                            for skill in priorities:
                                st.info(f"📈 {skill}")
                        else:
                            st.info("No priority skills identified.")
                    
                    with col4:
                        # Learning Resources
                        st.subheader("📚 Learning Resources")
                        resources = analysis["structured_data"]["learning_resources"]
                        if resources:
                            for resource in resources:
                                st.write(f"• {resource}")
                        else:
                            st.info("No specific resources recommended.")
                        
                        # Career Transition Strategy
                        st.subheader("🔄 Career Transition Strategy")
                        strategies = analysis["structured_data"]["transition_strategy"]
                        if strategies:
                            for strategy in strategies:
                                st.write(f"• {strategy}")
                        else:
                            st.info("No specific transition strategy provided.")
                    
                    # Add a separator before the learning path section
                    st.markdown("---")
                
                else:
                    st.error("Failed to generate structured analysis.")
                
            except Exception as e:
                st.error(f"Error analyzing skills: {str(e)}")
                if st.checkbox("Show detailed error"):
                    st.exception(e)
    
    # Learning path section
    st.header("Create Learning Path")
    
    with st.form("learning_path_form"):
        col5, col6 = st.columns(2)
        
        with col5:
            skill_to_learn = st.selectbox(
                "Select Skill to Develop",
                options=[""] + (analysis["structured_data"]["priority_skills"] if 'analysis' in locals() else []) + [
                    "Python Programming", "Data Analysis", "Machine Learning",
                    "Project Management", "Leadership", "Communication"
                ]
            )
            
            current_level = st.selectbox(
                "Current Level",
                ["beginner", "intermediate", "advanced", "expert"]
            )
        
        with col6:
            target_level = st.selectbox(
                "Target Level",
                ["intermediate", "advanced", "expert"],
                index=1
            )
        
        create_path_button = st.form_submit_button("Create Learning Path")
    
    # Generate learning path
    if create_path_button:
        if not skill_to_learn:
            st.error("Please select a skill to develop.")
            return
            
        with st.spinner("Creating learning path..."):
            try:
                # Get learning path
                learning_path = advisor.create_learning_path(
                    skill=skill_to_learn,
                    current_level=current_level,
                    target_level=target_level
                )
                
                # Validate response structure
                if "structured_data" not in learning_path:
                    st.error("Invalid response format! 'structured_data' missing.")
                    st.stop()
                
                required_sections = ["objectives", "resources", "timeline", "exercises", "assessment"]
                missing_sections = [
                    section for section in required_sections 
                    if section not in learning_path["structured_data"]
                ]
                
                if missing_sections:
                    st.error(f"Missing sections in learning path: {', '.join(missing_sections)}")
                    st.stop()
                
                # Store in session state
                st.session_state["current_learning_path"] = learning_path
                
                # Display learning path
                st.success(f"Learning path created for {skill_to_learn}!")
                
                # Learning objectives with validation
                st.subheader("🎯 Learning Objectives")
                objectives = learning_path["structured_data"]["objectives"]
                if objectives:
                    for obj in objectives:
                        st.write(f"• {obj}")
                else:
                    st.warning("No learning objectives found.")
                st.divider()
                
                # Resources and timeline
                col7, col8 = st.columns(2)
                
                with col7:
                    st.subheader("📚 Recommended Resources")
                    resources = learning_path["structured_data"]["resources"]
                    if resources:
                        for resource in resources:
                            with st.expander(f"Resource: {resource.split(':')[0] if ':' in resource else resource}"):
                                st.write(resource)
                    else:
                        st.warning("No resources found.")
                    
                    st.subheader("✍️ Practice Exercises")
                    exercises = learning_path["structured_data"]["exercises"]
                    if exercises:
                        for i, exercise in enumerate(exercises, 1):
                            st.write(f"{i}. {exercise}")
                    else:
                        st.warning("No practice exercises found.")
                
                with col8:
                    st.subheader("⏱️ Timeline and Milestones")
                    timeline = learning_path["structured_data"]["timeline"]
                    if timeline:
                        for milestone in timeline:
                            st.info(milestone)
                    else:
                        st.warning("No timeline found.")
                    
                    st.subheader("📋 Assessment Criteria")
                    assessment = learning_path["structured_data"]["assessment"]
                    if assessment:
                        for criterion in assessment:
                            st.success(criterion)
                    else:
                        st.warning("No assessment criteria found.")
                
                # After displaying the learning path content
                if st.button("Track This Skill"):
                    try:
                        # Create a new skill progress entry
                        new_skill_progress = {
                            "skill_name": skill_to_learn,
                            "current_level": current_level,
                            "target_level": target_level,
                            "start_date": datetime.now().strftime("%Y-%m-%d"),
                            "learning_path": learning_path["structured_data"],
                            "completed_objectives": [],
                            "progress_percentage": 0
                        }
                        
                        # Initialize skill_progress if it doesn't exist
                        if "skill_progress" not in st.session_state:
                            st.session_state.skill_progress = {}
                        
                        # Add or update the skill progress
                        st.session_state.skill_progress[skill_to_learn] = new_skill_progress
                        
                        # Force a rerun to update the display
                        st.rerun()
            
                    except Exception as e:
                        st.error(f"Error tracking skill: {str(e)}")
                        if st.checkbox("Show detailed error"):
                            st.exception(e)
            
            except Exception as e:
                st.error(f"Error creating learning path: {str(e)}")
                st.write("Detailed error information:")
                st.exception(e)
    
    # Move the progress tracking section outside of the if create_path_button block
    if st.session_state.get("skill_progress"):
        st.markdown("---")
        st.header("🎯 Your Tracked Skills")
        
        for skill, progress in st.session_state.skill_progress.items():
            with st.expander(f"{skill} - {progress['current_level']} → {progress['target_level']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Started:** {progress['start_date']}")
                    st.markdown(f"**Current Level:** {progress['current_level']}")
                    st.markdown(f"**Target Level:** {progress['target_level']}")
                
                with col2:
                    # Progress tracking
                    completed = st.multiselect(
                        "Completed Objectives",
                        options=progress["learning_path"]["objectives"],
                        default=progress.get("completed_objectives", []),
                        key=f"tracked_objectives_{skill}"
                    )
                    
                    # Update progress
                    progress["completed_objectives"] = completed
                    progress_percentage = (len(completed) / len(progress["learning_path"]["objectives"])) * 100
                    progress["progress_percentage"] = progress_percentage
                    
                    # Display progress
                    st.progress(progress_percentage)
                    st.metric("Progress", f"{progress_percentage:.1f}%")
                
                # Display remaining objectives
                remaining = [obj for obj in progress["learning_path"]["objectives"] 
                           if obj not in completed]
                if remaining:
                    st.markdown("**Next Objectives:**")
                    for obj in remaining[:3]:
                        st.info(f"• {obj}")
                
                # Option to remove tracking
                if st.button("Stop Tracking", key=f"remove_{skill}"):
                    del st.session_state.skill_progress[skill]
                    st.rerun()

if __name__ == "__main__":
    main() 