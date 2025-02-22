import os
from typing import Dict
import pdfplumber
from langchain.prompts import PromptTemplate
from .base_agent import BaseAgent
from config.config import Config

class ResumeAnalyzerAgent(BaseAgent):
    def __init__(self, verbose: bool = False):
        super().__init__(
            role="Resume Analyzer",
            goal="Extract and analyze key information from resumes",
            backstory="Expert in parsing resumes and identifying key skills, experience, and qualifications",
            verbose=verbose
        )
        
        self.analysis_prompt = PromptTemplate(
            input_variables=["resume_text"],
            template="""
            Analyze the following resume and extract key information in a structured format:
            
            Resume Text:
            {resume_text}
            
            Please extract and organize the following information:
            1. Professional Summary (2-3 sentences)
            2. Skills (List all technical and soft skills)
            3. Work Experience (Company, Role, Duration, Key Achievements)
            4. Education
            
            Also provide:
            - Key Strengths (Top 3-5)
            - Areas for Improvement (2-3 suggestions)
            """
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from a PDF resume"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                return "\n".join(
                    page.extract_text() 
                    for page in pdf.pages 
                    if page.extract_text()
                )
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {str(e)}")
    
    def analyze_resume(self, resume_text: str) -> Dict:
        """Analyze resume text and extract structured information"""
        try:
            # Get analysis from LLM using invoke instead of predict
            response = self.llm.invoke(
                self.analysis_prompt.format(resume_text=resume_text)
            ).content
            
            # Parse and structure the response
            analysis = {
                "raw_analysis": response,
                "structured_data": self._parse_llm_response(response)
            }
            
            self._log("Successfully analyzed resume")
            return analysis
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Parse the LLM response into a structured format"""
        sections = response.split("\n\n")
        parsed_data = {
            "professional_summary": [],
            "skills": [],
            "work_experience": [],
            "education": [],
            "key_strengths": [],
            "areas_for_improvement": []
        }
        
        current_section = None
        for section in sections:
            if "Professional Summary" in section:
                current_section = "professional_summary"
            elif "Skills" in section:
                current_section = "skills"
            elif "Work Experience" in section:
                current_section = "work_experience"
            elif "Education" in section:
                current_section = "education"
            elif "Key Strengths" in section:
                current_section = "key_strengths"
            elif "Areas for Improvement" in section:
                current_section = "areas_for_improvement"
            elif current_section and section.strip():
                items = [item.strip("- ") for item in section.split("\n") if item.strip()]
                parsed_data[current_section].extend(items)
        
        return parsed_data
    
    def process_resume(self, file_path: str) -> Dict:
        """Process a resume file and return structured analysis"""
        try:
            # Validate file size
            if os.path.getsize(file_path) > Config.MAX_RESUME_SIZE_MB * 1024 * 1024:
                raise ValueError(f"Resume file size exceeds {Config.MAX_RESUME_SIZE_MB}MB limit")
            
            # Extract text
            resume_text = self.extract_text_from_pdf(file_path)
            
            # Analyze resume
            return self.analyze_resume(resume_text)
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg) 