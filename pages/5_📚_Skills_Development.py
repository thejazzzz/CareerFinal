import streamlit as st
from agents.skills_advisor import SkillsAdvisorAgent
from datetime import datetime
import os
import uuid
import json
import pandas as pd
import re
from pathlib import Path
from utils.auth_utils import is_authenticated

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

# Helper function to sync progress data across components
def sync_progress_data(skill_name, progress_percentage):
    """
    Ensure progress data is synchronized across all parts of the application
    
    Args:
        skill_name: The name of the skill being updated
        progress_percentage: The new progress percentage value
    """
    try:
        # Update the current learning path if it matches this skill
        if 'current_learning_path' in st.session_state:
            current_path = st.session_state.current_learning_path
            current_path_title = current_path.get('title', '')
            current_path_skill = current_path.get('skill_name', '')
            
            if current_path_title == skill_name or current_path_skill == skill_name:
                # Update progress information
                if 'progress' not in current_path:
                    current_path['progress'] = {}
                
                current_path['progress']['completed'] = progress_percentage
                current_path['progress']['total'] = 100
                
                print(f"Synced current_learning_path progress to {progress_percentage}%")
        
        # Update skill progress if it exists
        if 'skill_progress' in st.session_state and skill_name in st.session_state.skill_progress:
            st.session_state.skill_progress[skill_name]['progress_percentage'] = progress_percentage
            print(f"Synced skill_progress data for {skill_name} to {progress_percentage}%")
        
        # Persist changes
        from utils.data_persistence import DataPersistence
        data_persistence = DataPersistence()
        data_persistence.save_session_state(st.session_state)
        print(f"Saved session state after progress update for {skill_name}")
    except Exception as e:
        print(f"Error syncing progress data: {str(e)}")

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
                                # Create a cleaner resource display with shorter content
                                with st.expander(resource['title']):
                                    st.write(f"**Description:** {resource['description']}")
                                    if resource.get('url'):
                                        st.write(f"[Open Resource]({resource['url']})")
                            else:
                                # Handle string resources if present
                                title = resource.split(':')[0] if ':' in resource else resource
                                with st.expander(title):
                                    st.write(resource)
                    else:
                        st.warning("No resources found.")

                    # Exercise section with proper indentation
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
                        
                        # Log activity
                        if "user_context" in st.session_state and "activities" in st.session_state.user_context:
                            activity = {
                                "type": "Learning Path",
                                "description": f"Started tracking progress for {skill_to_learn} (from {current_level} to {target_level})",
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            st.session_state.user_context["activities"].insert(0, activity)
                        
                        # Save session state to prevent data loss
                        try:
                            from utils.data_persistence import DataPersistence
                            data_persistence = DataPersistence()
                            # Force data persistence to save current_learning_path with updated progress
                            print("PROGRESS DEBUG: Saving session state with updated learning path progress")
                            session_data = dict(st.session_state)
                            print(f"PROGRESS DEBUG: current_learning_path in session data: {session_data.get('current_learning_path', {})}")
                            success = data_persistence.save_session_state(session_data)
                            if success:
                                print("Session state saved after progress update.")
                            else:
                                print("Warning: Failed to save session state after progress update.")
                        except Exception as e:
                            print(f"Error saving session state after progress update: {str(e)}")
                        
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
                        # Create a cleaner resource display with shorter content
                        with st.expander(resource['title']):
                            st.write(f"**Description:** {resource['description']}")
                            if resource.get('url'):
                                st.write(f"[Open Resource]({resource['url']})")
                    else:
                        # Handle string resources if present
                        title = resource.split(':')[0] if ':' in resource else resource
                        with st.expander(title):
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
                
                # Log activity
                if "user_context" in st.session_state and "activities" in st.session_state.user_context:
                    activity = {
                        "type": "Learning Path",
                        "description": f"Started tracking progress for {skill_to_learn} (from {current_level} to {target_level})",
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.user_context["activities"].insert(0, activity)
                
                # Save session state to prevent data loss
                try:
                    from utils.data_persistence import DataPersistence
                    data_persistence = DataPersistence()
                    # Force data persistence to save current_learning_path with updated progress
                    print("PROGRESS DEBUG: Saving session state with updated learning path progress")
                    session_data = dict(st.session_state)
                    print(f"PROGRESS DEBUG: current_learning_path in session data: {session_data.get('current_learning_path', {})}")
                    success = data_persistence.save_session_state(session_data)
                    if success:
                        print("Session state saved after progress update.")
                    else:
                        print("Warning: Failed to save session state after progress update.")
                except Exception as e:
                    print(f"Error saving session state after progress update: {str(e)}")
                
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
            # Check for missing keys and provide defaults
            current_level = progress_data.get('current_level', progress_data.get('skill_level', 'beginner'))
            target_level = progress_data.get('target_level', 'advanced')
            
            with st.expander(f"{skill_name} ({current_level} → {target_level})"):
                st.write(f"**Started:** {progress_data.get('start_date', 'Unknown')}")
                
                # Calculate and display progress
                if 'learning_path' in progress_data and 'objectives' in progress_data['learning_path']:
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
                        current_path_title = st.session_state.current_learning_path.get('title', '')
                        current_path_skill = st.session_state.current_learning_path.get('skill_name', '')
                        
                        # Check if this is the current learning path being tracked
                        if current_path_title == skill_name or current_path_skill == skill_name:
                            st.session_state.current_learning_path['title'] = skill_name
                            st.session_state.current_learning_path['progress'] = {
                                'completed': progress_percentage,
                                'total': 100
                            }
                            # Force save to ensure updates are persisted
                            from utils.data_persistence import DataPersistence
                            data_persistence = DataPersistence()
                            data_persistence.save_session_state(st.session_state)
                            print(f"Updated and saved current_learning_path progress to {progress_percentage}%")
                    
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
                                    
                                    # Calculate new progress percentage
                                    completed = len(progress_data['completed_objectives'])
                                    new_percentage = int((completed / total_objectives) * 100) if total_objectives > 0 else 0
                                    
                                    # Sync progress data across components
                                    sync_progress_data(skill_name, new_percentage)
                            else:
                                if obj_id in progress_data.get('completed_objectives', []):
                                    progress_data['completed_objectives'].remove(obj_id)
                                    
                                    # Calculate new progress percentage
                                    completed = len(progress_data['completed_objectives'])
                                    new_percentage = int((completed / total_objectives) * 100) if total_objectives > 0 else 0
                                    
                                    # Sync progress data across components
                                    sync_progress_data(skill_name, new_percentage)
                        else:
                            is_completed = objective in progress_data.get('completed_objectives', [])
                            
                            # Create a checkbox for each objective
                            if st.checkbox(objective, value=is_completed, key=obj_key):
                                if objective not in progress_data.get('completed_objectives', []):
                                    if 'completed_objectives' not in progress_data:
                                        progress_data['completed_objectives'] = []
                                    progress_data['completed_objectives'].append(objective)
                                    
                                    # Calculate new progress percentage
                                    completed = len(progress_data['completed_objectives'])
                                    new_percentage = int((completed / total_objectives) * 100) if total_objectives > 0 else 0
                                    
                                    # Sync progress data across components
                                    sync_progress_data(skill_name, new_percentage)
                            else:
                                if objective in progress_data.get('completed_objectives', []):
                                    progress_data['completed_objectives'].remove(objective)
                                    
                                    # Calculate new progress percentage
                                    completed = len(progress_data['completed_objectives'])
                                    new_percentage = int((completed / total_objectives) * 100) if total_objectives > 0 else 0
                                    
                                    # Sync progress data across components
                                    sync_progress_data(skill_name, new_percentage)
                
                # Resources section
                st.subheader("Resources")
                # Check if learning_path and resources exist before accessing them
                if 'learning_path' in progress_data and 'resources' in progress_data['learning_path']:
                    resources = progress_data['learning_path']['resources']
                    # Display up to 3 resources
                    for resource in resources[:3]:
                        if isinstance(resource, dict):
                            resource_title = resource.get('title', 'Resource')
                            resource_url = resource.get('url', '')
                            resource_desc = resource.get('description', '')
                            
                            if resource_url:
                                st.markdown(f"• [{resource_title}]({resource_url}): {resource_desc}")
                            else:
                                st.markdown(f"• **{resource_title}**: {resource_desc}")
                        else:
                            st.write(f"• {resource}")
                else:
                    st.info("No resources available for this skill.")
                
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
            # Generate a stable ID based on skill name
            path_id = f"{skill_name}_{user_id}"
            
            # Ensure progress_percentage exists and is correctly calculated
            if 'progress_percentage' not in progress_data or progress_data['progress_percentage'] == 0:
                # Calculate the percentage based on completed objectives
                if 'learning_path' in progress_data and 'objectives' in progress_data['learning_path']:
                    total_objectives = len(progress_data['learning_path']['objectives'])
                    completed = len(progress_data.get('completed_objectives', []))
                    progress_data['progress_percentage'] = int((completed / total_objectives) * 100) if total_objectives > 0 else 0
                    print(f"Calculated progress for {skill_name}: {progress_data['progress_percentage']}% ({completed}/{total_objectives})")
                else:
                    progress_data['progress_percentage'] = 0
                    print(f"No objectives found for {skill_name}, setting progress to 0%")
            else:
                print(f"Using existing progress for {skill_name}: {progress_data['progress_percentage']}%")
            
            # Create a properly structured path entry
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
                    "completed_resources": progress_data.get("completed_resources", []),
                    "completed_exercises": progress_data.get("completed_exercises", []),
                    "progress_percentage": progress_data.get("progress_percentage", 0),
                    "last_updated": datetime.now().isoformat(),
                    "notes": progress_data.get("notes", []),
                    "time_spent_hours": progress_data.get("time_spent_hours", 0)
                }
            })
            
            # Sync with current_learning_path if this is the active skill
            if 'current_learning_path' in st.session_state:
                current_path_title = st.session_state.current_learning_path.get('title', '')
                # Check both skill_name and title fields for matching
                if current_path_title == skill_name or st.session_state.current_learning_path.get('skill_name') == skill_name:
                    # Update progress field
                    if 'progress' not in st.session_state.current_learning_path:
                        st.session_state.current_learning_path['progress'] = {}
                    
                    st.session_state.current_learning_path['progress'] = {
                        'completed': progress_data['progress_percentage'],
                        'total': 100
                    }
                    print(f"Updated current_learning_path progress to {progress_data['progress_percentage']}%")
                    print(f"Current_learning_path content: {st.session_state.current_learning_path}")
    
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
                # Initialize progress_percentage
                progress_percentage = 0
                
                # Check if the path has a progress key
                if "progress" in path and path["progress"] is not None:
                    # Try to get progress percentage from different possible locations
                    if isinstance(path["progress"], dict):
                        if "progress_percentage" in path["progress"]:
                            progress_percentage = path["progress"]["progress_percentage"]
                        elif "completed" in path["progress"]:
                            progress_percentage = path["progress"]["completed"]
                else:
                    # If no progress key, create one
                    path["progress"] = {}
                
                # If we still don't have a progress percentage, calculate it from objectives
                if progress_percentage == 0 and "structured_data" in path and "objectives" in path["structured_data"]:
                    total = len(path["structured_data"]["objectives"])
                    
                    # Get completed objectives safely
                    if "progress" in path and isinstance(path["progress"], dict):
                        completed = len(path["progress"].get("completed_objectives", []))
                    else:
                        completed = 0
                        
                    progress_percentage = int((completed / total) * 100) if total > 0 else 0
                    
                    # Update the path's progress dictionary
                    if "progress" not in path:
                        path["progress"] = {}
                    path["progress"]["progress_percentage"] = progress_percentage
            except Exception as e:
                st.error(f"Error calculating progress: {str(e)}")
                progress_percentage = 0
                # Initialize progress if not present
                if "progress" not in path:
                    path["progress"] = {"progress_percentage": 0}
            
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
            
            # Ensure path has a progress key
            if "progress" not in path or path["progress"] is None:
                path["progress"] = {}
            
            # Handle both object and string formats
            for obj in objectives_list:
                if isinstance(obj, dict):
                    objective_options.append({"label": obj["title"], "value": obj["id"]})
                    # Safely access completed objectives
                    if obj["id"] in path["progress"].get("completed_objectives", []):
                        objective_defaults.append(obj["id"])
                else:
                    objective_options.append(obj)
                    # Safely access completed objectives
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
                    # Safely access completed resources
                    if res["id"] in path["progress"].get("completed_resources", []):
                        resource_defaults.append(res["id"])
                else:
                    resource_options.append(res)
                    # Safely access completed resources
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
                    # Safely access completed exercises
                    if ex["id"] in path["progress"].get("completed_exercises", []):
                        exercise_defaults.append(ex["id"])
                else:
                    exercise_options.append(ex)
                    # Safely access completed exercises
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
                        if 'current_learning_path' not in st.session_state:
                            st.session_state.current_learning_path = {}
                            
                        # Make sure the current_learning_path has all required fields
                        st.session_state.current_learning_path['title'] = path.get("skill_name", path.get("skill", "Unknown Skill"))
                        
                        # Ensure the progress field is properly set as a dictionary with completed and total keys
                        st.session_state.current_learning_path['progress'] = {
                            'completed': progress_pct,
                            'total': 100
                        }
                        
                        # Log the update for debugging
                        print(f"Updated current_learning_path progress to {progress_pct}%")
                        print(f"Progress data structure: {st.session_state.current_learning_path['progress']}")
                        
                        # Additional debugging to verify the progress update
                        print(f"PROGRESS DEBUG: Updated progress for {path.get('skill_name')} to {progress_pct}%")
                        print(f"PROGRESS DEBUG: current_learning_path contents: {st.session_state.current_learning_path}")
                        
                        # Use the sync function to ensure progress is updated across the application
                        skill_name = path.get("skill_name", path.get("title", "Unknown Skill"))
                        sync_progress_data(skill_name, progress_pct)
                        
                        # Create activity record
                        if "user_context" in st.session_state and "activities" in st.session_state.user_context:
                            skill_name = path.get("skill_name", "skill")
                            activity = {
                                "type": "Progress Update",
                                "description": f"Updated {skill_name} learning path progress to {progress_pct}%",
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            st.session_state.user_context["activities"].insert(0, activity)
                            
                        # Save session state to prevent data loss
                        try:
                            from utils.data_persistence import DataPersistence
                            data_persistence = DataPersistence()
                            # Force data persistence to save current_learning_path with updated progress
                            print("PROGRESS DEBUG: Saving session state with updated learning path progress")
                            session_data = dict(st.session_state)
                            print(f"PROGRESS DEBUG: current_learning_path in session data: {session_data.get('current_learning_path', {})}")
                            success = data_persistence.save_session_state(session_data)
                            if success:
                                print("Session state saved after progress update.")
                            else:
                                print("Warning: Failed to save session state after progress update.")
                        except Exception as e:
                            print(f"Error saving session state after progress update: {str(e)}")
                    except Exception as e:
                        st.warning(f"Note: Unable to update session state progress: {str(e)}")
                
                st.success("Progress updated successfully!")
                
                # Force an app refresh to update the UI with new progress values
                st.rerun()
                
                # The code below may not execute due to the rerun above
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
                except ValueError as e:
                    if "time_spent_hours" in str(e):
                        st.warning("Unable to generate assessment: The time tracking feature is still being updated. Your progress has been saved successfully.")
                    else:
                        st.error(f"Error generating assessment: {str(e)}")
                        st.info("Your progress has been saved, but we couldn't generate an assessment at this time.")
                except Exception as e:
                    st.error(f"Error generating assessment: {str(e)}")
                    st.info("Your progress has been saved, but we couldn't generate an assessment at this time.")
                
            except Exception as e:
                st.error(f"Error updating progress: {str(e)}")
                if st.checkbox("Show detailed error"):
                    st.exception(e)

if __name__ == "__main__":
    main() 