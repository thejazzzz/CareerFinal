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
            Create a learning path for skill development:
            
            Skill: {skill}
            Current Level: {current_level}
            Target Level: {target_level}
            
            Please provide:
            1. Learning Objectives
            2. Recommended Resources (courses, books, projects)
            3. Timeline and Milestones
            4. Practice Exercises
            5. Assessment Criteria
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
        
        Args:
            skill (str): The skill to develop
            current_level (str): Current proficiency level
            target_level (str): Target proficiency level
            
        Returns:
            Dict: Detailed learning path and resources
        """
        try:
            # Get learning path from LLM using invoke instead of predict
            response = self.llm.invoke(
                self.learning_path_prompt.format(
                    skill=skill,
                    current_level=current_level,
                    target_level=target_level
                )
            ).content
            
            # Parse and structure the response
            learning_path = {
                "raw_response": response,
                "structured_data": self._parse_learning_path(response)
            }
            
            self._log(f"Created learning path for {skill}")
            return learning_path
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
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
        for section in sections:
            if "Learning Objectives" in section:
                current_section = "objectives"
            elif "Recommended Resources" in section:
                current_section = "resources"
            elif "Timeline and Milestones" in section:
                current_section = "timeline"
            elif "Practice Exercises" in section:
                current_section = "exercises"
            elif "Assessment Criteria" in section:
                current_section = "assessment"
            elif current_section and section.strip():
                items = [item.strip("- ") for item in section.split("\n") if item.strip()]
                parsed_data[current_section].extend(items)
        
        return parsed_data
    
    def get_required_fields(self) -> List[str]:
        """Get required fields for skills analysis"""
        return ["current_skills", "target_role"] 