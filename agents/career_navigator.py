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
            Based on the following profile, create a detailed career development plan:

            CURRENT PROFILE:
            - Role: {current_role}
            - Experience: {experience}
            - Skills: {skills}
            - Interests: {interests}
            - Career Goals: {goals}

            Please provide a structured analysis in the following format:

            CAREER PATH OPTIONS:
            1. [Path 1 with role progression]
            2. [Path 2 with role progression]
            3. [Path 3 with role progression]

            DEVELOPMENT TIMELINE:
            - Short-term (0-2 years): [Specific milestones and objectives]
            - Medium-term (2-5 years): [Specific milestones and objectives]
            - Long-term (5+ years): [Specific milestones and objectives]

            POTENTIAL CHALLENGES AND SOLUTIONS:
            Challenge 1: [Specific challenge]
            Solution 1: [Detailed solution]
            Challenge 2: [Specific challenge]
            Solution 2: [Detailed solution]

            INDUSTRY TRENDS AND OPPORTUNITIES:
            1. [Current trend and its impact]
            2. [Emerging opportunity and how to leverage it]
            3. [Future prediction and preparation strategy]

            REQUIRED SKILLS AND CERTIFICATIONS:
            Technical Skills:
            - [Key technical skill 1]
            - [Key technical skill 2]
            
            Soft Skills:
            - [Key soft skill 1]
            - [Key soft skill 2]
            
            Recommended Certifications:
            - [Relevant certification 1]
            - [Relevant certification 2]
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
            # Format inputs
            skills_text = ", ".join(skills)
            interests_text = ", ".join(interests)
            goals_text = ", ".join(goals)
            
            # Get career path analysis
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
            parsed_data = self._parse_career_path(response)
            
            # Validate parsed data
            if not any(parsed_data["path_options"]):
                self._log("Warning: No career path options found in response")
            if not any(parsed_data["timeline"]):
                self._log("Warning: No timeline entries found in response")
            if not any(parsed_data["trends"]):
                self._log("Warning: No industry trends found in response")
            
            career_path = {
                "raw_analysis": response,
                "structured_data": parsed_data
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
        """Parse the career path response with improved section detection"""
        parsed_data = {
            "path_options": [],
            "timeline": [],
            "challenges": [],
            "solutions": [],
            "trends": [],
            "required_skills": {
                "technical": [],
                "soft": [],
                "certifications": []
            }
        }
        
        # Split into major sections first
        sections = response.split("\n\n")
        current_section = None
        current_skill_type = None
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Identify major sections
            if "CAREER PATH OPTIONS:" in section:
                lines = section.split("\n")[1:]  # Skip the header
                for line in lines:
                    if line.strip() and any(c.isdigit() for c in line):
                        path = line.split(".", 1)[1].strip() if "." in line else line.strip()
                        if path:
                            parsed_data["path_options"].append(path)
            
            elif "DEVELOPMENT TIMELINE:" in section:
                lines = section.split("\n")[1:]  # Skip the header
                for line in lines:
                    if line.strip().startswith("-"):
                        timeline_item = line.strip("- ").strip()
                        if timeline_item:
                            parsed_data["timeline"].append(timeline_item)
            
            elif "POTENTIAL CHALLENGES AND SOLUTIONS:" in section:
                lines = section.split("\n")[1:]  # Skip the header
                challenge = None
                for line in lines:
                    line = line.strip()
                    if line.startswith("Challenge"):
                        challenge = line.split(":", 1)[1].strip() if ":" in line else line.strip()
                        if challenge:
                            parsed_data["challenges"].append(challenge)
                    elif line.startswith("Solution") and challenge:
                        solution = line.split(":", 1)[1].strip() if ":" in line else line.strip()
                        if solution:
                            parsed_data["solutions"].append(solution)
            
            elif "INDUSTRY TRENDS AND OPPORTUNITIES:" in section:
                lines = section.split("\n")[1:]  # Skip the header
                for line in lines:
                    if line.strip() and any(c.isdigit() for c in line):
                        trend = line.split(".", 1)[1].strip() if "." in line else line.strip()
                        if trend:
                            parsed_data["trends"].append(trend)
            
            elif "REQUIRED SKILLS AND CERTIFICATIONS:" in section:
                lines = section.split("\n")[1:]  # Skip the header
                current_type = None
                for line in lines:
                    line = line.strip()
                    if "Technical Skills:" in line:
                        current_type = "technical"
                    elif "Soft Skills:" in line:
                        current_type = "soft"
                    elif "Recommended Certifications:" in line:
                        current_type = "certifications"
                    elif line.startswith("-") and current_type:
                        skill = line.strip("- ").strip()
                        if skill:
                            parsed_data["required_skills"][current_type].append(skill)
        
        # Ensure we have matching challenges and solutions
        if len(parsed_data["challenges"]) > len(parsed_data["solutions"]):
            parsed_data["challenges"] = parsed_data["challenges"][:len(parsed_data["solutions"])]
        elif len(parsed_data["solutions"]) > len(parsed_data["challenges"]):
            parsed_data["solutions"] = parsed_data["solutions"][:len(parsed_data["challenges"])]
        
        # Add default values if sections are empty
        if not parsed_data["path_options"]:
            parsed_data["path_options"] = ["Career path information not available"]
        if not parsed_data["timeline"]:
            parsed_data["timeline"] = ["Timeline information not available"]
        if not parsed_data["challenges"] or not parsed_data["solutions"]:
            parsed_data["challenges"] = ["Challenge information not available"]
            parsed_data["solutions"] = ["Solution information not available"]
        if not parsed_data["trends"]:
            parsed_data["trends"] = ["Industry trend information not available"]
        
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
        
        # Add default values if sections are empty
        if not parsed_data["overview"]:
            parsed_data["overview"] = ["Role overview information not available"]
        if not parsed_data["requirements"]:
            parsed_data["requirements"] = ["Required skills information not available"]
        if not parsed_data["outlook"]:
            parsed_data["outlook"] = ["Industry outlook information not available"]
        if not parsed_data["salary"]:
            parsed_data["salary"] = ["Salary range information not available"]
        if not parsed_data["companies"]:
            parsed_data["companies"] = ["Key companies information not available"]
        
        return parsed_data
    
    def get_required_fields(self) -> List[str]:
        """Get required fields for career navigation"""
        return ["current_role", "experience", "goals"] 