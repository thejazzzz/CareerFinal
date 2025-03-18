from typing import Dict, List
from .base_agent import BaseAgent
from langchain.prompts import PromptTemplate
import re

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
            Analyze the following role and industry in detail:
            
            Target Role: {target_role}
            Industry: {industry}
            
            Please provide a comprehensive analysis with the following sections (use bullet points for each section):

            1. Role Overview and Responsibilities:
            - [Detailed description of the role]
            - [Key responsibilities and day-to-day tasks]
            - [Where this role fits in organizational structure]
            
            2. Required Skills and Experience:
            - [Technical skills needed] 
            - [Soft skills required]
            - [Required years of experience]
            - [Educational requirements]
            
            3. Industry Outlook and Trends:
            - [Current state of the industry]
            - [Projected growth trajectory]
            - [Key trends affecting this role]
            
            4. Salary Range and Growth Potential:
            - [Entry-level salary range]
            - [Mid-career salary expectations]
            - [Senior-level compensation]
            - [Career advancement paths]
            
            5. Key Companies and Organizations:
            - [Top companies that hire for this role]
            - [Industries where this role is in demand]
            - [Notable employers to target]

            Make your response detailed, practical, and specific to this exact role and industry.
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
            
            # Debug log
            self._log(f"Raw career path response (first 200 chars): {response[:200]}...")
            
            # Parse and structure the response
            parsed_data = self._parse_career_path(response)
            
            # Validate parsed data
            if not any(parsed_data["path_options"]):
                self._log("Warning: No career path options found in response")
            if not any(parsed_data["timeline"]):
                self._log("Warning: No timeline entries found in response")
            if not any(parsed_data["trends"]):
                self._log("Warning: No industry trends found in response")
            
            # Log skills data for debugging
            self._log(f"Technical skills found: {len(parsed_data['required_skills']['technical'])}")
            self._log(f"Soft skills found: {len(parsed_data['required_skills']['soft'])}")
            self._log(f"Certifications found: {len(parsed_data['required_skills']['certifications'])}")
            
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
            
            # Log the raw response for debugging
            self._log(f"Raw role analysis response for {target_role} (first 200 chars): {response[:200]}...")
            
            # Parse and structure the response
            analysis = {
                "raw_analysis": response,
                "structured_data": self._parse_role_analysis(response)
            }
            
            # Validate the structure
            for key, value in analysis["structured_data"].items():
                self._log(f"Section '{key}' has {len(value)} items")
            
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
            
            elif "REQUIRED SKILLS AND CERTIFICATIONS:" in section or "REQUIRED SKILLS:" in section:
                self._log("Found skills section, parsing...")
                lines = section.split("\n")[1:]  # Skip the header
                current_type = None
                
                # Check if this section has subsections
                has_subsections = any("Technical Skills:" in line or "Soft Skills:" in line or 
                                     "Technical:" in line or "Soft:" in line or
                                     "Certifications:" in line for line in lines)
                
                if has_subsections:
                    for line in lines:
                        line = line.strip()
                        # Identify subsection types with more flexible matching
                        if any(term in line for term in ["Technical Skills:", "Technical:"]):
                            current_type = "technical"
                            self._log("Found technical skills subsection")
                        elif any(term in line for term in ["Soft Skills:", "Soft:", "Non-Technical:"]):
                            current_type = "soft"
                            self._log("Found soft skills subsection")
                        elif any(term in line for term in ["Recommended Certifications:", "Certifications:", "Certification:"]):
                            current_type = "certifications"
                            self._log("Found certifications subsection")
                        # Extract skills from bullet points
                        elif line.startswith("-") or line.startswith("•") or line.startswith("*"):
                            skill = line.strip("- •*").strip()
                            if skill and current_type:
                                parsed_data["required_skills"][current_type].append(skill)
                                self._log(f"Added {current_type} skill: {skill}")
                else:
                    # If there are no clear subsections, try to categorize skills by keywords
                    self._log("No clear skill subsections, attempting to categorize by keywords")
                    for line in lines:
                        line = line.strip()
                        if line.startswith("-") or line.startswith("•") or line.startswith("*"):
                            skill = line.strip("- •*").strip()
                            if not skill:
                                continue
                                
                            # Attempt to categorize by keywords
                            if any(term in skill.lower() for term in ["degree", "certification", "certified", "certificate", "diploma"]):
                                parsed_data["required_skills"]["certifications"].append(skill)
                                self._log(f"Categorized as certification: {skill}")
                            elif any(term in skill.lower() for term in ["communication", "leadership", "teamwork", "problem-solving", 
                                                                      "collaboration", "interpersonal", "time management"]):
                                parsed_data["required_skills"]["soft"].append(skill)
                                self._log(f"Categorized as soft skill: {skill}")
                            else:
                                # Default to technical
                                parsed_data["required_skills"]["technical"].append(skill)
                                self._log(f"Categorized as technical skill: {skill}")
        
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
            
        # Add default values for skills sections if they're empty
        if not parsed_data["required_skills"]["technical"]:
            parsed_data["required_skills"]["technical"] = ["Technical skills information not available"]
        if not parsed_data["required_skills"]["soft"]:
            parsed_data["required_skills"]["soft"] = ["Soft skills information not available"]
        if not parsed_data["required_skills"]["certifications"]:
            parsed_data["required_skills"]["certifications"] = ["Certification information not available"]
        
        return parsed_data
    
    def _parse_role_analysis(self, response: str) -> Dict:
        """Parse the role analysis response"""
        parsed_data = {
            "overview": [],
            "requirements": [],
            "outlook": [],
            "salary": [],
            "companies": []
        }
        
        # First try to split by numbered sections
        section_pattern = r'(\d+\.\s*[^:]+:)'
        sections = re.split(section_pattern, response)
        
        # If we have well-formatted numbered sections
        if len(sections) > 1:
            self._log("Parsing role analysis using section pattern")
            current_section = None
            for i, section in enumerate(sections):
                section = section.strip()
                if not section:
                    continue
                
                # Check if this is a section header
                if re.match(r'^\d+\.\s*', section):
                    section_lower = section.lower()
                    if 'overview' in section_lower or 'responsibilities' in section_lower:
                        current_section = "overview"
                    elif 'skills' in section_lower or 'required' in section_lower or 'experience' in section_lower:
                        current_section = "requirements"
                    elif 'outlook' in section_lower or 'trends' in section_lower:
                        current_section = "outlook"
                    elif 'salary' in section_lower or 'compensation' in section_lower:
                        current_section = "salary"
                    elif 'companies' in section_lower or 'organizations' in section_lower or 'employers' in section_lower:
                        current_section = "companies"
                elif current_section and i < len(sections) - 1:
                    # This is the content of a section
                    lines = [line.strip() for line in section.split('\n') if line.strip()]
                    # Extract items that look like bullet points
                    for line in lines:
                        # If line starts with bullet point or dash
                        if line.startswith('-') or line.startswith('•'):
                            item = line[1:].strip()
                            if item:
                                parsed_data[current_section].append(item)
                        # If line starts with number and period
                        elif re.match(r'^\d+\.', line):
                            item = re.sub(r'^\d+\.', '', line).strip()
                            if item:
                                parsed_data[current_section].append(item)
                        # If it's a substantial line, include it even without bullet point
                        elif len(line) > 10 and not line.startswith('http'):
                            parsed_data[current_section].append(line)
        
        # If the above parsing method didn't work, try the simpler approach
        if not any(len(items) for items in parsed_data.values()):
            self._log("Fallback to simple parsing for role analysis")
            sections = response.split("\n\n")
            current_section = None
            for section in sections:
                if not section.strip():
                    continue
                
                section_lower = section.lower()
                if any(term in section_lower for term in ["role overview", "responsibilities", "1."]):
                    current_section = "overview"
                elif any(term in section_lower for term in ["required skills", "experience", "2."]):
                    current_section = "requirements"
                elif any(term in section_lower for term in ["industry outlook", "trends", "3."]):
                    current_section = "outlook"
                elif any(term in section_lower for term in ["salary", "compensation", "4."]):
                    current_section = "salary"
                elif any(term in section_lower for term in ["key companies", "organizations", "5."]):
                    current_section = "companies"
                
                if current_section:
                    lines = [line.strip() for line in section.split('\n') if line.strip()]
                    # Skip the first line if it's likely a section header
                    start_idx = 1 if len(lines) > 1 and any(term in lines[0].lower() 
                                                          for term in ["overview", "skills", "outlook", "salary", "companies"]) else 0
                    
                    for line in lines[start_idx:]:
                        # Process bullet points and numbered items
                        if line.startswith('-') or line.startswith('•'):
                            item = line[1:].strip()
                            if item:
                                parsed_data[current_section].append(item)
                        elif re.match(r'^\d+\.', line):
                            item = re.sub(r'^\d+\.', '', line).strip()
                            if item:
                                parsed_data[current_section].append(item)
                        # Include substantial non-bullet lines as well
                        elif len(line) > 10:
                            parsed_data[current_section].append(line)
        
        # Add default values if sections are empty
        if not parsed_data["overview"]:
            parsed_data["overview"] = ["Role overview information not available. Please try with a more specific job title."]
        if not parsed_data["requirements"]:
            parsed_data["requirements"] = ["Required skills information not available. Please try with a more specific job title."]
        if not parsed_data["outlook"]:
            parsed_data["outlook"] = ["Industry outlook information not available. Please try with a more specific industry."]
        if not parsed_data["salary"]:
            parsed_data["salary"] = ["Salary range information not available. Please try with a more specific job title and industry."]
        if not parsed_data["companies"]:
            parsed_data["companies"] = ["Key companies information not available. Please try with a more specific industry."]
        
        return parsed_data
    
    def get_required_fields(self) -> List[str]:
        """Get required fields for career navigation"""
        return ["current_role", "experience", "goals"] 