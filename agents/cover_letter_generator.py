from typing import Dict, List
from .base_agent import BaseAgent
from langchain.prompts import PromptTemplate

class CoverLetterGeneratorAgent(BaseAgent):
    def __init__(self, verbose: bool = False):
        super().__init__(
            role="Cover Letter Generator",
            goal="Create personalized and compelling cover letters",
            backstory="Expert in professional writing and tailoring cover letters to specific job requirements",
            verbose=verbose
        )
        
        self.cover_letter_prompt = PromptTemplate(
            input_variables=["job_description", "candidate_info", "company_name", "style"],
            template="""
            Generate a professional cover letter based on the following:
            
            Job Description:
            {job_description}
            
            Candidate Information:
            {candidate_info}
            
            Company: {company_name}
            Style: {style}
            
            Please write a compelling cover letter that:
            1. Addresses key job requirements
            2. Highlights relevant experience and skills
            3. Shows enthusiasm for the role and company
            4. Maintains a professional yet {style} tone
            5. Includes a strong opening and closing
            """
        )
        
        self.letter_improvement_prompt = PromptTemplate(
            input_variables=["cover_letter", "focus_areas"],
            template="""
            Review and improve the following cover letter focusing on:
            {focus_areas}
            
            Cover Letter:
            {cover_letter}
            
            Please provide:
            1. Improved Version
            2. Specific Enhancements Made
            3. Additional Suggestions
            """
        )
    
    def generate_cover_letter(
        self,
        job_description: str,
        candidate_info: Dict,
        company_name: str,
        style: str = "professional"  # Options: professional, enthusiastic, concise
    ) -> Dict:
        """
        Generate a customized cover letter
        
        Args:
            job_description (str): Full job posting description
            candidate_info (Dict): Candidate's background information
            company_name (str): Company name
            style (str): Desired tone/style of the letter
            
        Returns:
            Dict: Generated cover letter and analysis
        """
        try:
            # Format candidate info
            candidate_text = "\n".join([
                f"Experience: {candidate_info.get('experience', '')}",
                f"Skills: {', '.join(candidate_info.get('skills', []))}",
                f"Achievements: {', '.join(candidate_info.get('achievements', []))}"
            ])
            
            # Generate cover letter using LLM
            response = self.llm.invoke(
                self.cover_letter_prompt.format(
                    job_description=job_description,
                    candidate_info=candidate_text,
                    company_name=company_name,
                    style=style
                )
            ).content
            
            # Parse and structure the response
            cover_letter = {
                "raw_content": response,
                "structured_data": self._parse_cover_letter(response)
            }
            
            self._log(f"Generated cover letter for {company_name}")
            return cover_letter
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
    def improve_cover_letter(
        self,
        cover_letter: str,
        focus_areas: List[str]
    ) -> Dict:
        """
        Improve an existing cover letter
        
        Args:
            cover_letter (str): Existing cover letter content
            focus_areas (List[str]): Areas to focus improvement on
            
        Returns:
            Dict: Improved version and suggestions
        """
        try:
            # Format focus areas
            focus_text = "\n".join(f"- {area}" for area in focus_areas)
            
            # Get improvements from LLM
            response = self.llm.invoke(
                self.letter_improvement_prompt.format(
                    cover_letter=cover_letter,
                    focus_areas=focus_text
                )
            ).content
            
            # Parse and structure the response
            improvements = {
                "raw_content": response,
                "structured_data": self._parse_improvements(response)
            }
            
            self._log("Generated cover letter improvements")
            return improvements
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
    def _parse_cover_letter(self, response: str) -> Dict:
        """Parse the generated cover letter"""
        sections = response.split("\n\n")
        parsed_data = {
            "greeting": "",
            "opening": "",
            "body": [],
            "closing": "",
            "signature": ""
        }
        
        current_section = None
        for section in sections:
            if "Dear" in section or "To" in section:
                parsed_data["greeting"] = section.strip()
                current_section = "opening"
            elif "Sincerely" in section or "Best" in section or "Regards" in section:
                parsed_data["closing"] = section.strip()
                current_section = "signature"
            elif current_section == "opening":
                parsed_data["opening"] = section.strip()
                current_section = "body"
            elif current_section == "body":
                parsed_data["body"].append(section.strip())
            elif current_section == "signature":
                parsed_data["signature"] = section.strip()
        
        return parsed_data
    
    def _parse_improvements(self, response: str) -> Dict:
        """Parse the improvement suggestions"""
        sections = response.split("\n\n")
        parsed_data = {
            "improved_version": "",
            "enhancements": [],
            "suggestions": []
        }
        
        current_section = None
        for section in sections:
            if "Improved Version" in section:
                current_section = "improved_version"
                parsed_data["improved_version"] = section.split("\n", 1)[1].strip()
            elif "Specific Enhancements" in section:
                current_section = "enhancements"
            elif "Additional Suggestions" in section:
                current_section = "suggestions"
            elif current_section in ["enhancements", "suggestions"] and section.strip():
                items = [item.strip("- ") for item in section.split("\n") if item.strip()]
                parsed_data[current_section].extend(items)
        
        return parsed_data
    
    def get_required_fields(self) -> List[str]:
        """Get required fields for cover letter generation"""
        return ["job_description", "candidate_info", "company_name"] 