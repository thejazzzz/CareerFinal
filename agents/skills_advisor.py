from typing import Dict, List
from .base_agent import BaseAgent
from langchain.prompts import PromptTemplate

class SkillsAdvisorAgent(BaseAgent):
    def __init__(self, verbose: bool = False):
        super().__init__(
            role="Skills Development Advisor",
            goal="Analyze skill gaps and provide personalized learning recommendations",
            backstory="Expert in career development and skill enhancement strategies",
            verbose=verbose
        )
        
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
        job_requirements: List[str]
    ) -> Dict:
        """
        Analyze gaps between current skills and target role requirements
        
        Args:
            current_skills (List[str]): List of current skills
            target_role (str): Target job role
            job_requirements (List[str]): Required skills for target role
            
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
            return analysis
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
    def create_learning_path(
        self,
        skill: str,
        current_level: str = "beginner",
        target_level: str = "proficient"
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
            
            learning_path = {
                "raw_response": response,
                "structured_data": structured_data
            }
            
            # Validate structured data
            if not all(key in structured_data for key in ["objectives", "resources", "timeline", "exercises", "assessment"]):
                raise ValueError("Missing required sections in learning path")
            
            if not all(len(structured_data[key]) > 0 for key in structured_data):
                raise ValueError("Empty sections found in learning path")
            
            return learning_path
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(f"Error creating learning path: {error_msg}")
            raise ValueError(f"Failed to create learning path: {error_msg}")
    
    def _parse_skills_analysis(self, response: str) -> Dict:
        """Parse the skills analysis response"""
        sections = response.split("\n\n")
        parsed_data = {
            "skill_gaps": [],
            "priority_skills": [],
            "learning_resources": [],
            "transition_strategy": []
        }
        
        current_section = None
        for section in sections:
            if "Skill Gap Analysis" in section:
                current_section = "skill_gaps"
            elif "Priority Skills" in section:
                current_section = "priority_skills"
            elif "Learning Resources" in section:
                current_section = "learning_resources"
            elif "Career Transition Strategy" in section:
                current_section = "transition_strategy"
            elif current_section and section.strip():
                items = [item.strip("- ") for item in section.split("\n") if item.strip()]
                parsed_data[current_section].extend(items)
        
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