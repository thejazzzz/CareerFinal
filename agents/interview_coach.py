from typing import Dict, List
from .base_agent import BaseAgent
from langchain.prompts import PromptTemplate
import re

class InterviewCoachAgent(BaseAgent):
    def __init__(self, verbose: bool = False):
        super().__init__(
            role="Interview Coach",
            goal="Conduct mock interviews and provide detailed feedback",
            backstory="Expert interview coach with experience in technical and behavioral interviews",
            verbose=verbose
        )
        
        self.question_generator_prompt = PromptTemplate(
            input_variables=["role", "experience_level", "skills", "interview_type"],
            template="""
            Generate relevant interview questions for the following:
            
            Role: {role}
            Experience Level: {experience_level}
            Required Skills: {skills}
            Interview Type: {interview_type}
            
            Please provide:
            1. Technical Questions (with expected answers)
            2. Behavioral Questions (with STAR format guidance)
            3. Role-specific Scenarios
            4. Questions to Ask the Interviewer
            """
        )
        
        self.answer_evaluation_prompt = PromptTemplate(
            input_variables=["question", "answer", "role", "experience_level"],
            template="""
            Evaluate the following interview response:
            
            Question: {question}
            Candidate's Answer: {answer}
            Role: {role}
            Experience Level: {experience_level}
            
            Please provide:
            1. Overall Score (0-100)
            2. Strengths in the Response
            3. Areas for Improvement
            4. Sample Better Response
            5. Additional Tips
            """
        )
    
    def generate_interview_questions(
        self,
        role: str,
        experience_level: str,
        skills: List[str],
        interview_type: str = "full"  # Options: technical, behavioral, full
    ) -> Dict:
        """
        Generate relevant interview questions based on role and experience
        
        Args:
            role (str): Target job role
            experience_level (str): Years/level of experience
            skills (List[str]): Required skills for the role
            interview_type (str): Type of interview questions to generate
            
        Returns:
            Dict: Structured interview questions and guidance
        """
        try:
            # Format skills for prompt
            skills_text = "\n".join(f"- {skill}" for skill in skills)
            
            # Generate questions using LLM
            response = self.llm.invoke(
                self.question_generator_prompt.format(
                    role=role,
                    experience_level=experience_level,
                    skills=skills_text,
                    interview_type=interview_type
                )
            ).content
            
            # Parse and structure the response
            questions = {
                "raw_response": response,
                "structured_data": self._parse_questions(response)
            }
            
            self._log(f"Generated interview questions for {role}")
            return questions
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
    def evaluate_response(
        self,
        question: str,
        answer: str,
        role: str,
        experience_level: str
    ) -> Dict:
        """
        Evaluate a candidate's interview response
        
        Args:
            question (str): Interview question
            answer (str): Candidate's response
            role (str): Target job role
            experience_level (str): Years/level of experience
            
        Returns:
            Dict: Evaluation and feedback
        """
        try:
            # Get evaluation from LLM
            response = self.llm.invoke(
                self.answer_evaluation_prompt.format(
                    question=question,
                    answer=answer,
                    role=role,
                    experience_level=experience_level
                )
            ).content
            
            # Parse and structure the response
            evaluation = {
                "raw_response": response,
                "structured_data": self._parse_evaluation(response)
            }
            
            self._log("Completed response evaluation")
            return evaluation
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
    def _parse_questions(self, response: str) -> Dict:
        """Parse the generated interview questions with improved error handling"""
        parsed_data = {
            "technical_questions": [],
            "behavioral_questions": [],
            "scenario_questions": [],
            "questions_to_ask": []
        }
        
        try:
            # Split the response into sections
            sections = response.split('\n')
            current_section = None
            
            for line in sections:
                line = line.strip()
                if not line:
                    continue
                
                # Check for section headers
                if "Technical Questions:" in line:
                    current_section = "technical_questions"
                    continue
                elif "Behavioral Questions:" in line:
                    current_section = "behavioral_questions"
                    continue
                elif "Role-specific Scenarios:" in line:
                    current_section = "scenario_questions"
                    continue
                elif "Questions to Ask" in line:
                    current_section = "questions_to_ask"
                    continue
                
                # Extract questions
                # Remove leading numbers and special characters
                if line and current_section:
                    # Remove leading numbers (1., 2., etc.)
                    question = re.sub(r'^\d+\.\s*', '', line).strip()
                    
                    # Skip if it's empty after cleaning
                    if not question:
                        continue
                        
                    # Skip if it's a section header
                    if any(header in question for header in ["Technical Questions:", "Behavioral Questions:", 
                                                           "Role-specific Scenarios:", "Questions to Ask"]):
                        continue
                    
                    # Add the question to the appropriate section
                    if len(question) > 5:  # Ensure it's a valid question
                        parsed_data[current_section].append(question)
            
            # Debug output
            for section, questions in parsed_data.items():
                print(f"Parsed {section}: {len(questions)} questions")
                for q in questions:
                    print(f"- {q}")
            
            return parsed_data
            
        except Exception as e:
            print(f"Error parsing questions: {str(e)}")
            print(f"Raw response being parsed: {response}")
            return parsed_data
    
    def _parse_evaluation(self, response: str) -> Dict:
        """Parse the response evaluation"""
        sections = response.split("\n\n")
        parsed_data = {
            "score": None,
            "strengths": [],
            "improvements": [],
            "better_response": "",
            "tips": []
        }
        
        current_section = None
        for section in sections:
            if "Overall Score" in section:
                try:
                    parsed_data["score"] = int(section.split(":")[1].strip().split()[0])
                except:
                    pass
            elif "Strengths" in section:
                current_section = "strengths"
            elif "Areas for Improvement" in section:
                current_section = "improvements"
            elif "Sample Better Response" in section:
                current_section = "better_response"
                parsed_data["better_response"] = section.split("\n", 1)[1].strip()
            elif "Additional Tips" in section:
                current_section = "tips"
            elif current_section in ["strengths", "improvements", "tips"] and section.strip():
                items = [item.strip("- ") for item in section.split("\n") if item.strip()]
                parsed_data[current_section].extend(items)
        
        return parsed_data
    
    def get_required_fields(self) -> List[str]:
        """Get required fields for interview coaching"""
        return ["role", "experience_level"] 