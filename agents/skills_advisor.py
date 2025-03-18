from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from langchain.prompts import PromptTemplate
import os
import datetime
import json
import re
import uuid

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
            
            Please provide a DETAILED analysis with the following sections (be specific and comprehensive):
            
            1. Skill Gap Analysis:
            - Identify ALL missing skills required for the target role
            - For each skill gap, briefly explain its importance
            
            2. Priority Skills to Develop:
            - List at least 3-5 most critical skills to focus on first
            - For each priority skill, explain why it's important
            
            3. Learning Resources and Timeline:
            - Provide at least 5 SPECIFIC learning resources (include actual course names, book titles, platforms)
            - Include links or platforms where these resources can be found
            - Suggest estimated timeline for acquiring each priority skill
            
            4. Career Transition Strategy:
            - Outline at least 5 concrete steps to transition to the target role
            - Include networking strategies, portfolio development, and interview preparation advice
            
            Make your response detailed, specific, and immediately actionable.
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
                "structured_data": self._parse_skills_analysis(response),
                "target_role": target_role  # Add target role to response for context
            }
            
            # Ensure we have resources even if parsing failed to find them
            if not analysis["structured_data"]["learning_resources"]:
                analysis["structured_data"]["learning_resources"] = [
                    f"Online courses related to {target_role} on platforms like Coursera, Udemy, or LinkedIn Learning",
                    f"Books and publications about {target_role} roles and responsibilities",
                    f"Industry certifications relevant to {target_role}",
                    "Join professional communities and forums in your field",
                    "Follow industry leaders and experts on social media"
                ]
                self._log(f"Added default learning resources for {target_role}")
            
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
        skill_name: str,
        target_role: str,
        skill_level: str = "beginner",
        resources_preference: str = "balanced",
        time_commitment: str = "medium",
        existing_skills: List[str] = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """Create a personalized learning path for a skill"""
        try:
            # Generate a unique ID for this learning path
            path_id = str(uuid.uuid4())
            
            # Set up user preferences
            if existing_skills is None:
                existing_skills = []
            
            # Calculate estimated time based on time commitment
            time_mapping = {
                "low": {"hours_per_week": 2, "total_weeks": 4},
                "medium": {"hours_per_week": 5, "total_weeks": 6},
                "high": {"hours_per_week": 10, "total_weeks": 8}
            }
            
            time_estimate = time_mapping.get(time_commitment.lower(), time_mapping["medium"])
            
            # Create learning path skeleton with user preferences
            learning_path = {
                "id": path_id,
                "skill_name": skill_name,
                "target_role": target_role,
                "skill_level": skill_level,
                "resources_preference": resources_preference,
                "time_commitment": time_commitment,
                "estimated_hours_per_week": time_estimate["hours_per_week"],
                "estimated_weeks": time_estimate["total_weeks"],
                "existing_skills": existing_skills,
                "date_created": datetime.datetime.now().isoformat(),
                "last_updated": datetime.datetime.now().isoformat(),
                "structured_data": {
                    "objectives": [],
                    "resources": [],
                    "exercises": [],
                    "timeline": [],  # Add timeline field
                    "assessment": []  # Add assessment field
                },
                "progress": {
                    "completed_objectives": [],
                    "completed_resources": [],
                    "completed_exercises": [],
                    "time_spent_hours": 0,
                    "progress_percentage": 0,
                    "last_updated": datetime.datetime.now().isoformat()
                }
            }
            
            # Generate structured content based on skill
            learning_path = self._generate_learning_path_content(learning_path)
            
            # Save the learning path
            self.learning_paths[path_id] = learning_path
            
            # If a user_id is provided, save the learning path to their data
            if user_id:
                self._save_learning_path(user_id, learning_path)
            
            # Debug log
            self._log(f"Created learning path for {skill_name} (ID: {path_id})")
            
            return learning_path
            
        except Exception as e:
            error_msg = self._format_error(e)
            self._log(f"Error creating learning path: {error_msg}")
            
            # Return a minimal valid response structure even in case of error
            timestamp = datetime.datetime.now()
            return {
                "id": f"error_{timestamp.strftime('%Y%m%d%H%M%S')}",
                "skill_name": skill_name,
                "target_role": target_role,
                "skill_level": skill_level,
                "resources_preference": resources_preference,
                "time_commitment": time_estimate["total_weeks"],
                "estimated_hours_per_week": time_estimate["hours_per_week"],
                "estimated_weeks": time_estimate["total_weeks"],
                "date_created": timestamp.isoformat(),
                "error": str(e),
                "structured_data": {
                    "objectives": ["Master fundamental concepts", "Build practical skills", "Complete real-world projects"],
                    "resources": [
                        {"id": str(uuid.uuid4()), "title": "Online courses", "description": "Structured online learning", "url": "https://www.coursera.org/"},
                        {"id": str(uuid.uuid4()), "title": "Books and guides", "description": "Comprehensive learning materials", "url": "https://www.goodreads.com/"},
                        {"id": str(uuid.uuid4()), "title": "Practice resources", "description": "Interactive exercises and projects", "url": "https://www.codecademy.com/"},
                        {"id": str(uuid.uuid4()), "title": "Community forums", "description": "Connect with others learning the same skills", "url": "https://stackoverflow.com/"},
                        {"id": str(uuid.uuid4()), "title": "Video tutorials", "description": "Visual learning through video content", "url": "https://www.youtube.com/"}
                    ],
                    "exercises": ["Basic exercises", "Intermediate challenges", "Advanced projects"],
                    "timeline": ["Week 1-2: Basics", "Week 3-4: Advanced concepts", "Week 5-6: Projects"],
                    "assessment": ["Knowledge tests", "Project evaluation", "Practical application"]
                },
                "progress": {
                    "completed_objectives": [],
                    "completed_resources": [],
                    "completed_exercises": [],
                    "time_spent_hours": 0,
                    "progress_percentage": 0,
                    "last_updated": timestamp.isoformat()
                }
            }
    
    def _generate_learning_path_content(self, learning_path: Dict) -> Dict:
        """Generate structured content for a learning path based on the skill and user preferences"""
        try:
            skill_name = learning_path["skill_name"]
            skill_level = learning_path["skill_level"]
            target_role = learning_path["target_role"]
            
            self._log(f"Generating learning path content for {skill_name} ({skill_level}) for {target_role}")
            
            # Create default content based on the skill
            if skill_name.lower() in ["python", "python programming"]:
                learning_path["structured_data"]["objectives"] = [
                    {"id": str(uuid.uuid4()), "title": "Understand Python fundamentals", "description": "Learn basic syntax, data types, and control structures"},
                    {"id": str(uuid.uuid4()), "title": "Master data structures", "description": "Become proficient with lists, dictionaries, sets, and tuples"},
                    {"id": str(uuid.uuid4()), "title": "Learn object-oriented programming", "description": "Understand classes, objects, inheritance, and polymorphism"},
                    {"id": str(uuid.uuid4()), "title": "Work with Python modules", "description": "Learn to use and create Python modules and packages"}
                ]
                
                learning_path["structured_data"]["resources"] = [
                    {"id": str(uuid.uuid4()), "title": "Python.org Documentation", "description": "Official Python documentation", "url": "https://docs.python.org/3/"},
                    {"id": str(uuid.uuid4()), "title": "Automate the Boring Stuff with Python", "description": "Practical Python programming book", "url": "https://automatetheboringstuff.com/"},
                    {"id": str(uuid.uuid4()), "title": "Codecademy Python Course", "description": "Interactive Python learning course", "url": "https://www.codecademy.com/learn/learn-python-3"}
                ]
                
                learning_path["structured_data"]["exercises"] = [
                    {"id": str(uuid.uuid4()), "title": "Build a CLI tool", "description": "Create a command-line interface tool for a practical task"},
                    {"id": str(uuid.uuid4()), "title": "Data analysis project", "description": "Analyze a dataset using pandas and matplotlib"},
                    {"id": str(uuid.uuid4()), "title": "Web scraping project", "description": "Extract and process data from websites using Beautiful Soup"}
                ]
                
                learning_path["structured_data"]["timeline"] = [
                    "Week 1-2: Python fundamentals and data structures",
                    "Week 3-4: Object-oriented programming and modules",
                    "Week 5-6: Practical projects and advanced topics"
                ]
                
                learning_path["structured_data"]["assessment"] = [
                    "Complete a capstone project combining multiple skills",
                    "Pass a comprehensive Python assessment test",
                    "Create a portfolio of at least 3 Python projects"
                ]
            
            elif skill_name.lower() in ["data analysis", "data analytics"]:
                learning_path["structured_data"]["objectives"] = [
                    {"id": str(uuid.uuid4()), "title": "Learn data collection and cleaning", "description": "Understand how to gather and prepare data for analysis"},
                    {"id": str(uuid.uuid4()), "title": "Master statistical analysis", "description": "Learn descriptive and inferential statistics"},
                    {"id": str(uuid.uuid4()), "title": "Develop data visualization skills", "description": "Create effective charts and graphs to communicate findings"},
                    {"id": str(uuid.uuid4()), "title": "Understand data storytelling", "description": "Learn to present insights effectively to stakeholders"}
                ]
                
                learning_path["structured_data"]["resources"] = [
                    {"id": str(uuid.uuid4()), "title": "Kaggle Learn", "description": "Free courses on data science and analysis", "url": "https://www.kaggle.com/learn"},
                    {"id": str(uuid.uuid4()), "title": "DataCamp", "description": "Interactive data science courses", "url": "https://www.datacamp.com/"},
                    {"id": str(uuid.uuid4()), "title": "Storytelling with Data", "description": "Book on effective data visualization", "url": "http://www.storytellingwithdata.com/"}
                ]
                
                learning_path["structured_data"]["exercises"] = [
                    {"id": str(uuid.uuid4()), "title": "Exploratory data analysis", "description": "Analyze a dataset to uncover patterns and insights"},
                    {"id": str(uuid.uuid4()), "title": "Dashboard creation", "description": "Build an interactive dashboard to visualize key metrics"},
                    {"id": str(uuid.uuid4()), "title": "Business report", "description": "Create a comprehensive report with actionable recommendations"}
                ]
                
                learning_path["structured_data"]["timeline"] = [
                    "Week 1-2: Data collection, cleaning, and preparation",
                    "Week 3-4: Statistical analysis and visualization",
                    "Week 5-6: Advanced analytics and presentation skills"
                ]
                
                learning_path["structured_data"]["assessment"] = [
                    "Complete an end-to-end analysis project with real-world data",
                    "Create a portfolio of data visualizations",
                    "Present findings to peers and receive feedback"
                ]
            
            elif skill_name.lower() in ["machine learning", "ml"]:
                learning_path["structured_data"]["objectives"] = [
                    {"id": str(uuid.uuid4()), "title": "Understand ML fundamentals", "description": "Learn about supervised and unsupervised learning"},
                    {"id": str(uuid.uuid4()), "title": "Master key algorithms", "description": "Implement common ML algorithms from scratch"},
                    {"id": str(uuid.uuid4()), "title": "Work with ML libraries", "description": "Learn to use scikit-learn, TensorFlow, or PyTorch"},
                    {"id": str(uuid.uuid4()), "title": "Apply ML to real problems", "description": "Solve practical problems using machine learning"}
                ]
                
                learning_path["structured_data"]["resources"] = [
                    {"id": str(uuid.uuid4()), "title": "Andrew Ng's Machine Learning Course", "description": "Comprehensive introduction to ML", "url": "https://www.coursera.org/learn/machine-learning"},
                    {"id": str(uuid.uuid4()), "title": "Hands-On Machine Learning", "description": "Practical guide to ML with Scikit-Learn and TensorFlow", "url": "https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/"},
                    {"id": str(uuid.uuid4()), "title": "Fast.ai", "description": "Practical deep learning for coders", "url": "https://www.fast.ai/"}
                ]
                
                learning_path["structured_data"]["exercises"] = [
                    {"id": str(uuid.uuid4()), "title": "Classification project", "description": "Build a model to classify data into categories"},
                    {"id": str(uuid.uuid4()), "title": "Regression analysis", "description": "Predict continuous values using regression techniques"},
                    {"id": str(uuid.uuid4()), "title": "Clustering challenge", "description": "Apply unsupervised learning to discover patterns"}
                ]
                
                learning_path["structured_data"]["timeline"] = [
                    "Week 1-2: ML fundamentals and algorithms",
                    "Week 3-4: Working with ML libraries and frameworks",
                    "Week 5-6: Applied ML projects and evaluation techniques"
                ]
                
                learning_path["structured_data"]["assessment"] = [
                    "Implement a complete ML pipeline from data preparation to evaluation",
                    "Participate in a Kaggle competition",
                    "Create a portfolio of ML projects demonstrating different techniques"
                ]
            
            elif skill_name.lower() in ["deep learning", "neural networks"]:
                learning_path["structured_data"]["objectives"] = [
                    {"id": str(uuid.uuid4()), "title": "Understand neural network basics", "description": "Learn about neurons, activation functions, and backpropagation"},
                    {"id": str(uuid.uuid4()), "title": "Master deep learning architectures", "description": "Study CNNs, RNNs, and Transformers"},
                    {"id": str(uuid.uuid4()), "title": "Implement deep learning models", "description": "Build and train models using frameworks like TensorFlow or PyTorch"},
                    {"id": str(uuid.uuid4()), "title": "Apply deep learning to complex problems", "description": "Solve challenging tasks in computer vision, NLP, or other domains"}
                ]
                
                learning_path["structured_data"]["resources"] = [
                    {"id": str(uuid.uuid4()), "title": "Deep Learning Specialization", "description": "Comprehensive deep learning course by Andrew Ng", "url": "https://www.coursera.org/specializations/deep-learning"},
                    {"id": str(uuid.uuid4()), "title": "Deep Learning with PyTorch", "description": "Hands-on introduction to PyTorch", "url": "https://pytorch.org/tutorials/"},
                    {"id": str(uuid.uuid4()), "title": "TensorFlow Documentation", "description": "Official TensorFlow tutorials and guides", "url": "https://www.tensorflow.org/learn"}
                ]
                
                learning_path["structured_data"]["exercises"] = [
                    {"id": str(uuid.uuid4()), "title": "Image classification", "description": "Build a CNN to classify images"},
                    {"id": str(uuid.uuid4()), "title": "Text generation", "description": "Create an RNN or Transformer for text generation"},
                    {"id": str(uuid.uuid4()), "title": "Transfer learning project", "description": "Apply pre-trained models to new problems"}
                ]
                
                learning_path["structured_data"]["timeline"] = [
                    "Week 1-2: Neural network fundamentals and architectures",
                    "Week 3-4: Deep learning frameworks and implementation",
                    "Week 5-8: Advanced applications and optimization techniques"
                ]
                
                learning_path["structured_data"]["assessment"] = [
                    "Build and deploy a deep learning model to solve a real-world problem",
                    "Optimize a model for performance and efficiency",
                    "Create a portfolio showcasing different deep learning techniques"
                ]
            
            elif skill_name.lower() in ["project management"]:
                learning_path["structured_data"]["objectives"] = [
                    {"id": str(uuid.uuid4()), "title": "Learn project management fundamentals", "description": "Understand project lifecycle, methodologies, and planning"},
                    {"id": str(uuid.uuid4()), "title": "Master resource management", "description": "Learn to allocate and manage project resources effectively"},
                    {"id": str(uuid.uuid4()), "title": "Develop stakeholder communication", "description": "Build skills for effective stakeholder engagement"},
                    {"id": str(uuid.uuid4()), "title": "Understand risk management", "description": "Learn to identify, assess, and mitigate project risks"}
                ]
                
                learning_path["structured_data"]["resources"] = [
                    {"id": str(uuid.uuid4()), "title": "PMI Resources", "description": "Project Management Institute guides and resources", "url": "https://www.pmi.org/"},
                    {"id": str(uuid.uuid4()), "title": "Project Management Body of Knowledge", "description": "PMBOK Guide - industry standard", "url": "https://www.pmi.org/pmbok-guide-standards"},
                    {"id": str(uuid.uuid4()), "title": "Agile Practice Guide", "description": "Guide to agile methodologies", "url": "https://www.pmi.org/pmbok-guide-standards/practice-guides/agile"}
                ]
                
                learning_path["structured_data"]["exercises"] = [
                    {"id": str(uuid.uuid4()), "title": "Project charter creation", "description": "Develop a comprehensive project charter"},
                    {"id": str(uuid.uuid4()), "title": "Risk assessment", "description": "Conduct a risk assessment for a sample project"},
                    {"id": str(uuid.uuid4()), "title": "Project plan development", "description": "Create a complete project plan with timelines and milestones"}
                ]
                
                learning_path["structured_data"]["timeline"] = [
                    "Week 1-2: Project management fundamentals and methodologies",
                    "Week 3-4: Resource allocation and stakeholder management",
                    "Week 5-6: Risk management and project execution"
                ]
                
                learning_path["structured_data"]["assessment"] = [
                    "Manage a small project from initiation to closure",
                    "Create a portfolio of project management artifacts",
                    "Obtain feedback from experienced project managers"
                ]
            
            # Default content for any other skill
            else:
                learning_path["structured_data"]["objectives"] = [
                    {"id": str(uuid.uuid4()), "title": f"Learn {skill_name} fundamentals", "description": f"Build a strong foundation in {skill_name}"},
                    {"id": str(uuid.uuid4()), "title": f"Develop practical {skill_name} skills", "description": f"Apply {skill_name} concepts to real-world situations"},
                    {"id": str(uuid.uuid4()), "title": f"Master advanced {skill_name} techniques", "description": f"Learn specialized techniques in {skill_name}"},
                    {"id": str(uuid.uuid4()), "title": f"Apply {skill_name} to {target_role} role", "description": f"Understand how {skill_name} is used in {target_role} positions"}
                ]
                
                learning_path["structured_data"]["resources"] = [
                    {"id": str(uuid.uuid4()), "title": "Online Courses", "description": f"Interactive courses teaching {skill_name} fundamentals and applications", "url": f"https://www.coursera.org/search?query={skill_name.replace(' ', '+')}"},
                    {"id": str(uuid.uuid4()), "title": "Books & Guides", "description": f"Comprehensive learning materials and reference guides", "url": f"https://www.amazon.com/s?k={skill_name.replace(' ', '+')}+books"},
                    {"id": str(uuid.uuid4()), "title": "Community Forums", "description": f"Connect with other learners and experts in the field", "url": f"https://www.reddit.com/search/?q={skill_name.replace(' ', '+')}"},
                    {"id": str(uuid.uuid4()), "title": "Video Tutorials", "description": f"Visual step-by-step learning resources", "url": f"https://www.youtube.com/results?search_query={skill_name.replace(' ', '+')}+tutorial"},
                    {"id": str(uuid.uuid4()), "title": "Certification Programs", "description": f"Professional credentials to validate your expertise", "url": ""}
                ]
                
                learning_path["structured_data"]["exercises"] = [
                    {"id": str(uuid.uuid4()), "title": "Beginner Project", "description": f"Apply fundamental {skill_name} concepts to a simple project"},
                    {"id": str(uuid.uuid4()), "title": "Practice Challenge", "description": f"Solve real-world problems using intermediate skills"},
                    {"id": str(uuid.uuid4()), "title": "Advanced Application", "description": f"Create a complex solution demonstrating mastery"}
                ]
                
                learning_path["structured_data"]["timeline"] = [
                    f"Week 1-2: {skill_name} fundamentals",
                    f"Week 3-4: Practical {skill_name} applications",
                    f"Week 5-6: Advanced {skill_name} techniques and integration with {target_role} role"
                ]
                
                learning_path["structured_data"]["assessment"] = [
                    f"Complete a portfolio of {skill_name} projects",
                    f"Demonstrate {skill_name} skills in a practical assessment",
                    f"Apply {skill_name} to solve a problem relevant to {target_role}"
                ]
            
            return learning_path
            
        except Exception as e:
            error_msg = str(e)
            self._log(f"Error generating learning path content: {error_msg}")
            
            # Create basic default content
            learning_path["structured_data"]["objectives"] = [
                {"id": str(uuid.uuid4()), "title": "Learn fundamental concepts", "description": "Build a strong foundation in the subject"},
                {"id": str(uuid.uuid4()), "title": "Develop practical skills", "description": "Apply concepts to real-world situations"},
                {"id": str(uuid.uuid4()), "title": "Master advanced techniques", "description": "Learn specialized techniques in the subject"}
            ]
            
            learning_path["structured_data"]["resources"] = [
                {"id": str(uuid.uuid4()), "title": "Online courses", "description": "Structured online learning", "url": "https://www.coursera.org/"},
                {"id": str(uuid.uuid4()), "title": "Books and guides", "description": "Comprehensive learning materials", "url": "https://www.goodreads.com/"},
                {"id": str(uuid.uuid4()), "title": "Practice resources", "description": "Interactive exercises and projects", "url": "https://www.codecademy.com/"},
                {"id": str(uuid.uuid4()), "title": "Community forums", "description": "Connect with others learning the same skills", "url": "https://stackoverflow.com/"},
                {"id": str(uuid.uuid4()), "title": "Video tutorials", "description": "Visual learning through video content", "url": "https://www.youtube.com/"}
            ]
            
            learning_path["structured_data"]["exercises"] = [
                {"id": str(uuid.uuid4()), "title": "Beginner project", "description": "Apply fundamental concepts"},
                {"id": str(uuid.uuid4()), "title": "Intermediate challenge", "description": "Solve more complex problems"},
                {"id": str(uuid.uuid4()), "title": "Advanced application", "description": "Demonstrate expertise in complex situations"}
            ]
            
            learning_path["structured_data"]["timeline"] = [
                "Week 1-2: Fundamentals",
                "Week 3-4: Practical applications",
                "Week 5-6: Advanced techniques"
            ]
            
            learning_path["structured_data"]["assessment"] = [
                "Complete a portfolio of projects",
                "Demonstrate skills in a practical assessment",
                "Apply knowledge to solve a real-world problem"
            ]
            
            return learning_path
    
    def _parse_skills_analysis(self, response: str) -> Dict:
        """Parse the skills analysis response"""
        try:
            parsed_data = {
                "skill_gaps": [],
                "priority_skills": [],
                "learning_resources": [],
                "transition_strategy": []
            }
            
            # Debug log for troubleshooting
            self._log(f"Raw analysis response (first 100 chars): {response[:100]}...")
            
            # Split into sections and process each line
            current_section = None
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Identify sections with more variations
                if any(term in line.lower() for term in ["skill gap analysis", "gap analysis", "1. skill gap", "skill gaps"]):
                    current_section = "skill_gaps"
                    self._log(f"Found skill_gaps section: {line}")
                    continue
                elif any(term in line.lower() for term in ["priority skills", "skills to develop", "2. priority", "key skills"]):
                    current_section = "priority_skills"
                    self._log(f"Found priority_skills section: {line}")
                    continue
                elif any(term in line.lower() for term in ["learning resources", "resources", "3. learning", "recommended resources"]):
                    current_section = "learning_resources"
                    self._log(f"Found learning_resources section: {line}")
                    continue
                elif any(term in line.lower() for term in ["career transition", "transition strategy", "4. career", "action plan"]):
                    current_section = "transition_strategy"
                    self._log(f"Found transition_strategy section: {line}")
                    continue
                
                # Add items to current section if line starts with a bullet point, number, or has a common pattern
                if current_section:
                    # Check for bullet points, numbers, or other common patterns
                    if (line.startswith(('-', '•', '*', '>', '→')) or 
                        any(line.startswith(f"{i}.") for i in range(1, 10)) or
                        ":" in line or  # Lines with colons often contain valuable info
                        " - " in line):  # Common separator in lists
                        
                        # Clean the line by removing bullets, numbers, etc.
                        cleaned_line = re.sub(r'^[0-9\.\-\*•→\s>]+', '', line).strip()
                        
                        # If the line still has content after cleaning
                        if cleaned_line and len(cleaned_line) > 3:  # Avoid very short entries
                            # Remove any "skill gap:" prefix for cleaner entries
                            if current_section == "skill_gaps" and ":" in cleaned_line:
                                parts = cleaned_line.split(":", 1)
                                if len(parts) > 1 and len(parts[1].strip()) > 0:
                                    cleaned_line = parts[1].strip()
                                    
                            parsed_data[current_section].append(cleaned_line)
                            self._log(f"Added to {current_section}: {cleaned_line}")
                    elif current_section == "skill_gaps" and len(line) > 10:
                        # For skill gaps, also include lines that have substantial content
                        # even if they don't start with a bullet or number
                        parsed_data[current_section].append(line)
                        self._log(f"Added non-bulleted line to skill_gaps: {line}")
            
            # If no skill gaps were found but we have priority skills, infer gaps
            if not parsed_data["skill_gaps"] and parsed_data["priority_skills"]:
                self._log("No explicit skill gaps found, inferring from priority skills")
                for skill in parsed_data["priority_skills"]:
                    parsed_data["skill_gaps"].append(f"Gap in {skill} knowledge/experience")
            
            # Add fallback content if sections are empty
            if not parsed_data["skill_gaps"]:
                parsed_data["skill_gaps"] = ["No significant skill gaps identified. Focus on deepening existing skills."]
                self._log("Added default skill gap message")
                
            if not parsed_data["priority_skills"]:
                parsed_data["priority_skills"] = ["Continue developing current skill set", "Explore advanced techniques in your field"]
                self._log("Added default priority skills")
                
            if not parsed_data["learning_resources"]:
                parsed_data["learning_resources"] = [
                    "Online courses on platforms like Coursera, Udemy, or LinkedIn Learning",
                    "Books and publications about the target role",
                    "Industry certifications relevant to the target role",
                    "Join professional communities and forums in your field",
                    "Follow industry leaders and experts on social media"
                ]
                self._log("Added default learning resources")
                
            if not parsed_data["transition_strategy"]:
                parsed_data["transition_strategy"] = [
                    "Build a portfolio showcasing your skills",
                    "Network with professionals in your target role",
                    "Gain practical experience through projects or volunteer work"
                ]
                self._log("Added default transition strategy")
            
            # Debug logging
            self._log(f"Parsed sections: {[k for k, v in parsed_data.items() if v]}")
            self._log(f"Number of items parsed: {sum(len(v) for v in parsed_data.values())}")
            
            return parsed_data
            
        except Exception as e:
            self._log(f"Error parsing skills analysis: {str(e)}")
            self._log(f"Raw response: {response}")
            
            # Return default data structure with fallback content
            return {
                "skill_gaps": ["Error analyzing skill gaps. Please try again."],
                "priority_skills": ["Focus on core skills relevant to your target role"],
                "learning_resources": ["Online courses and tutorials", "Industry documentation and guides"],
                "transition_strategy": ["Build a portfolio", "Network with professionals in your field"]
            }
    
    def _parse_learning_path(self, response: str) -> Dict:
        """Parse the learning path response with improved section detection and error handling"""
        # Debug log
        self._log(f"Parsing learning path response of length: {len(response)}")
        
        parsed_data = {
            "objectives": [],
            "resources": [],
            "timeline": [],
            "exercises": [],
            "assessment": []
        }
        
        # Track which sections were found for debugging
        found_sections = []
        
        # First attempt: Try to parse by section headers
        current_section = None
        for line in response.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers with more variations
            if any(header in line.lower() for header in ["learning objectives", "objectives:", "1. learning objectives"]):
                current_section = "objectives"
                found_sections.append("objectives")
                continue
            elif any(header in line.lower() for header in ["recommended resources", "resources:", "2. recommended resources"]):
                current_section = "resources"
                found_sections.append("resources")
                continue
            elif any(header in line.lower() for header in ["timeline", "milestones", "3. timeline", "timeline and milestones"]):
                current_section = "timeline"
                found_sections.append("timeline")
                continue
            elif any(header in line.lower() for header in ["practice exercises", "exercises:", "4. practice exercises"]):
                current_section = "exercises"
                found_sections.append("exercises")
                continue
            elif any(header in line.lower() for header in ["assessment criteria", "assessment:", "5. assessment"]):
                current_section = "assessment"
                found_sections.append("assessment")
                continue
            
            # Process line based on current section
            if current_section and line:
                # Remove numbering and bullet points
                cleaned_line = re.sub(r'^[\d\.\-\*•►\s]+', '', line).strip()
                if cleaned_line:
                    parsed_data[current_section].append(cleaned_line)
        
        # Debug log
        self._log(f"Found sections in first pass: {found_sections}")
        
        # Second attempt: If sections are missing, try to parse by numbered sections
        if len(found_sections) < 5:
            self._log("First pass incomplete, trying second parsing method")
            sections = re.split(r'\n\s*\d+\.|\n\s*[A-Za-z]+:', response)
            if len(sections) > 1:
                # First element is usually empty or introduction
                sections = sections[1:]
                
                # Map sections to our structure if we have enough
                if len(sections) >= 5:
                    section_mapping = ["objectives", "resources", "timeline", "exercises", "assessment"]
                    for i, section_content in enumerate(sections[:5]):
                        section_name = section_mapping[i]
                        lines = [line.strip() for line in section_content.split('\n') if line.strip()]
                        cleaned_lines = [re.sub(r'^[\d\.\-\*•►\s]+', '', line).strip() for line in lines]
                        parsed_data[section_name] = [line for line in cleaned_lines if line]
                        if parsed_data[section_name]:
                            found_sections.append(section_name)
        
        # Debug log
        self._log(f"Found sections after second pass: {found_sections}")
        self._log(f"Parsed data counts: objectives={len(parsed_data['objectives'])}, resources={len(parsed_data['resources'])}, timeline={len(parsed_data['timeline'])}, exercises={len(parsed_data['exercises'])}, assessment={len(parsed_data['assessment'])}")
        
        # Add default items if sections are empty
        for section in parsed_data:
            if not parsed_data[section]:
                if section == "objectives":
                    parsed_data[section] = ["Master fundamental concepts", "Build practical skills", "Complete real-world projects"]
                elif section == "resources":
                    parsed_data[section] = ["Online courses", "Practice exercises", "Documentation"]
                elif section == "timeline":
                    parsed_data[section] = ["Week 1-2: Basics", "Week 3-4: Advanced concepts", "Week 5-6: Projects"]
                elif section == "exercises":
                    parsed_data[section] = ["Basic exercises", "Intermediate challenges", "Advanced projects"]
                elif section == "assessment":
                    parsed_data[section] = ["Knowledge tests", "Project evaluation", "Practical application"]
                
                self._log(f"Added default items for empty section: {section}")
        
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
    
    def update_learning_path_progress(
        self,
        learning_path_id: str,
        completed_objectives: List[str] = None,
        completed_resources: List[str] = None,
        completed_exercises: List[str] = None,
        time_spent_minutes: float = 0,
        reflection: str = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """Update progress for a learning path"""
        try:
            # Ensure parameters are not None
            completed_objectives = completed_objectives or []
            completed_resources = completed_resources or []
            completed_exercises = completed_exercises or []
            
            # Check if the learning path exists
            if learning_path_id not in self.learning_paths:
                if user_id:
                    # Try to load learning paths first
                    self._load_learning_paths(user_id)
                    if learning_path_id not in self.learning_paths:
                        raise ValueError(f"Learning path {learning_path_id} not found")
                else:
                    raise ValueError(f"Learning path {learning_path_id} not found")
            
            # Get the learning path
            learning_path = self.learning_paths[learning_path_id]
            
            # Ensure progress exists
            if "progress" not in learning_path:
                learning_path["progress"] = {
                    "completed_objectives": [],
                    "completed_resources": [],
                    "completed_exercises": [],
                    "time_spent_hours": 0,
                    "progress_percentage": 0,
                    "last_updated": datetime.datetime.now().isoformat()
                }
            
            # Ensure the time_spent_hours field exists
            if "time_spent_hours" not in learning_path["progress"]:
                learning_path["progress"]["time_spent_hours"] = 0
                
            # For safety, ensure completed_* lists exist in progress
            if "completed_objectives" not in learning_path["progress"]:
                learning_path["progress"]["completed_objectives"] = []
            if "completed_resources" not in learning_path["progress"]:
                learning_path["progress"]["completed_resources"] = []
            if "completed_exercises" not in learning_path["progress"]:
                learning_path["progress"]["completed_exercises"] = []
            
            # Replace completed items instead of updating
            learning_path["progress"]["completed_objectives"] = completed_objectives
            learning_path["progress"]["completed_resources"] = completed_resources
            learning_path["progress"]["completed_exercises"] = completed_exercises
            
            # Update time spent
            if time_spent_minutes > 0:
                learning_path["progress"]["time_spent_hours"] += time_spent_minutes / 60
            
            # Calculate progress percentage
            total_items = (
                len(learning_path["structured_data"]["objectives"]) +
                len(learning_path["structured_data"]["resources"]) +
                len(learning_path["structured_data"]["exercises"])
            )
            
            completed_items = (
                len(learning_path["progress"]["completed_objectives"]) +
                len(learning_path["progress"]["completed_resources"]) +
                len(learning_path["progress"]["completed_exercises"])
            )
            
            if total_items > 0:
                # Convert to integer percentage for cleaner display
                learning_path["progress"]["progress_percentage"] = int((completed_items / total_items) * 100)
            else:
                learning_path["progress"]["progress_percentage"] = 0
            
            # Update last updated timestamp
            learning_path["progress"]["last_updated"] = datetime.datetime.now().isoformat()
            
            # Add reflection if provided
            if reflection:
                if "reflections" not in learning_path:
                    learning_path["reflections"] = []
                
                learning_path["reflections"].append({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "content": reflection,
                    "progress_at_reflection": learning_path["progress"]["progress_percentage"]
                })
            
            # Save the updated learning path
            if user_id:
                self._save_learning_path(user_id, learning_path)
            
            # Debug log with integer percentage
            self._log(f"Updated progress for learning path {learning_path_id} - {learning_path['progress']['progress_percentage']}%")
            
            return learning_path["progress"]
            
        except Exception as e:
            error_msg = str(e)
            self._log(f"Error updating learning path progress: {error_msg}")
            raise ValueError(f"Failed to update learning path progress: {error_msg}")
    
    def assess_progress(
        self,
        learning_path_id: str,
        user_reflection: str = "",
        user_id: Optional[str] = None
    ) -> Dict:
        """Assess progress and provide feedback for a learning path"""
        try:
            # Check if the learning path exists
            if learning_path_id not in self.learning_paths:
                if user_id:
                    # Try to load learning paths first
                    self._load_learning_paths(user_id)
                    if learning_path_id not in self.learning_paths:
                        raise ValueError(f"Learning path {learning_path_id} not found")
                else:
                    raise ValueError(f"Learning path {learning_path_id} not found")
            
            # Get the learning path
            learning_path = self.learning_paths[learning_path_id]
            
            # Ensure basic structure exists
            if "progress" not in learning_path:
                learning_path["progress"] = {
                    "completed_objectives": [],
                    "completed_resources": [],
                    "completed_exercises": [],
                    "time_spent_hours": 0,
                    "progress_percentage": 0,
                    "last_updated": datetime.datetime.now().isoformat()
                }
            
            if "structured_data" not in learning_path:
                learning_path["structured_data"] = {
                    "objectives": [],
                    "resources": [],
                    "exercises": []
                }
            
            # Calculate progress metrics
            progress = learning_path["progress"]
            structured_data = learning_path["structured_data"]
            
            # Ensure all required lists exist
            for key in ["completed_objectives", "completed_resources", "completed_exercises"]:
                if key not in progress:
                    progress[key] = []
            
            for key in ["objectives", "resources", "exercises"]:
                if key not in structured_data:
                    structured_data[key] = []
            
            # Calculate completion percentages for each section
            objectives_completion = len(progress["completed_objectives"]) / len(structured_data["objectives"]) if structured_data["objectives"] else 0
            resources_completion = len(progress["completed_resources"]) / len(structured_data["resources"]) if structured_data["resources"] else 0
            exercises_completion = len(progress["completed_exercises"]) / len(structured_data["exercises"]) if structured_data["exercises"] else 0
            
            # Convert percentages to integer for cleaner display
            objectives_completion = round(objectives_completion * 100, 1)
            resources_completion = round(resources_completion * 100, 1)
            exercises_completion = round(exercises_completion * 100, 1)
            
            # Ensure progress_percentage exists
            if "progress_percentage" not in progress:
                total_items = (
                    len(structured_data["objectives"]) +
                    len(structured_data["resources"]) +
                    len(structured_data["exercises"])
                )
                
                completed_items = (
                    len(progress["completed_objectives"]) +
                    len(progress["completed_resources"]) +
                    len(progress["completed_exercises"])
                )
                
                progress["progress_percentage"] = int((completed_items / total_items) * 100) if total_items > 0 else 0
            
            # Generate feedback based on progress
            feedback = {
                "overall_progress": progress["progress_percentage"],
                "objectives_completion": objectives_completion,
                "resources_completion": resources_completion,
                "exercises_completion": exercises_completion,
                "time_spent_hours": progress.get("time_spent_hours", 0),
                "feedback": [],
                "next_steps": [],
                "assessment_date": datetime.datetime.now().isoformat()
            }
            
            # Generate feedback messages
            if progress["progress_percentage"] < 25:
                feedback["feedback"].append("You're just getting started. Keep up the momentum!")
                feedback["next_steps"].append("Focus on completing the foundational objectives first.")
            elif progress["progress_percentage"] < 50:
                feedback["feedback"].append("You're making steady progress. Keep going!")
                feedback["next_steps"].append("Consider spending more time on practical exercises.")
            elif progress["progress_percentage"] < 75:
                feedback["feedback"].append("You're well on your way to mastering this skill!")
                feedback["next_steps"].append("Start applying your knowledge to real-world projects.")
            else:
                feedback["feedback"].append("Excellent progress! You're almost there.")
                feedback["next_steps"].append("Focus on the remaining advanced topics to complete your learning path.")
            
            # Add section-specific feedback
            if objectives_completion < resources_completion and objectives_completion < exercises_completion:
                feedback["feedback"].append("You've been exploring resources and exercises, but make sure to complete the core learning objectives.")
            elif resources_completion < objectives_completion and resources_completion < exercises_completion:
                feedback["feedback"].append("You're making good progress on objectives, but consider exploring more of the recommended resources.")
            elif exercises_completion < objectives_completion and exercises_completion < resources_completion:
                feedback["feedback"].append("You've been studying the material, but need more practice with the exercises to solidify your skills.")
            
            # Add time-based feedback
            if progress["time_spent_hours"] < 5:
                feedback["feedback"].append("Consider dedicating more time to this skill to accelerate your progress.")
            elif progress["time_spent_hours"] > 20 and progress["progress_percentage"] < 50:
                feedback["feedback"].append("You've spent significant time on this skill. Consider reviewing your learning approach for more efficiency.")
            
            # Add user reflection to the learning path if provided
            if user_reflection:
                timestamp = datetime.datetime.now().isoformat()
                if "reflections" not in learning_path:
                    learning_path["reflections"] = []
                
                learning_path["reflections"].append({
                    "timestamp": timestamp,
                    "content": user_reflection,
                    "progress_at_reflection": progress["progress_percentage"]
                })
                
                # Save the updated learning path
                if user_id:
                    self._save_learning_path(user_id, learning_path)
            
            # Debug log with integer percentage
            self._log(f"Assessed progress for learning path {learning_path_id} - Overall: {int(progress['progress_percentage'])}%")
            
            return feedback
            
        except Exception as e:
            error_msg = str(e)
            self._log(f"Error assessing progress: {error_msg}")
            raise ValueError(f"Failed to assess progress: {error_msg}")
    
    def get_user_learning_paths(self, user_id: str) -> List[Dict]:
        """Get all learning paths for a user"""
        try:
            # First, try to load learning paths from disk if not already loaded
            if not self.learning_paths:
                self._load_learning_paths(user_id)
            
            # Return the learning paths as a list
            paths = list(self.learning_paths.values())
            
            # Debug log
            self._log(f"Retrieved {len(paths)} learning paths for user {user_id}")
            
            return paths
        except Exception as e:
            self._log(f"Error retrieving learning paths: {str(e)}")
            return []
    
    def _save_user_data(self, user_id: str, data_type: str, data: Dict) -> None:
        """Save user data to disk"""
        try:
            # Create the user directory path
            user_dir = os.path.join(self.user_data_path, user_id)
            
            # Create directory if it doesn't exist
            os.makedirs(user_dir, exist_ok=True)
            
            # Create the file path
            file_path = os.path.join(user_dir, f"{data_type}.json")
            
            # Save the data to disk
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Debug log
            self._log(f"Saved {data_type} data for user {user_id}")
            
        except Exception as e:
            self._log(f"Error saving {data_type} data: {str(e)}")
            raise
    
    def _save_learning_path(self, user_id: str, learning_path: Dict) -> None:
        """Save a learning path to disk"""
        try:
            # Create the user directory path
            user_dir = os.path.join(self.user_data_path, user_id)
            learning_paths_dir = os.path.join(user_dir, "learning_paths")
            
            # Create directories if they don't exist
            os.makedirs(learning_paths_dir, exist_ok=True)
            
            # Ensure the learning path has an ID
            if "id" not in learning_path:
                timestamp = datetime.datetime.now()
                learning_path["id"] = f"{learning_path.get('skill', 'unknown')}_{timestamp.strftime('%Y%m%d%H%M%S')}"
            
            # Create the file path
            file_path = os.path.join(learning_paths_dir, f"{learning_path['id']}.json")
            
            # Save the learning path to disk
            with open(file_path, 'w') as f:
                json.dump(learning_path, f, indent=2)
            
            # Debug log
            self._log(f"Saved learning path {learning_path['id']} for user {user_id}")
            
        except Exception as e:
            self._log(f"Error saving learning path: {str(e)}")
            raise
    
    def _load_learning_paths(self, user_id: str) -> None:
        """Load all learning paths for a user"""
        try:
            # Create the user directory path
            user_dir = os.path.join(self.user_data_path, user_id)
            learning_paths_dir = os.path.join(user_dir, "learning_paths")
            
            # Check if the directory exists
            if not os.path.exists(learning_paths_dir):
                os.makedirs(learning_paths_dir, exist_ok=True)
                self._log(f"Created learning paths directory for user {user_id}")
                return
            
            # Load all learning path files
            path_files = [f for f in os.listdir(learning_paths_dir) if f.endswith('.json')]
            
            # Debug log
            self._log(f"Found {len(path_files)} learning path files for user {user_id}")
            
            # Load each file
            for file_name in path_files:
                try:
                    file_path = os.path.join(learning_paths_dir, file_name)
                    with open(file_path, 'r') as f:
                        learning_path = json.load(f)
                        
                    # Add to the learning paths dictionary
                    if "id" in learning_path:
                        self.learning_paths[learning_path["id"]] = learning_path
                except Exception as e:
                    self._log(f"Error loading learning path file {file_name}: {str(e)}")
            
            self._log(f"Successfully loaded {len(self.learning_paths)} learning paths for user {user_id}")
            
        except Exception as e:
            self._log(f"Error loading learning paths: {str(e)}")
            # Initialize empty if loading fails
            self.learning_paths = {}
    
    def _format_list_with_progress(self, items: List[str], completed_items: List[str]) -> str:
        """Format a list of items with completion status"""
        # Implementation for formatting progress lists 
    
    def _log(self, message):
        """Log a message with a timestamp"""
        if self.verbose:
            # Remove any raw numeric progress percentage
            if "Updated progress for learning path" in message and "%" in message:
                parts = message.split(" to ")
                if len(parts) > 1:
                    # Remove the raw number, just keep the formatted percentage
                    message = parts[0] + " to " + parts[1].split("%")[0] + "%"
            
            print(f"[Skills Development Advisor] {message}") 