from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from langchain.prompts import PromptTemplate
import os
import datetime
import json

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
            
            # Get learning path from LLM
            response = self.llm.invoke(
                self.learning_path_prompt.format(
                    skill=skill,
                    current_level=current_level,
                    target_level=target_level
                )
            ).content
            
            # Debug log
            self._log(f"Raw LLM response: {response}")
            
            # Parse and structure the response
            structured_data = self._parse_learning_path(response)
            
            # Debug log
            self._log(f"Parsed structured data: {structured_data}")
            
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
            
            return learning_path
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(f"Error creating learning path: {error_msg}")
            raise ValueError(f"Failed to create learning path: {error_msg}")
    
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
        """Parse the learning path response"""
        sections = response.split("\n\n")
        parsed_data = {
            "objectives": [],
            "resources": [],
            "timeline": [],
            "exercises": [],
            "assessment": []
        }
        
        current_section = None
        for line in response.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if "1. Learning Objectives" in line or "Learning Objectives:" in line:
                current_section = "objectives"
                continue
            elif "2. Recommended Resources" in line or "Recommended Resources:" in line:
                current_section = "resources"
                continue
            elif "3. Timeline and Milestones" in line or "Timeline:" in line:
                current_section = "timeline"
                continue
            elif "4. Practice Exercises" in line or "Practice Exercises:" in line:
                current_section = "exercises"
                continue
            elif "5. Assessment Criteria" in line or "Assessment:" in line:
                current_section = "assessment"
                continue
            
            # Process line based on current section
            if current_section and line:
                # Remove numbering and bullet points
                cleaned_line = line.lstrip("0123456789.- *•►").strip()
                if cleaned_line:
                    parsed_data[current_section].append(cleaned_line)
        
        # Add default items if sections are empty
        if not parsed_data["objectives"]:
            parsed_data["objectives"] = ["Master fundamental concepts", "Build practical skills", "Complete real-world projects"]
        if not parsed_data["resources"]:
            parsed_data["resources"] = ["Online courses", "Practice exercises", "Documentation"]
        if not parsed_data["timeline"]:
            parsed_data["timeline"] = ["Week 1-2: Basics", "Week 3-4: Advanced concepts", "Week 5-6: Projects"]
        if not parsed_data["exercises"]:
            parsed_data["exercises"] = ["Basic exercises", "Intermediate challenges", "Advanced projects"]
        if not parsed_data["assessment"]:
            parsed_data["assessment"] = ["Knowledge tests", "Project evaluation", "Practical application"]
        
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
        """Update progress for a specific learning path"""
        # Implementation for updating progress
    
    def assess_progress(
        self,
        learning_path_id: str,
        user_reflection: str = "",
        user_id: Optional[str] = None
    ) -> Dict:
        """Assess progress on a learning path and provide recommendations"""
        # Implementation for progress assessment
    
    def get_user_learning_paths(self, user_id: str) -> List[Dict]:
        """Get all learning paths for a user"""
        # Implementation for retrieving learning paths 
    
    def _save_user_data(self, user_id: str, data_type: str, data: Dict) -> None:
        """Save user data to disk"""
        # Implementation for saving data
    
    def _save_learning_path(self, user_id: str, learning_path: Dict) -> None:
        """Save a learning path to disk"""
        # Implementation for saving learning paths
    
    def _load_learning_paths(self, user_id: str) -> None:
        """Load all learning paths for a user"""
        # Implementation for loading learning paths
    
    def _format_list_with_progress(self, items: List[str], completed_items: List[str]) -> str:
        """Format a list of items with completion status"""
        # Implementation for formatting progress lists 