import requests
from typing import Dict, List
from .base_agent import BaseAgent
from config.config import Config
from langchain.prompts import PromptTemplate

class JobSearchAgent(BaseAgent):
    def __init__(self, verbose: bool = False):
        super().__init__(
            role="Job Search Expert",
            goal="Find relevant job opportunities based on user skills and preferences",
            backstory="Expert in job market analysis and matching candidates with suitable positions",
            verbose=verbose
        )
        
        self.job_matching_prompt = PromptTemplate(
            input_variables=["job_description", "user_skills"],
            template="""
            Analyze the following job description and user skills to determine job fit:
            
            Job Description:
            {job_description}
            
            User Skills:
            {user_skills}
            
            Please provide:
            1. Match Score (0-100)
            2. Key Matching Skills
            3. Missing Skills
            4. Recommendations for Application
            """
        )
    
    def search_jobs(
        self, 
        keywords: str, 
        location: str = "", 
        country: str = "us",
        max_results: int = None
    ) -> List[Dict]:
        """
        Search for jobs using the Adzuna API
        
        Args:
            keywords (str): Search keywords (job title, skills, etc.)
            location (str): Location for job search
            country (str): Country code for search (default: us)
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Dict]: List of job postings
        """
        try:
            # Set default max results from config if not specified
            if max_results is None:
                max_results = Config.MAX_JOBS_PER_SEARCH
                
            # Build API URL
            base_url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
            params = {
                "app_id": Config.ADZUNA_APP_ID,
                "app_key": Config.ADZUNA_API_KEY,
                "results_per_page": max_results,
                "what": keywords,
                "where": location,
                "content-type": "application/json"
            }
            
            # Make API request
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            
            # Parse response
            jobs_data = response.json()
            
            # Extract relevant job information
            jobs = []
            for job in jobs_data.get("results", []):
                jobs.append({
                    "title": job.get("title"),
                    "company": job.get("company", {}).get("display_name"),
                    "location": job.get("location", {}).get("display_name"),
                    "description": job.get("description"),
                    "salary_min": job.get("salary_min"),
                    "salary_max": job.get("salary_max"),
                    "url": job.get("redirect_url")
                })
            
            self._log(f"Found {len(jobs)} matching jobs")
            return jobs
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
    def analyze_job_fit(self, job_description: str, user_skills: List[str]) -> Dict:
        """
        Analyze how well a job matches the user's skills
        
        Args:
            job_description (str): The job description to analyze
            user_skills (List[str]): List of user's skills
            
        Returns:
            Dict: Analysis of job fit
        """
        try:
            # Format skills for prompt
            skills_text = "\n".join(f"- {skill}" for skill in user_skills)
            
            # Get analysis from LLM using invoke instead of predict
            response = self.llm.invoke(
                self.job_matching_prompt.format(
                    job_description=job_description,
                    user_skills=skills_text
                )
            ).content
            
            # Parse response
            analysis = {
                "raw_analysis": response,
                "structured_data": self._parse_job_fit_response(response)
            }
            
            return analysis
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(error_msg)
            raise ValueError(error_msg)
    
    def _parse_job_fit_response(self, response: str) -> Dict:
        """Parse the job fit analysis response"""
        sections = response.split("\n\n")
        parsed_data = {
            "match_score": None,
            "matching_skills": [],
            "missing_skills": [],
            "recommendations": []
        }
        
        for section in sections:
            if "Match Score" in section:
                # Extract number from text (e.g., "Match Score: 85" -> 85)
                try:
                    parsed_data["match_score"] = int(section.split(":")[1].strip().split()[0])
                except:
                    pass
            elif "Key Matching Skills" in section:
                skills = section.split("\n")[1:]
                parsed_data["matching_skills"] = [s.strip("- ") for s in skills if s.strip()]
            elif "Missing Skills" in section:
                skills = section.split("\n")[1:]
                parsed_data["missing_skills"] = [s.strip("- ") for s in skills if s.strip()]
            elif "Recommendations" in section:
                recs = section.split("\n")[1:]
                parsed_data["recommendations"] = [r.strip("- ") for r in recs if r.strip()]
        
        return parsed_data
    
    def get_required_fields(self) -> List[str]:
        """Get required fields for job search"""
        return ["keywords"] 