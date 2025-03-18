import streamlit as st
from agents.skills_advisor import SkillsAdvisorAgent
from datetime import datetime
import os
import uuid
import json

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
        st.session_state.active_tab = "Skill Analysis"
    
    if "learning_paths" not in st.session_state:
        st.session_state.learning_paths = {}
    
    if "selected_learning_path" not in st.session_state:
        st.session_state.selected_learning_path = None
        
    if "skill_analysis_results" not in st.session_state:
        st.session_state.skill_analysis_results = None

def main():
    st.title("📚 Skills Development")
    
    # Initialize session state and agent
    initialize_session_state()
    advisor = get_skills_advisor()
    
    # Set user profile in advisor
    advisor.set_user_profile(st.session_state.user_context)
    
    # Create tabs - using session state to maintain selected tab
    tabs = ["Skill Analysis", "Learning Paths", "Progress Tracking"]
    
    # Get active tab from session state or use radio button
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Skill Analysis"
    
    # Radio button should reflect the active tab in session state
    active_tab = st.radio("Navigation", tabs, 
                         index=tabs.index(st.session_state.active_tab),
                         horizontal=True,
                         key="tab_navigation")
    
    # Update session state when radio button changes
    st.session_state.active_tab = active_tab
    
    # Display the content of the selected tab
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
                value=st.session_state.user_context.get("target_role", "") or 
                      (st.session_state.user_context.get("career_goals", "").split("\n")[0] 
                       if st.session_state.user_context.get("career_goals") else "")
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
                    job_requirements=requirements_list,
                    user_id=st.session_state.user_context.get("user_id")
                )
                
                # Store analysis in session state for use in learning paths tab
                st.session_state.skill_analysis_results = analysis
                
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
                    
                    # Add a button to navigate to Learning Paths tab
                    if st.button("Create Learning Paths for Priority Skills"):
                        # Update the session state variable
                        st.session_state.active_tab = "Learning Paths"
                        
                        # Optionally set a flag to indicate we came from skill analysis
                        st.session_state.from_skill_analysis = True
                        
                        # Force rerun to apply the change
                        st.rerun()
                
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
    analysis_available = st.session_state.skill_analysis_results is not None
    
    # Get priority skills from analysis if available
    priority_skills = []
    if analysis_available and "structured_data" in st.session_state.skill_analysis_results:
        analysis = st.session_state.skill_analysis_results
        if "priority_skills" in analysis["structured_data"]:
            priority_skills = analysis["structured_data"]["priority_skills"]
            
            # Display a message about the priority skills from analysis
            if priority_skills:
                st.info(f"Based on your skill analysis for {analysis.get('target_role', 'your target role')}, "
                       f"we recommend focusing on these priority skills: {', '.join(priority_skills)}")
    
    # Default skills if none are available from analysis
    default_skills = [
        "Python Programming", "Data Analysis", "Machine Learning",
        "Project Management", "Leadership", "Communication"
    ]
    
    # Combine skills for selection
    all_skills = priority_skills + [skill for skill in default_skills if skill not in priority_skills]
    
    # Add user's current skills if they're not already in the list
    user_skills = st.session_state.user_context.get("skills", [])
    all_skills = all_skills + [skill for skill in user_skills if skill not in all_skills]
    
    # Default skill selection - use first priority skill if coming from skill analysis
    default_skill = ""
    if st.session_state.get("from_skill_analysis", False) and priority_skills:
        default_skill = priority_skills[0]
        # Reset the flag
        st.session_state.from_skill_analysis = False
    
    with st.form("learning_path_form"):
        col5, col6 = st.columns(2)
        
        with col5:
            skill_to_learn = st.selectbox(
                "Select Skill to Develop",
                options=[""] + all_skills,
                index=0 if default_skill == "" else all_skills.index(default_skill) + 1
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
                    skill_name=skill_to_learn,
                    target_role=st.session_state.user_context.get("target_role", ""),
                    skill_level=current_level,
                    user_id=st.session_state.user_context.get("user_id")
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
                
                # Initialize progress information for display in profile
                st.session_state.current_learning_path['title'] = skill_to_learn
                st.session_state.current_learning_path['progress'] = {
                    'completed': 0,
                    'total': 100
                }
                
                # Display learning path
                st.success(f"Learning path created for {skill_to_learn}!")
                
                # Learning objectives with validation
                st.subheader("🎯 Learning Objectives")
                objectives = learning_path["structured_data"]["objectives"]
                if objectives:
                    for obj in objectives:
                        if isinstance(obj, dict):
                            st.write(f"• **{obj['title']}**: {obj['description']}")
                        else:
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
                            if isinstance(resource, dict):
                                with st.expander(f"Resource: {resource['title']}"):
                                    st.write(f"**{resource['title']}**")
                                    st.write(resource['description'])
                                    if resource.get('url'):
                                        st.write(f"[Open Resource]({resource['url']})")
                            else:
                                with st.expander(f"Resource: {resource.split(':')[0] if ':' in resource else resource}"):
                                    st.write(resource)
                    else:
                        # Add some default resources if none are found
                        st.warning("No specific resources found. Here are some general recommendations:")
                        st.write("• Online courses on platforms like Coursera, Udemy, or LinkedIn Learning")
                        st.write("• Industry-specific books and publications")
                        st.write("• Documentation and official guides")
                    
                    st.subheader("✍️ Practice Exercises")
                    exercises = learning_path["structured_data"]["exercises"]
                    if exercises:
                        for i, exercise in enumerate(exercises, 1):
                            if isinstance(exercise, dict):
                                st.write(f"{i}. **{exercise['title']}**: {exercise['description']}")
                            else:
                                st.write(f"{i}. {exercise}")
                    else:
                        st.warning("No practice exercises found. Try these general exercises:")
                        st.write("1. Create a small project to practice fundamental concepts")
                        st.write("2. Solve practice problems related to this skill")
                        st.write("3. Apply this skill to improve an existing project")
                
                with col8:
                    st.subheader("⏱️ Timeline and Milestones")
                    # Safely access timeline with fallback
                    timeline = learning_path["structured_data"].get("timeline", [])
                    if timeline:
                        for milestone in timeline:
                            st.info(milestone)
                    else:
                        st.warning("No timeline found.")
                    
                    st.subheader("📋 Assessment Criteria")
                    # Safely access assessment with fallback
                    assessment = learning_path["structured_data"].get("assessment", [])
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
                            "current_level": learning_path.get("skill_level", "beginner"),
                            "target_level": target_level,
                            "start_date": datetime.now().strftime("%Y-%m-%d"),
                            "learning_path": learning_path["structured_data"],
                            "completed_objectives": [],
                            "progress_percentage": 0
                        }
                        
                        # Add or update the skill progress
                        st.session_state.skill_progress[skill_to_learn] = new_skill_progress
                        
                        st.success(f"Now tracking progress for {skill_to_learn}!")
                        
                        # Offer to go to progress tracking tab
                        if st.button("Go to Progress Tracking"):
                            st.session_state.active_tab = "Progress Tracking"
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
        skill_to_learn = learning_path.get("skill_name", "Unknown Skill")
        
        st.success(f"Current learning path: {skill_to_learn}")
        
        # Learning objectives with validation
        st.subheader("🎯 Learning Objectives")
        objectives = learning_path["structured_data"]["objectives"]
        if objectives:
            for obj in objectives:
                if isinstance(obj, dict):
                    st.write(f"• **{obj['title']}**: {obj['description']}")
                else:
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
                    if isinstance(resource, dict):
                        with st.expander(f"Resource: {resource['title']}"):
                            st.write(f"**{resource['title']}**")
                            st.write(resource['description'])
                            if resource.get('url'):
                                st.write(f"[Open Resource]({resource['url']})")
                    else:
                        with st.expander(f"Resource: {resource.split(':')[0] if ':' in resource else resource}"):
                            st.write(resource)
                else:
                    st.warning("No resources found.")
                
                st.subheader("✍️ Practice Exercises")
                exercises = learning_path["structured_data"]["exercises"]
                if exercises:
                    for i, exercise in enumerate(exercises, 1):
                        if isinstance(exercise, dict):
                            st.write(f"{i}. **{exercise['title']}**: {exercise['description']}")
                        else:
                            st.write(f"{i}. {exercise}")
                    else:
                        st.warning("No practice exercises found.")
        
        with col8:
            st.subheader("⏱️ Timeline and Milestones")
            # Safely access timeline with fallback
            timeline = learning_path["structured_data"].get("timeline", [])
            if timeline:
                for milestone in timeline:
                    st.info(milestone)
            else:
                st.warning("No timeline found.")
            
            st.subheader("📋 Assessment Criteria")
            # Safely access assessment with fallback
            assessment = learning_path["structured_data"].get("assessment", [])
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
                    "current_level": learning_path.get("skill_level", "beginner"),
                    "target_level": target_level,
                    "start_date": datetime.now().strftime("%Y-%m-%d"),
                    "learning_path": learning_path["structured_data"],
                    "completed_objectives": [],
                    "progress_percentage": 0
                }
                
                # Add or update the skill progress
                st.session_state.skill_progress[skill_to_learn] = new_skill_progress
                
                st.success(f"Now tracking progress for {skill_to_learn}!")
                
                # Offer to go to progress tracking tab
                if st.button("Go to Progress Tracking"):
                    st.session_state.active_tab = "Progress Tracking"
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
                
                # Count completed objectives, handling both string and object formats
                if progress_data['learning_path']['objectives'] and isinstance(progress_data['learning_path']['objectives'][0], dict):
                    # Handle object format where we use the ID for tracking
                    completed_objective_ids = progress_data.get('completed_objectives', [])
                    completed = len(completed_objective_ids)
                else:
                    # Handle string format
                    completed = len(progress_data.get('completed_objectives', []))
                
                progress_percentage = int((completed / total_objectives) * 100) if total_objectives > 0 else 0
                
                # Update progress percentage
                progress_data['progress_percentage'] = progress_percentage
                
                # Update current_learning_path for display in profile
                if 'current_learning_path' in st.session_state:
                    st.session_state.current_learning_path['title'] = skill_name
                    st.session_state.current_learning_path['progress'] = {
                        'completed': progress_percentage,
                        'total': 100
                    }
                
                # Display progress bar
                st.progress(progress_percentage / 100)
                st.write(f"**Progress:** {int(progress_percentage)}% ({completed}/{total_objectives} objectives completed)")
                
                # Objectives with checkboxes
                st.subheader("Learning Objectives")
                
                # Create a unique key for each objective
                for i, objective in enumerate(progress_data['learning_path']['objectives']):
                    obj_key = f"{skill_name}_obj_{i}"
                    
                    # Handle objective in both formats
                    if isinstance(objective, dict):
                        obj_id = objective.get('id', str(i))
                        obj_title = objective.get('title', '')
                        is_completed = obj_id in progress_data.get('completed_objectives', [])
                        
                        # Create a checkbox for each objective
                        if st.checkbox(obj_title, value=is_completed, key=obj_key):
                            if obj_id not in progress_data.get('completed_objectives', []):
                                if 'completed_objectives' not in progress_data:
                                    progress_data['completed_objectives'] = []
                                progress_data['completed_objectives'].append(obj_id)
                        else:
                            if obj_id in progress_data.get('completed_objectives', []):
                                progress_data['completed_objectives'].remove(obj_id)
                    else:
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
            
            # Ensure progress_percentage exists
            if 'progress_percentage' not in progress_data:
                # Calculate the percentage if it doesn't exist
                if 'learning_path' in progress_data and 'objectives' in progress_data['learning_path']:
                    total_objectives = len(progress_data['learning_path']['objectives'])
                    completed = len(progress_data.get('completed_objectives', []))
                    progress_data['progress_percentage'] = int((completed / total_objectives) * 100) if total_objectives > 0 else 0
                else:
                    progress_data['progress_percentage'] = 0
            
            session_paths.append({
                "id": path_id,
                "skill_name": skill_name,
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
    disk_path_skills = {path.get("skill_name", "") for path in disk_paths}
    combined_paths = disk_paths + [path for path in session_paths if path.get("skill_name", "") not in disk_path_skills]
    
    if not combined_paths:
        st.info("No active learning paths. Create a learning path to start tracking progress!")
        
        # Add a button to navigate to Learning Paths tab
        if st.button("Create a Learning Path"):
            st.session_state.active_tab = "Learning Paths"
            st.rerun()
        return
    
    # Display learning path selection
    path_options = {}
    for path in combined_paths:
        # Handle both old and new field names
        skill = path.get("skill_name", path.get("skill", "Unknown Skill"))
        current = path.get("skill_level", path.get("current_level", "beginner"))
        target = path.get("target_role", path.get("target_level", "advanced"))
        path_options[f"{skill} ({current} → {target})"] = path["id"]
    
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
            # Safely access progress_percentage with fallback
            try:
                if "progress" in path and "progress_percentage" in path["progress"]:
                    progress_percentage = path["progress"]["progress_percentage"]
                elif "progress" in path and isinstance(path["progress"], dict) and "completed" in path["progress"]:
                    progress_percentage = path["progress"]["completed"]
                else:
                    # Calculate it from objectives if available
                    if "structured_data" in path and "objectives" in path["structured_data"]:
                        total = len(path["structured_data"]["objectives"])
                        completed = len(path["progress"].get("completed_objectives", []))
                        progress_percentage = int((completed / total) * 100) if total > 0 else 0
                    else:
                        progress_percentage = 0
            except Exception as e:
                st.error(f"Error calculating progress: {str(e)}")
                progress_percentage = 0
            
            # Ensure progress_percentage is an integer for display
            st.progress(int(progress_percentage) / 100)
            st.metric("Overall Progress", f"{int(progress_percentage)}%")
            
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
            objectives_list = path["structured_data"].get("objectives", [])
            
            # Prepare options and defaults for objectives
            objective_options = []
            objective_defaults = []
            
            # Handle both object and string formats
            for obj in objectives_list:
                if isinstance(obj, dict):
                    objective_options.append({"label": obj["title"], "value": obj["id"]})
                    if obj["id"] in path["progress"].get("completed_objectives", []):
                        objective_defaults.append(obj["id"])
                else:
                    objective_options.append(obj)
                    if obj in path["progress"].get("completed_objectives", []):
                        objective_defaults.append(obj)
            
            # Determine if we're using dict format objectives
            using_dict_objectives = objectives_list and isinstance(objectives_list[0], dict)
            
            # Display objectives multiselect
            if using_dict_objectives:
                completed_objectives = st.multiselect(
                    "Learning Objectives",
                    options=[opt["value"] for opt in objective_options],
                    default=objective_defaults,
                    format_func=lambda x: next((opt["label"] for opt in objective_options if opt["value"] == x), x)
                )
            else:
                completed_objectives = st.multiselect(
                    "Learning Objectives",
                    options=objective_options,
                    default=objective_defaults
                )
            
            # Prepare resources
            resources_list = path["structured_data"].get("resources", [])
            
            # Prepare options and defaults for resources
            resource_options = []
            resource_defaults = []
            
            # Handle both object and string formats
            for res in resources_list:
                if isinstance(res, dict):
                    resource_options.append({"label": res["title"], "value": res["id"]})
                    if res["id"] in path["progress"].get("completed_resources", []):
                        resource_defaults.append(res["id"])
                else:
                    resource_options.append(res)
                    if res in path["progress"].get("completed_resources", []):
                        resource_defaults.append(res)
            
            # Determine if we're using dict format
            using_dict_resources = resources_list and isinstance(resources_list[0], dict)
            
            # Display resources multiselect
            if using_dict_resources:
                completed_resources = st.multiselect(
                    "Resources",
                    options=[opt["value"] for opt in resource_options],
                    default=resource_defaults,
                    format_func=lambda x: next((opt["label"] for opt in resource_options if opt["value"] == x), x)
                )
            else:
                completed_resources = st.multiselect(
                    "Resources",
                    options=resource_options,
                    default=resource_defaults
                )
            
            # Prepare exercises
            exercises_list = path["structured_data"].get("exercises", [])
            
            # Prepare options and defaults for exercises
            exercise_options = []
            exercise_defaults = []
            
            # Handle both object and string formats
            for ex in exercises_list:
                if isinstance(ex, dict):
                    exercise_options.append({"label": ex["title"], "value": ex["id"]})
                    if ex["id"] in path["progress"].get("completed_exercises", []):
                        exercise_defaults.append(ex["id"])
                else:
                    exercise_options.append(ex)
                    if ex in path["progress"].get("completed_exercises", []):
                        exercise_defaults.append(ex)
            
            # Determine if we're using dict format
            using_dict_exercises = exercises_list and isinstance(exercises_list[0], dict)
            
            # Display exercises multiselect
            if using_dict_exercises:
                completed_exercises = st.multiselect(
                    "Exercises",
                    options=[opt["value"] for opt in exercise_options],
                    default=exercise_defaults,
                    format_func=lambda x: next((opt["label"] for opt in exercise_options if opt["value"] == x), x)
                )
            else:
                completed_exercises = st.multiselect(
                    "Exercises",
                    options=exercise_options,
                    default=exercise_defaults
                )
        
        # Update progress button
        if st.button("Update Progress"):
            try:
                # Ensure completed lists are never None
                completed_objectives_list = completed_objectives or []
                completed_resources_list = completed_resources or []
                completed_exercises_list = completed_exercises or []
                
                # Update progress in the advisor
                updated_path = advisor.update_learning_path_progress(
                    learning_path_id=path["id"],
                    completed_objectives=completed_objectives_list,
                    completed_resources=completed_resources_list,
                    completed_exercises=completed_exercises_list,
                    time_spent_minutes=time_spent * 60,  # Convert hours to minutes
                    reflection=user_notes,
                    user_id=user_id
                )
                
                # Also update session state if this is a session-based path
                if path["skill_name"] in st.session_state.get("skill_progress", {}):
                    try:
                        # Update the completed objectives in the session state
                        st.session_state.skill_progress[path["skill_name"]]["completed_objectives"] = completed_objectives_list
                        
                        # Safely update progress_percentage
                        if "progress" in updated_path and "progress_percentage" in updated_path["progress"]:
                            progress_pct = updated_path["progress"]["progress_percentage"]
                        else:
                            # Calculate it if not available
                            total = len(path["structured_data"].get("objectives", []))
                            completed_count = len(completed_objectives_list)
                            progress_pct = int((completed_count / total) * 100) if total > 0 else 0
                        
                        st.session_state.skill_progress[path["skill_name"]]["progress_percentage"] = progress_pct
                        
                        # Also update the current_learning_path for profile display
                        if 'current_learning_path' in st.session_state:
                            st.session_state.current_learning_path['title'] = path.get("skill_name", path.get("skill", "Unknown Skill"))
                            st.session_state.current_learning_path['progress'] = {
                                'completed': progress_pct,
                                'total': 100
                            }
                    except Exception as e:
                        st.warning(f"Note: Unable to update session state progress: {str(e)}")
                
                st.success("Progress updated successfully!")
                
                # Get assessment feedback
                try:
                    assessment = advisor.assess_progress(
                        learning_path_id=path["id"],
                        user_reflection=user_notes,
                        user_id=user_id
                    )
                    
                    # Display assessment feedback
                    st.subheader("Progress Assessment")
                    
                    # Display feedback messages
                    for feedback in assessment.get("feedback", []):
                        st.info(feedback)
                    
                    # Display next steps
                    st.subheader("Recommended Next Steps")
                    for step in assessment.get("next_steps", []):
                        st.success(step)
                    
                    # Display section completion metrics
                    st.subheader("Section Completion")
                    col3, col4, col5 = st.columns(3)
                    
                    with col3:
                        st.metric("Objectives", f"{int(assessment.get('objectives_completion', 0))}%")
                    
                    with col4:
                        st.metric("Resources", f"{int(assessment.get('resources_completion', 0))}%")
                    
                    with col5:
                        st.metric("Exercises", f"{int(assessment.get('exercises_completion', 0))}%")
                except Exception as e:
                    st.error(f"Error generating assessment: {str(e)}")
                    st.info("Your progress has been saved, but we couldn't generate an assessment at this time.")
                
            except Exception as e:
                st.error(f"Error updating progress: {str(e)}")
                if st.checkbox("Show detailed error"):
                    st.exception(e)

if __name__ == "__main__":
    main() 