from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from langchain.prompts import PromptTemplate
import os
import datetime
import json
import re

class SkillsAdvisorAgent(BaseAgent):
    def __init__(self, verbose: bool = False, user_data_path: str = None):
        super().__init__(
            role="Skills Development Advisor",
            goal="Analyze skill gaps and provide personalized learning recommendations",
            backstory="Expert in career development and skill enhancement strategies",
            verbose=verbose
        )
        
        # Path for storing user learning data
        self.user_data_path = user_data_path or "data/user_skills"
        os.makedirs(self.user_data_path, exist_ok=True)
        
        # User profile data
        self.user_profile = {}
        
        # Active learning paths and progress tracking
        self.learning_paths = {}
        self.skill_progress = {}
        
        self.skills_analysis_prompt = PromptTemplate(
            input_variables=["current_skills", "target_role", "job_requirements"],
            template="""
            Analyze the skill gap between current skills and target role requirements:
            
            Current Skills:
            {current_skills}
            
            Target Role:
            {target_role}
            
            Job Requirements:
            {job_requirements}
            
            Please provide:
            1. Skill Gap Analysis
            2. Priority Skills to Develop
            3. Learning Resources and Timeline
            4. Career Transition Strategy
            """
        )
        
        self.learning_path_prompt = PromptTemplate(
            input_variables=["skill", "current_level", "target_level"],
            template="""
            Create a detailed learning path for skill development:
            
            Skill: {skill}
            Current Level: {current_level}
            Target Level: {target_level}
            
            Please provide a structured response with the following sections, using bullet points for each item:
            
            1. Learning Objectives:
            - [List specific, measurable objectives]
            
            2. Recommended Resources:
            - [List courses, books, tutorials, documentation]
            
            3. Timeline and Milestones:
            - [Break down into weekly or monthly goals]
            
            4. Practice Exercises:
            - [List specific exercises and projects]
            
            5. Assessment Criteria:
            - [List ways to measure progress]
            
            Make sure each section has at least 3-5 detailed items.
            """
        )
    
    def analyze_skill_gaps(
        self,
        current_skills: List[str],
        target_role: str,
        job_requirements: List[str],
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Analyze gaps between current skills and target role requirements
        
        Args:
            current_skills (List[str]): List of current skills
            target_role (str): Target job role
            job_requirements (List[str]): Required skills for target role
            user_id (Optional[str]): User ID for saving analysis
            
        Returns:
            Dict: Skill gap analysis and recommendations
        """
        try:
            # Format inputs for prompt
            current_skills_text = "\n".join(f"- {skill}" for skill in current_skills)
            requirements_text = "\n".join(f"- {req}" for req in job_requirements)
            
            # Get analysis from LLM using invoke instead of predict
            response = self.llm.invoke(
                self.skills_analysis_prompt.format(
                    current_skills=current_skills_text,
                    target_role=target_role,
                    job_requirements=requirements_text
                )
            ).content
            
            # Parse and structure the response
            analysis = {
                "raw_analysis": response,
                "structured_data": self._parse_skills_analysis(response)
            }
            
            self._log(f"Completed skill gap analysis for {target_role}")
            
            # Save analysis if user_id is provided
            if user_id:
                self._save_user_data(user_id, f"analysis_{target_role}", analysis)
            
            return analysis
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
    def create_learning_path(
        self,
        skill: str,
        current_level: str = "beginner",
        target_level: str = "proficient",
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Create a detailed learning path for a specific skill
        """
        try:
            # Debug log
            self._log(f"Creating learning path for {skill} (from {current_level} to {target_level})")
            
            # Validate inputs
            if not skill or not isinstance(skill, str):
                raise ValueError(f"Invalid skill: {skill}. Must be a non-empty string.")
            
            valid_levels = ["beginner", "intermediate", "advanced", "expert", "proficient"]
            if current_level not in valid_levels:
                self._log(f"Warning: Invalid current_level: {current_level}. Using 'beginner' instead.")
                current_level = "beginner"
            
            if target_level not in valid_levels:
                self._log(f"Warning: Invalid target_level: {target_level}. Using 'proficient' instead.")
                target_level = "proficient"
            
            # Get learning path from LLM
            prompt = self.learning_path_prompt.format(
                skill=skill,
                current_level=current_level,
                target_level=target_level
            )
            
            self._log(f"Sending prompt to LLM: {prompt}")
            
            response = self.llm.invoke(prompt).content
            
            # Debug log
            self._log(f"Received raw LLM response of length: {len(response)}")
            
            # Parse and structure the response
            structured_data = self._parse_learning_path(response)
            
            # Validate structured data
            for section, items in structured_data.items():
                if not items or not isinstance(items, list):
                    self._log(f"Warning: Section '{section}' is empty or invalid. Using defaults.")
                    if section == "objectives":
                        structured_data[section] = ["Master fundamental concepts", "Build practical skills", "Complete real-world projects"]
                    elif section == "resources":
                        structured_data[section] = ["Online courses", "Practice exercises", "Documentation"]
                    elif section == "timeline":
                        structured_data[section] = ["Week 1-2: Basics", "Week 3-4: Advanced concepts", "Week 5-6: Projects"]
                    elif section == "exercises":
                        structured_data[section] = ["Basic exercises", "Intermediate challenges", "Advanced projects"]
                    elif section == "assessment":
                        structured_data[section] = ["Knowledge tests", "Project evaluation", "Practical application"]
            
            # Debug log
            self._log(f"Parsed structured data with {sum(len(items) for items in structured_data.values())} total items")
            
            # Create learning path object with progress tracking
            timestamp = datetime.datetime.now()
            learning_path = {
                "id": f"{skill}_{timestamp.strftime('%Y%m%d%H%M%S')}",
                "skill": skill,
                "current_level": current_level,
                "target_level": target_level,
                "created_at": timestamp.isoformat(),
                "modified_at": timestamp.isoformat(),
                "raw_response": response,
                "structured_data": structured_data,
                "progress": {
                    "status": "active",
                    "completed_objectives": [],
                    "completed_resources": [],
                    "completed_exercises": [],
                    "progress_percentage": 0,
                    "last_updated": timestamp.isoformat(),
                    "notes": [],
                    "time_spent_hours": 0
                }
            }
            
            # Store in instance memory
            self.learning_paths[learning_path["id"]] = learning_path
            
            # Save learning path if user_id is provided
            if user_id:
                self._save_learning_path(user_id, learning_path)
            
            self._log(f"Successfully created learning path for {skill}")
            return learning_path
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(f"Error creating learning path: {error_msg}")
            
            # Return a minimal valid response structure even in case of error
            timestamp = datetime.datetime.now()
            return {
                "id": f"error_{timestamp.strftime('%Y%m%d%H%M%S')}",
                "skill": skill,
                "current_level": current_level,
                "target_level": target_level,
                "created_at": timestamp.isoformat(),
                "error": str(e),
                "structured_data": {
                    "objectives": ["Master fundamental concepts", "Build practical skills", "Complete real-world projects"],
                    "resources": ["Online courses", "Practice exercises", "Documentation"],
                    "timeline": ["Week 1-2: Basics", "Week 3-4: Advanced concepts", "Week 5-6: Projects"],
                    "exercises": ["Basic exercises", "Intermediate challenges", "Advanced projects"],
                    "assessment": ["Knowledge tests", "Project evaluation", "Practical application"]
                }
            }
    
    def _parse_skills_analysis(self, response: str) -> Dict:
        """Parse the skills analysis response"""
        try:
            parsed_data = {
                "skill_gaps": [],
                "priority_skills": [],
                "learning_resources": [],
                "transition_strategy": []
            }
            
            # Split into sections and process each line
            current_section = None
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Identify sections
                if "Skill Gap Analysis" in line or "Gap Analysis" in line:
                    current_section = "skill_gaps"
                    continue
                elif "Priority Skills" in line:
                    current_section = "priority_skills"
                    continue
                elif "Learning Resources" in line or "Resources" in line:
                    current_section = "learning_resources"
                    continue
                elif "Career Transition Strategy" in line or "Transition Strategy" in line:
                    current_section = "transition_strategy"
                    continue
                
                # Add items to current section if line starts with a bullet point or number
                if current_section and (line.startswith(('-', '•', '*')) or 
                                      any(line.startswith(f"{i}.") for i in range(1, 10))):
                    # Clean the line by removing bullets and numbers
                    cleaned_line = line.lstrip("0123456789.- *•").strip()
                    if cleaned_line:
                        parsed_data[current_section].append(cleaned_line)
            
            # Debug logging
            self._log(f"Parsed sections: {[k for k, v in parsed_data.items() if v]}")
            self._log(f"Number of items parsed: {sum(len(v) for v in parsed_data.values())}")
            
            return parsed_data
            
        except Exception as e:
            self._log(f"Error parsing skills analysis: {str(e)}")
            self._log(f"Raw response: {response}")
            return parsed_data
    
    def _parse_learning_path(self, response: str) -> Dict:
        """Parse the learning path response with improved section detection and error handling"""
        # Debug log
        self._log(f"Parsing learning path response of length: {len(response)}")
        
        parsed_data = {
            "objectives": [],
            "resources": [],
            "timeline": [],
            "exercises": [],
            "assessment": []
        }
        
        # Track which sections were found for debugging
        found_sections = []
        
        # First attempt: Try to parse by section headers
        current_section = None
        for line in response.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers with more variations
            if any(header in line.lower() for header in ["learning objectives", "objectives:", "1. learning objectives"]):
                current_section = "objectives"
                found_sections.append("objectives")
                continue
            elif any(header in line.lower() for header in ["recommended resources", "resources:", "2. recommended resources"]):
                current_section = "resources"
                found_sections.append("resources")
                continue
            elif any(header in line.lower() for header in ["timeline", "milestones", "3. timeline", "timeline and milestones"]):
                current_section = "timeline"
                found_sections.append("timeline")
                continue
            elif any(header in line.lower() for header in ["practice exercises", "exercises:", "4. practice exercises"]):
                current_section = "exercises"
                found_sections.append("exercises")
                continue
            elif any(header in line.lower() for header in ["assessment criteria", "assessment:", "5. assessment"]):
                current_section = "assessment"
                found_sections.append("assessment")
                continue
            
            # Process line based on current section
            if current_section and line:
                # Remove numbering and bullet points
                cleaned_line = re.sub(r'^[\d\.\-\*•►\s]+', '', line).strip()
                if cleaned_line:
                    parsed_data[current_section].append(cleaned_line)
        
        # Debug log
        self._log(f"Found sections in first pass: {found_sections}")
        
        # Second attempt: If sections are missing, try to parse by numbered sections
        if len(found_sections) < 5:
            self._log("First pass incomplete, trying second parsing method")
            sections = re.split(r'\n\s*\d+\.|\n\s*[A-Za-z]+:', response)
            if len(sections) > 1:
                # First element is usually empty or introduction
                sections = sections[1:]
                
                # Map sections to our structure if we have enough
                if len(sections) >= 5:
                    section_mapping = ["objectives", "resources", "timeline", "exercises", "assessment"]
                    for i, section_content in enumerate(sections[:5]):
                        section_name = section_mapping[i]
                        lines = [line.strip() for line in section_content.split('\n') if line.strip()]
                        cleaned_lines = [re.sub(r'^[\d\.\-\*•►\s]+', '', line).strip() for line in lines]
                        parsed_data[section_name] = [line for line in cleaned_lines if line]
                        if parsed_data[section_name]:
                            found_sections.append(section_name)
        
        # Debug log
        self._log(f"Found sections after second pass: {found_sections}")
        self._log(f"Parsed data counts: objectives={len(parsed_data['objectives'])}, resources={len(parsed_data['resources'])}, timeline={len(parsed_data['timeline'])}, exercises={len(parsed_data['exercises'])}, assessment={len(parsed_data['assessment'])}")
        
        # Add default items if sections are empty
        for section in parsed_data:
            if not parsed_data[section]:
                if section == "objectives":
                    parsed_data[section] = ["Master fundamental concepts", "Build practical skills", "Complete real-world projects"]
                elif section == "resources":
                    parsed_data[section] = ["Online courses", "Practice exercises", "Documentation"]
                elif section == "timeline":
                    parsed_data[section] = ["Week 1-2: Basics", "Week 3-4: Advanced concepts", "Week 5-6: Projects"]
                elif section == "exercises":
                    parsed_data[section] = ["Basic exercises", "Intermediate challenges", "Advanced projects"]
                elif section == "assessment":
                    parsed_data[section] = ["Knowledge tests", "Project evaluation", "Practical application"]
                
                self._log(f"Added default items for empty section: {section}")
        
        return parsed_data
    
    def get_required_fields(self) -> List[str]:
        """Get required fields for skills analysis"""
        return ["current_skills", "target_role"]
    
    def set_user_profile(self, profile_data: Dict[str, Any]) -> None:
        """Set or update the user profile data"""
        self.user_profile = profile_data
        self._log(f"Updated user profile for {profile_data.get('name', 'user')}")
        
        # Save profile to disk
        if self.user_profile.get("user_id"):
            self._save_user_data(self.user_profile.get("user_id"), "profile", self.user_profile)
    
    def update_skill_progress(
        self,
        learning_path_id: str,
        completed_objectives: List[str] = None,
        completed_resources: List[str] = None,
        completed_exercises: List[str] = None,
        time_spent_hours: float = 0,
        user_notes: str = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """Update progress for a learning path"""
        try:
            # Check if the learning path exists
            if learning_path_id not in self.learning_paths:
                if user_id:
                    # Try to load learning paths first
                    self._load_learning_paths(user_id)
                    if learning_path_id not in self.learning_paths:
                        raise ValueError(f"Learning path {learning_path_id} not found")
                else:
                    raise ValueError(f"Learning path {learning_path_id} not found")
            
            # Get the learning path
            learning_path = self.learning_paths[learning_path_id]
            
            # Update completed items
            if completed_objectives is not None:
                learning_path["progress"]["completed_objectives"] = completed_objectives
            
            if completed_resources is not None:
                learning_path["progress"]["completed_resources"] = completed_resources
            
            if completed_exercises is not None:
                learning_path["progress"]["completed_exercises"] = completed_exercises
            
            # Update time spent
            if time_spent_hours > 0:
                learning_path["progress"]["time_spent_hours"] += time_spent_hours
            
            # Add user notes if provided
            if user_notes:
                timestamp = datetime.datetime.now().isoformat()
                if "notes" not in learning_path["progress"]:
                    learning_path["progress"]["notes"] = []
                
                learning_path["progress"]["notes"].append({
                    "timestamp": timestamp,
                    "content": user_notes
                })
            
            # Calculate progress percentage
            total_items = (
                len(learning_path["structured_data"]["objectives"]) +
                len(learning_path["structured_data"]["resources"]) +
                len(learning_path["structured_data"]["exercises"])
            )
            
            completed_items = (
                len(learning_path["progress"]["completed_objectives"]) +
                len(learning_path["progress"]["completed_resources"]) +
                len(learning_path["progress"]["completed_exercises"])
            )
            
            if total_items > 0:
                progress_percentage = (completed_items / total_items) * 100
            else:
                progress_percentage = 0
            
            # Update progress percentage and last updated timestamp
            learning_path["progress"]["progress_percentage"] = progress_percentage
            learning_path["progress"]["last_updated"] = datetime.datetime.now().isoformat()
            
            # Save the updated learning path
            if user_id:
                self._save_learning_path(user_id, learning_path)
            
            # Debug log
            self._log(f"Updated progress for learning path {learning_path_id} to {progress_percentage:.1f}%")
            
            return learning_path
            
        except Exception as e:
            error_msg = str(e)
            self._log(f"Error updating skill progress: {error_msg}")
            raise ValueError(f"Failed to update skill progress: {error_msg}")
    
    def assess_progress(
        self,
        learning_path_id: str,
        user_reflection: str = "",
        user_id: Optional[str] = None
    ) -> Dict:
        """Assess progress and provide feedback for a learning path"""
        try:
            # Check if the learning path exists
            if learning_path_id not in self.learning_paths:
                if user_id:
                    # Try to load learning paths first
                    self._load_learning_paths(user_id)
                    if learning_path_id not in self.learning_paths:
                        raise ValueError(f"Learning path {learning_path_id} not found")
                else:
                    raise ValueError(f"Learning path {learning_path_id} not found")
            
            # Get the learning path
            learning_path = self.learning_paths[learning_path_id]
            
            # Calculate progress metrics
            progress = learning_path["progress"]
            structured_data = learning_path["structured_data"]
            
            # Calculate completion percentages for each section
            objectives_completion = len(progress["completed_objectives"]) / len(structured_data["objectives"]) if structured_data["objectives"] else 0
            resources_completion = len(progress["completed_resources"]) / len(structured_data["resources"]) if structured_data["resources"] else 0
            exercises_completion = len(progress["completed_exercises"]) / len(structured_data["exercises"]) if structured_data["exercises"] else 0
            
            # Generate feedback based on progress
            feedback = {
                "overall_progress": progress["progress_percentage"],
                "objectives_completion": objectives_completion * 100,
                "resources_completion": resources_completion * 100,
                "exercises_completion": exercises_completion * 100,
                "time_spent_hours": progress["time_spent_hours"],
                "feedback": [],
                "next_steps": [],
                "assessment_date": datetime.datetime.now().isoformat()
            }
            
            # Generate feedback messages
            if progress["progress_percentage"] < 25:
                feedback["feedback"].append("You're just getting started. Keep up the momentum!")
                feedback["next_steps"].append("Focus on completing the foundational objectives first.")
            elif progress["progress_percentage"] < 50:
                feedback["feedback"].append("You're making steady progress. Keep going!")
                feedback["next_steps"].append("Consider spending more time on practical exercises.")
            elif progress["progress_percentage"] < 75:
                feedback["feedback"].append("You're well on your way to mastering this skill!")
                feedback["next_steps"].append("Start applying your knowledge to real-world projects.")
            else:
                feedback["feedback"].append("Excellent progress! You're almost there.")
                feedback["next_steps"].append("Focus on the remaining advanced topics to complete your learning path.")
            
            # Add section-specific feedback
            if objectives_completion < resources_completion and objectives_completion < exercises_completion:
                feedback["feedback"].append("You've been exploring resources and exercises, but make sure to complete the core learning objectives.")
            elif resources_completion < objectives_completion and resources_completion < exercises_completion:
                feedback["feedback"].append("You're making good progress on objectives, but consider exploring more of the recommended resources.")
            elif exercises_completion < objectives_completion and exercises_completion < resources_completion:
                feedback["feedback"].append("You've been studying the material, but need more practice with the exercises to solidify your skills.")
            
            # Add time-based feedback
            if progress["time_spent_hours"] < 5:
                feedback["feedback"].append("Consider dedicating more time to this skill to accelerate your progress.")
            elif progress["time_spent_hours"] > 20 and progress["progress_percentage"] < 50:
                feedback["feedback"].append("You've spent significant time on this skill. Consider reviewing your learning approach for more efficiency.")
            
            # Add user reflection to the learning path if provided
            if user_reflection:
                timestamp = datetime.datetime.now().isoformat()
                if "reflections" not in learning_path:
                    learning_path["reflections"] = []
                
                learning_path["reflections"].append({
                    "timestamp": timestamp,
                    "content": user_reflection,
                    "progress_at_reflection": progress["progress_percentage"]
                })
                
                # Save the updated learning path
                if user_id:
                    self._save_learning_path(user_id, learning_path)
            
            # Debug log
            self._log(f"Assessed progress for learning path {learning_path_id}")
            
            return feedback
            
        except Exception as e:
            error_msg = str(e)
            self._log(f"Error assessing progress: {error_msg}")
            raise ValueError(f"Failed to assess progress: {error_msg}")
    
    def get_user_learning_paths(self, user_id: str) -> List[Dict]:
        """Get all learning paths for a user"""
        try:
            # First, try to load learning paths from disk if not already loaded
            if not self.learning_paths:
                self._load_learning_paths(user_id)
            
            # Return the learning paths as a list
            paths = list(self.learning_paths.values())
            
            # Debug log
            self._log(f"Retrieved {len(paths)} learning paths for user {user_id}")
            
            return paths
        except Exception as e:
            self._log(f"Error retrieving learning paths: {str(e)}")
            return []
    
    def _save_user_data(self, user_id: str, data_type: str, data: Dict) -> None:
        """Save user data to disk"""
        try:
            # Create the user directory path
            user_dir = os.path.join(self.user_data_path, user_id)
            
            # Create directory if it doesn't exist
            os.makedirs(user_dir, exist_ok=True)
            
            # Create the file path
            file_path = os.path.join(user_dir, f"{data_type}.json")
            
            # Save the data to disk
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Debug log
            self._log(f"Saved {data_type} data for user {user_id}")
            
        except Exception as e:
            self._log(f"Error saving {data_type} data: {str(e)}")
            raise
    
    def _save_learning_path(self, user_id: str, learning_path: Dict) -> None:
        """Save a learning path to disk"""
        try:
            # Create the user directory path
            user_dir = os.path.join(self.user_data_path, user_id)
            learning_paths_dir = os.path.join(user_dir, "learning_paths")
            
            # Create directories if they don't exist
            os.makedirs(learning_paths_dir, exist_ok=True)
            
            # Ensure the learning path has an ID
            if "id" not in learning_path:
                timestamp = datetime.datetime.now()
                learning_path["id"] = f"{learning_path.get('skill', 'unknown')}_{timestamp.strftime('%Y%m%d%H%M%S')}"
            
            # Create the file path
            file_path = os.path.join(learning_paths_dir, f"{learning_path['id']}.json")
            
            # Save the learning path to disk
            with open(file_path, 'w') as f:
                json.dump(learning_path, f, indent=2)
            
            # Debug log
            self._log(f"Saved learning path {learning_path['id']} for user {user_id}")
            
        except Exception as e:
            self._log(f"Error saving learning path: {str(e)}")
            raise
    
    def _load_learning_paths(self, user_id: str) -> None:
        """Load all learning paths for a user"""
        try:
            # Create the user directory path
            user_dir = os.path.join(self.user_data_path, user_id)
            learning_paths_dir = os.path.join(user_dir, "learning_paths")
            
            # Check if the directory exists
            if not os.path.exists(learning_paths_dir):
                os.makedirs(learning_paths_dir, exist_ok=True)
                self._log(f"Created learning paths directory for user {user_id}")
                return
            
            # Load all learning path files
            path_files = [f for f in os.listdir(learning_paths_dir) if f.endswith('.json')]
            
            # Debug log
            self._log(f"Found {len(path_files)} learning path files for user {user_id}")
            
            # Load each file
            for file_name in path_files:
                try:
                    file_path = os.path.join(learning_paths_dir, file_name)
                    with open(file_path, 'r') as f:
                        learning_path = json.load(f)
                        
                    # Add to the learning paths dictionary
                    if "id" in learning_path:
                        self.learning_paths[learning_path["id"]] = learning_path
                except Exception as e:
                    self._log(f"Error loading learning path file {file_name}: {str(e)}")
            
            self._log(f"Successfully loaded {len(self.learning_paths)} learning paths for user {user_id}")
            
        except Exception as e:
            self._log(f"Error loading learning paths: {str(e)}")
            # Initialize empty if loading fails
            self.learning_paths = {}
    
    def _format_list_with_progress(self, items: List[str], completed_items: List[str]) -> str:
        """Format a list of items with completion status"""
        # Implementation for formatting progress lists 