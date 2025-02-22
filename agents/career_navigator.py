from typing import Dict, List
from .base_agent import BaseAgent
from langchain.prompts import PromptTemplate

class CareerNavigatorAgent(BaseAgent):
    def __init__(self, verbose: bool = False):
        super().__init__(
            role="Career Navigator",
            goal="Create personalized career paths and progression strategies",
            backstory="Expert in career planning and professional development",
            verbose=verbose
        )
        
        self.career_path_prompt = PromptTemplate(
            input_variables=["current_role", "experience", "skills", "interests", "goals"],
            template="""
            Create a personalized career path based on the following information:
            
            Current Role: {current_role}
            Experience: {experience}
            Skills: {skills}
            Interests: {interests}
            Career Goals: {goals}
            
            Please provide:
            1. Career Path Options (3-5 paths)
            2. Required Skills and Qualifications
            3. Timeline and Milestones
            4. Potential Challenges and Solutions
            5. Industry Trends and Opportunities
            """
        )
        
        self.role_analysis_prompt = PromptTemplate(
            input_variables=["target_role", "industry"],
            template="""
            Analyze the following role and industry:
            
            Target Role: {target_role}
            Industry: {industry}
            
            Please provide:
            1. Role Overview and Responsibilities
            2. Required Skills and Experience
            3. Industry Outlook and Trends
            4. Salary Range and Growth Potential
            5. Key Companies and Organizations
            """
        )
    
    def create_career_path(
        self,
        current_role: str,
        experience: str,
        skills: List[str],
        interests: List[str],
        goals: List[str]
    ) -> Dict:
        """
        Create a personalized career path based on user profile
        
        Args:
            current_role (str): Current job role
            experience (str): Years and type of experience
            skills (List[str]): List of current skills
            interests (List[str]): Professional interests
            goals (List[str]): Career goals
            
        Returns:
            Dict: Career path recommendations and analysis
        """
        try:
            # Format inputs for prompt
            skills_text = "\n".join(f"- {skill}" for skill in skills)
            interests_text = "\n".join(f"- {interest}" for interest in interests)
            goals_text = "\n".join(f"- {goal}" for goal in goals)
            
            # Get career path analysis from LLM using invoke instead of predict
            response = self.llm.invoke(
                self.career_path_prompt.format(
                    current_role=current_role,
                    experience=experience,
                    skills=skills_text,
                    interests=interests_text,
                    goals=goals_text
                )
            ).content
            
            # Parse and structure the response
            career_path = {
                "raw_analysis": response,
                "structured_data": self._parse_career_path(response)
            }
            
            self._log(f"Created career path plan for {current_role}")
            return career_path
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
    def analyze_role(self, target_role: str, industry: str) -> Dict:
        """
        Analyze a specific role and industry
        
        Args:
            target_role (str): Role to analyze
            industry (str): Industry context
            
        Returns:
            Dict: Role analysis and insights
        """
        try:
            # Get role analysis from LLM using invoke instead of predict
            response = self.llm.invoke(
                self.role_analysis_prompt.format(
                    target_role=target_role,
                    industry=industry
                )
            ).content
            
            # Parse and structure the response
            analysis = {
                "raw_analysis": response,
                "structured_data": self._parse_role_analysis(response)
            }
            
            self._log(f"Completed analysis for {target_role} in {industry}")
            return analysis
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
    def _parse_career_path(self, response: str) -> Dict:
        """Parse the career path response"""
        sections = response.split("\n\n")
        parsed_data = {
            "path_options": [],
            "required_skills": [],
            "timeline": [],
            "challenges": [],
            "trends": []
        }
        
        current_section = None
        for section in sections:
            if "Career Path Options" in section:
                current_section = "path_options"
            elif "Required Skills" in section:
                current_section = "required_skills"
            elif "Timeline" in section:
                current_section = "timeline"
            elif "Potential Challenges" in section:
                current_section = "challenges"
            elif "Industry Trends" in section:
                current_section = "trends"
            elif current_section and section.strip():
                items = [item.strip("- ") for item in section.split("\n") if item.strip()]
                parsed_data[current_section].extend(items)
        
        return parsed_data
    
    def _parse_role_analysis(self, response: str) -> Dict:
        """Parse the role analysis response"""
        sections = response.split("\n\n")
        parsed_data = {
            "overview": [],
            "requirements": [],
            "outlook": [],
            "salary": [],
            "companies": []
        }
        
        current_section = None
        for section in sections:
            if "Role Overview" in section:
                current_section = "overview"
            elif "Required Skills" in section:
                current_section = "requirements"
            elif "Industry Outlook" in section:
                current_section = "outlook"
            elif "Salary Range" in section:
                current_section = "salary"
            elif "Key Companies" in section:
                current_section = "companies"
            elif current_section and section.strip():
                items = [item.strip("- ") for item in section.split("\n") if item.strip()]
                parsed_data[current_section].extend(items)
        
        return parsed_data
    
    def get_required_fields(self) -> List[str]:
        """Get required fields for career navigation"""
        return ["current_role", "experience", "goals"] 