import streamlit as st
from agents.skills_advisor import SkillsAdvisorAgent
from datetime import datetime
import os
import uuid

# Initialize the skills advisor agent
@st.cache_resource
def get_skills_advisor():
    user_data_path = os.path.join("data", "user_skills")
    return SkillsAdvisorAgent(verbose=True, user_data_path=user_data_path)

def initialize_session_state():
    """Initialize required session state variables"""
    if "user_context" not in st.session_state:
        st.session_state.user_context = {
            "user_id": str(uuid.uuid4()),  # Generate unique user ID
            "name": "",
            "current_role": "",
            "experience": "",
            "skills": [],
            "interests": [],
            "career_goals": ""
        }
    
    if "skill_progress" not in st.session_state:
        st.session_state.skill_progress = {}
    
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "analysis"
    
    if "learning_paths" not in st.session_state:
        st.session_state.learning_paths = {}
    
    if "selected_learning_path" not in st.session_state:
        st.session_state.selected_learning_path = None

def main():
    st.title("📚 Skills Development")
    
    # Initialize session state and agent
    initialize_session_state()
    advisor = get_skills_advisor()
    
    # Set user profile in advisor
    advisor.set_user_profile(st.session_state.user_context)
    
    # Create tabs
    tabs = ["Skill Analysis", "Learning Paths", "Progress Tracking"]
    active_tab = st.radio("Navigation", tabs, horizontal=True)
    
    if active_tab == "Skill Analysis":
        display_skill_analysis_tab(advisor)
    elif active_tab == "Learning Paths":
        display_learning_paths_tab(advisor)
    else:
        display_progress_tracking_tab(advisor)

def display_skill_analysis_tab(advisor):
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

def display_learning_paths_tab(advisor):
    st.header("Create Learning Path")
    
    # Initialize session state variables if they don't exist
    if "current_learning_path" not in st.session_state:
        st.session_state.current_learning_path = None
    
    if "skill_progress" not in st.session_state:
        st.session_state.skill_progress = {}
    
    # Check if analysis has been performed
    analysis_available = "last_analysis" in st.session_state
    
    # Get priority skills from analysis if available
    priority_skills = []
    if analysis_available and "structured_data" in st.session_state.last_analysis:
        analysis = st.session_state.last_analysis
        if "priority_skills" in analysis["structured_data"]:
            priority_skills = analysis["structured_data"]["priority_skills"]
    
    # Default skills if none are available from analysis
    default_skills = [
        "Python Programming", "Data Analysis", "Machine Learning",
        "Project Management", "Leadership", "Communication"
    ]
    
    # Combine skills for selection
    all_skills = priority_skills + [skill for skill in default_skills if skill not in priority_skills]
    
    with st.form("learning_path_form"):
        col5, col6 = st.columns(2)
        
        with col5:
            skill_to_learn = st.selectbox(
                "Select Skill to Develop",
                options=[""] + all_skills
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
                
                # Check for error in response
                if "error" in learning_path:
                    st.error(f"Error creating learning path: {learning_path['error']}")
                    st.info("Using default learning path instead.")
                
                # Validate response structure
                if "structured_data" not in learning_path:
                    st.error("Invalid response format! 'structured_data' missing.")
                    st.stop()
                
                # Store in session state
                st.session_state.current_learning_path = learning_path
                
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
                        
                        # Add or update the skill progress
                        st.session_state.skill_progress[skill_to_learn] = new_skill_progress
                        
                        st.success(f"Now tracking progress for {skill_to_learn}!")
                        
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
    
    # Display current learning path if available
    elif st.session_state.current_learning_path is not None:
        learning_path = st.session_state.current_learning_path
        skill_to_learn = learning_path.get("skill", "Unknown Skill")
        
        st.success(f"Current learning path: {skill_to_learn}")
        
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
        
        # Track This Skill button for current learning path
        if st.button("Track This Skill"):
            try:
                # Create a new skill progress entry
                new_skill_progress = {
                    "skill_name": skill_to_learn,
                    "current_level": learning_path.get("current_level", "beginner"),
                    "target_level": learning_path.get("target_level", "advanced"),
                    "start_date": datetime.now().strftime("%Y-%m-%d"),
                    "learning_path": learning_path["structured_data"],
                    "completed_objectives": [],
                    "progress_percentage": 0
                }
                
                # Add or update the skill progress
                st.session_state.skill_progress[skill_to_learn] = new_skill_progress
                
                st.success(f"Now tracking progress for {skill_to_learn}!")
                
                # Force a rerun to update the display
                st.rerun()
        
            except Exception as e:
                st.error(f"Error tracking skill: {str(e)}")
                if st.checkbox("Show detailed error"):
                    st.exception(e)
    
    # Display tracked skills section
    if st.session_state.skill_progress:
        st.markdown("---")
        st.header("🎯 Your Tracked Skills")
        
        for skill_name, progress_data in st.session_state.skill_progress.items():
            with st.expander(f"{skill_name} ({progress_data['current_level']} → {progress_data['target_level']})"):
                st.write(f"**Started:** {progress_data['start_date']}")
                
                # Calculate and display progress
                total_objectives = len(progress_data['learning_path']['objectives'])
                completed = len(progress_data.get('completed_objectives', []))
                progress_percentage = int((completed / total_objectives) * 100) if total_objectives > 0 else 0
                
                # Update progress percentage
                progress_data['progress_percentage'] = progress_percentage
                
                # Display progress bar
                st.progress(progress_percentage / 100)
                st.write(f"**Progress:** {progress_percentage}% ({completed}/{total_objectives} objectives completed)")
                
                # Objectives with checkboxes
                st.subheader("Learning Objectives")
                
                # Create a unique key for each objective
                for i, objective in enumerate(progress_data['learning_path']['objectives']):
                    obj_key = f"{skill_name}_obj_{i}"
                    is_completed = objective in progress_data.get('completed_objectives', [])
                    
                    # Create a checkbox for each objective
                    if st.checkbox(objective, value=is_completed, key=obj_key):
                        if objective not in progress_data.get('completed_objectives', []):
                            if 'completed_objectives' not in progress_data:
                                progress_data['completed_objectives'] = []
                            progress_data['completed_objectives'].append(objective)
                    else:
                        if objective in progress_data.get('completed_objectives', []):
                            progress_data['completed_objectives'].remove(objective)
                
                # Resources section
                st.subheader("Resources")
                for resource in progress_data['learning_path']['resources'][:3]:  # Show first 3 resources
                    st.write(f"• {resource}")
                
                # Stop tracking button
                if st.button("Stop Tracking", key=f"stop_{skill_name}"):
                    del st.session_state.skill_progress[skill_name]
                    st.success(f"Stopped tracking {skill_name}")
                    st.rerun()

def display_progress_tracking_tab(advisor):
    st.header("Progress Tracking")
    
    # Initialize user ID if not already set
    if "user_context" not in st.session_state or "user_id" not in st.session_state.user_context:
        st.session_state.user_context = {
            "user_id": str(uuid.uuid4()),
            "name": "",
            "current_role": "",
            "experience": "",
            "skills": [],
            "interests": [],
            "career_goals": ""
        }
    
    user_id = st.session_state.user_context["user_id"]
    
    # Combine session-based and disk-based learning paths
    session_paths = []
    if st.session_state.get("skill_progress"):
        for skill_name, progress_data in st.session_state.skill_progress.items():
            # Convert session format to disk format
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            path_id = f"{skill_name}_{timestamp}"
            
            session_paths.append({
                "id": path_id,
                "skill": skill_name,
                "current_level": progress_data.get("current_level", "beginner"),
                "target_level": progress_data.get("target_level", "advanced"),
                "created_at": progress_data.get("start_date", datetime.now().strftime("%Y-%m-%d")),
                "structured_data": progress_data.get("learning_path", {}),
                "progress": {
                    "status": "active",
                    "completed_objectives": progress_data.get("completed_objectives", []),
                    "completed_resources": [],
                    "completed_exercises": [],
                    "progress_percentage": progress_data.get("progress_percentage", 0),
                    "last_updated": datetime.now().isoformat(),
                    "notes": [],
                    "time_spent_hours": 0
                }
            })
    
    # Get disk-based learning paths
    disk_paths = advisor.get_user_learning_paths(user_id)
    
    # Combine paths, prioritizing disk paths if there are duplicates
    disk_path_skills = {path["skill"] for path in disk_paths}
    combined_paths = disk_paths + [path for path in session_paths if path["skill"] not in disk_path_skills]
    
    if not combined_paths:
        st.info("No active learning paths. Create a learning path to start tracking progress!")
        return
    
    # Display learning path selection
    path_options = {f"{path['skill']} ({path['current_level']} → {path['target_level']})": path["id"] for path in combined_paths}
    selected_path_display = st.selectbox(
        "Select Learning Path",
        options=list(path_options.keys())
    )
    
    if selected_path_display:
        selected_path_id = path_options[selected_path_display]
        path = next(p for p in combined_paths if p["id"] == selected_path_id)
        
        # Display progress
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Progress Overview")
            progress_percentage = path["progress"]["progress_percentage"]
            st.progress(progress_percentage / 100)
            st.metric("Overall Progress", f"{progress_percentage:.1f}%")
            
            # Time tracking
            time_spent = st.number_input(
                "Additional hours spent",
                min_value=0.0,
                step=0.5,
                value=0.0
            )
            
            # User reflection
            user_notes = st.text_area("Reflection Notes", help="Share your thoughts on your progress")
        
        with col2:
            st.subheader("Completed Items")
            # Display completion checkboxes for objectives
            completed_objectives = st.multiselect(
                "Learning Objectives",
                options=path["structured_data"].get("objectives", []),
                default=path["progress"].get("completed_objectives", [])
            )
            
            # Display completion checkboxes for resources
            completed_resources = st.multiselect(
                "Resources",
                options=path["structured_data"].get("resources", []),
                default=path["progress"].get("completed_resources", [])
            )
            
            # Display completion checkboxes for exercises
            completed_exercises = st.multiselect(
                "Exercises",
                options=path["structured_data"].get("exercises", []),
                default=path["progress"].get("completed_exercises", [])
            )
        
        # Update progress button
        if st.button("Update Progress"):
            try:
                # Update progress in the advisor
                updated_path = advisor.update_skill_progress(
                    learning_path_id=path["id"],
                    completed_objectives=completed_objectives,
                    completed_resources=completed_resources,
                    completed_exercises=completed_exercises,
                    time_spent_hours=time_spent,
                    user_notes=user_notes,
                    user_id=user_id
                )
                
                # Also update session state if this is a session-based path
                if path["skill"] in st.session_state.get("skill_progress", {}):
                    st.session_state.skill_progress[path["skill"]]["completed_objectives"] = completed_objectives
                    st.session_state.skill_progress[path["skill"]]["progress_percentage"] = updated_path["progress"]["progress_percentage"]
                
                st.success("Progress updated successfully!")
                
                # Get assessment feedback
                assessment = advisor.assess_progress(
                    learning_path_id=path["id"],
                    user_reflection=user_notes,
                    user_id=user_id
                )
                
                # Display assessment feedback
                st.subheader("Progress Assessment")
                
                # Display feedback messages
                for feedback in assessment["feedback"]:
                    st.info(feedback)
                
                # Display next steps
                st.subheader("Recommended Next Steps")
                for step in assessment["next_steps"]:
                    st.success(step)
                
                # Display section completion metrics
                st.subheader("Section Completion")
                col3, col4, col5 = st.columns(3)
                
                with col3:
                    st.metric("Objectives", f"{assessment['objectives_completion']:.1f}%")
                
                with col4:
                    st.metric("Resources", f"{assessment['resources_completion']:.1f}%")
                
                with col5:
                    st.metric("Exercises", f"{assessment['exercises_completion']:.1f}%")
                
            except Exception as e:
                st.error(f"Error updating progress: {str(e)}")
                if st.checkbox("Show detailed error"):
                    st.exception(e)

if __name__ == "__main__":
    main() 