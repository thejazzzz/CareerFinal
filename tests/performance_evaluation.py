import os
import sys
import time
import statistics
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.resume_analyzer import ResumeAnalyzerAgent
from agents.career_navigator import CareerNavigatorAgent
from agents.skills_advisor import SkillsAdvisorAgent
from agents.career_chatbot import CareerChatbotAgent
from agents.job_searcher import JobSearchAgent
from agents.interview_coach import InterviewCoachAgent
from agents.cover_letter_generator import CoverLetterGeneratorAgent
from config.config import Config

class PerformanceEvaluation:
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.results = {
            "accuracy": {},
            "response_time": {},
            "user_satisfaction": {},
            "system_efficiency": {},
            "explainability": {},
            "adaptability": {},
            "reliability": {}
        }
        
        # Initialize agents
        try:
            self.resume_analyzer = ResumeAnalyzerAgent(verbose=verbose)
            self.career_navigator = CareerNavigatorAgent(verbose=verbose)
            self.skills_advisor = SkillsAdvisorAgent(verbose=verbose)
            self.career_chatbot = CareerChatbotAgent(verbose=verbose)
            self.job_searcher = JobSearchAgent(verbose=verbose)
            self.interview_coach = InterviewCoachAgent(verbose=verbose)
            self.cover_letter_generator = CoverLetterGeneratorAgent(verbose=verbose)
            self.log("All agents initialized successfully")
        except Exception as e:
            self.log(f"Error initializing agents: {str(e)}")
    
    def log(self, message):
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def evaluate_nlp_accuracy(self, sample_size=5):
        """Evaluate NLP accuracy for extracting key details from user inputs"""
        self.log("Evaluating NLP accuracy...")
        
        # Test data: resume analysis
        test_resume = "test_resume.pdf"
        
        try:
            start_time = time.time()
            result = self.resume_analyzer.process_resume(test_resume)
            processing_time = time.time() - start_time
            
            # Evaluate extraction quality
            accuracy_score = 0
            if result and "structured_data" in result:
                data = result["structured_data"]
                
                # Check presence of key sections
                key_sections = ["professional_summary", "skills", "experience", "education"]
                section_score = sum(1 for section in key_sections if section in data) / len(key_sections)
                
                # Check item count in sections
                content_score = min(1.0, sum(len(data.get(section, [])) for section in key_sections) / 20)
                
                # Check for any detected skills
                skills_score = min(1.0, len(data.get("skills", [])) / 5)
                
                # Overall accuracy
                accuracy_score = (section_score * 0.5) + (content_score * 0.3) + (skills_score * 0.2)
                
                self.log(f"Resume analysis accuracy: {accuracy_score:.2f}")
                self.log(f"Processing time: {processing_time:.2f}s")
                
                # Query consistency check
                career_query_responses = []
                for i in range(sample_size):
                    career_path = self.career_navigator.create_career_path(
                        current_role="Software Developer",
                        experience="3 years",
                        skills=["Python", "JavaScript", "React"],
                        interests=["AI", "Cloud Computing"],
                        goals=["Tech Lead", "Learn Machine Learning"]
                    )
                    if career_path and "structured_data" in career_path:
                        career_query_responses.append(len(career_path["structured_data"]["path_options"]))
                
                consistency_score = 1.0
                if career_query_responses:
                    variance = statistics.variance(career_query_responses) if len(career_query_responses) > 1 else 0
                    consistency_score = max(0, 1.0 - (variance / max(statistics.mean(career_query_responses), 1)))
                
                self.log(f"Query consistency score: {consistency_score:.2f}")
                
                # Overall NLP accuracy
                self.results["accuracy"]["nlp"] = (accuracy_score * 0.7) + (consistency_score * 0.3)
                self.log(f"Overall NLP accuracy: {self.results['accuracy']['nlp']:.2f}")
            else:
                self.log("Failed to process resume")
                self.results["accuracy"]["nlp"] = 0.0
                
        except Exception as e:
            self.log(f"Error evaluating NLP accuracy: {str(e)}")
            self.results["accuracy"]["nlp"] = 0.0
    
    def evaluate_recommendation_precision(self, sample_size=3):
        """Evaluate precision of career recommendations"""
        self.log("Evaluating recommendation precision...")
        
        try:
            # Different career profiles to test
            test_profiles = [
                {
                    "current_role": "Junior Software Developer",
                    "experience": "2 years of experience in web development",
                    "skills": ["Python", "JavaScript", "React", "SQL"],
                    "interests": ["Machine Learning", "Cloud Computing"],
                    "goals": ["Become a Senior Developer", "Work on AI projects"]
                },
                {
                    "current_role": "Marketing Specialist",
                    "experience": "3 years in digital marketing",
                    "skills": ["Social Media", "Content Creation", "SEO", "Analytics"],
                    "interests": ["Marketing Automation", "Brand Strategy"],
                    "goals": ["Marketing Manager", "Develop data-driven marketing campaigns"]
                },
                {
                    "current_role": "Data Analyst",
                    "experience": "1 year working with data visualization",
                    "skills": ["SQL", "Excel", "Tableau", "Basic Python"],
                    "interests": ["Machine Learning", "Big Data"],
                    "goals": ["Data Scientist", "Work with predictive models"]
                }
            ]
            
            alignment_scores = []
            relevance_scores = []
            
            for profile in test_profiles:
                try:
                    career_path = self.career_navigator.create_career_path(**profile)
                    
                    if career_path and "structured_data" in career_path:
                        data = career_path["structured_data"]
                        
                        # Check alignment of recommendations with goals
                        goal_alignment = 0
                        if data["path_options"] and profile["goals"]:
                            matches = sum(1 for goal in profile["goals"] 
                                         for path in data["path_options"] 
                                         if any(word.lower() in path.lower() for word in goal.lower().split()))
                            goal_alignment = min(1.0, matches / len(profile["goals"]))
                        
                        # Check relevance of skills recommendations
                        skill_relevance = 0
                        if "required_skills" in data and profile["current_role"]:
                            technical_skills = data["required_skills"].get("technical", [])
                            relevance_count = sum(1 for skill in technical_skills if any(
                                existing_skill.lower() in skill.lower() for existing_skill in profile["skills"]
                            ))
                            skill_relevance = min(1.0, relevance_count / max(len(technical_skills), 1))
                        
                        alignment_scores.append(goal_alignment)
                        relevance_scores.append(skill_relevance)
                        
                except Exception as e:
                    self.log(f"Error processing profile {profile['current_role']}: {str(e)}")
            
            # Calculate overall precision
            if alignment_scores and relevance_scores:
                avg_alignment = sum(alignment_scores) / len(alignment_scores)
                avg_relevance = sum(relevance_scores) / len(relevance_scores)
                
                # Overall recommendation precision
                self.results["accuracy"]["recommendation"] = (avg_alignment * 0.6) + (avg_relevance * 0.4)
                self.log(f"Goal alignment score: {avg_alignment:.2f}")
                self.log(f"Skill relevance score: {avg_relevance:.2f}")
                self.log(f"Overall recommendation precision: {self.results['accuracy']['recommendation']:.2f}")
            else:
                self.log("Failed to calculate recommendation precision")
                self.results["accuracy"]["recommendation"] = 0.0
                
        except Exception as e:
            self.log(f"Error evaluating recommendation precision: {str(e)}")
            self.results["accuracy"]["recommendation"] = 0.0
    
    def evaluate_response_time(self, num_iterations=3):
        """Evaluate system response time for various operations"""
        self.log("Evaluating response time...")
        
        response_times = {
            "resume_analysis": [],
            "career_path": [],
            "skills_assessment": [],
            "chatbot_response": []
        }
        
        try:
            # Resume analysis response time
            test_resume = "test_resume.pdf"
            for _ in range(num_iterations):
                start_time = time.time()
                self.resume_analyzer.process_resume(test_resume)
                response_times["resume_analysis"].append(time.time() - start_time)
            
            # Career path response time
            for _ in range(num_iterations):
                start_time = time.time()
                self.career_navigator.create_career_path(
                    current_role="Software Developer",
                    experience="3 years",
                    skills=["Python", "JavaScript"],
                    interests=["AI", "Cloud"],
                    goals=["Senior Developer"]
                )
                response_times["career_path"].append(time.time() - start_time)
            
            # Skills assessment response time
            for _ in range(num_iterations):
                start_time = time.time()
                self.skills_advisor.assess_skills(
                    current_skills=["Python", "JavaScript"],
                    target_role="Senior Developer"
                )
                response_times["skills_assessment"].append(time.time() - start_time)
            
            # Chatbot response time
            for _ in range(num_iterations):
                start_time = time.time()
                self.career_chatbot.get_response(
                    user_input="What skills should I learn to become a data scientist?",
                    chat_history=[]
                )
                response_times["chatbot_response"].append(time.time() - start_time)
            
            # Calculate average response times
            avg_response_times = {
                operation: sum(times) / len(times) if times else 0
                for operation, times in response_times.items()
            }
            
            # Store results
            self.results["response_time"] = avg_response_times
            
            # Calculate overall system efficiency score
            benchmark_times = {
                "resume_analysis": 5.0,  # 5 seconds benchmark
                "career_path": 3.0,      # 3 seconds benchmark
                "skills_assessment": 2.0, # 2 seconds benchmark
                "chatbot_response": 1.5   # 1.5 seconds benchmark
            }
            
            efficiency_scores = {}
            for operation, avg_time in avg_response_times.items():
                benchmark = benchmark_times.get(operation, 3.0)
                # Higher score for faster response (max 1.0)
                efficiency_scores[operation] = min(1.0, benchmark / max(avg_time, 0.1))
            
            # Overall efficiency score
            self.results["system_efficiency"]["response_time_score"] = sum(efficiency_scores.values()) / len(efficiency_scores) if efficiency_scores else 0.0
            
            self.log(f"Average response times:")
            for operation, avg_time in avg_response_times.items():
                self.log(f"  - {operation}: {avg_time:.2f}s (efficiency score: {efficiency_scores.get(operation, 0):.2f})")
            self.log(f"Overall response time efficiency score: {self.results['system_efficiency']['response_time_score']:.2f}")
            
        except Exception as e:
            self.log(f"Error evaluating response time: {str(e)}")
            self.results["system_efficiency"]["response_time_score"] = 0.0
    
    def evaluate_explainability(self):
        """Evaluate the system's ability to explain its recommendations"""
        self.log("Evaluating explainability...")
        
        try:
            # Generate career path for explainability analysis
            career_path = self.career_navigator.create_career_path(
                current_role="Business Analyst",
                experience="4 years in financial services",
                skills=["SQL", "Data Analysis", "Requirements Gathering", "Excel"],
                interests=["Data Science", "Product Management"],
                goals=["Product Owner", "Work with cross-functional teams"]
            )
            
            if career_path and "structured_data" in career_path:
                data = career_path["structured_data"]
                
                # Check for presence of explanation sections
                explanation_metrics = {
                    "path_options_provided": len(data.get("path_options", [])) > 0,
                    "timeline_provided": len(data.get("timeline", [])) > 0,
                    "challenges_provided": len(data.get("challenges", [])) > 0,
                    "solutions_provided": len(data.get("solutions", [])) > 0,
                    "trends_provided": len(data.get("trends", [])) > 0
                }
                
                # Calculate explanation completeness
                explanation_completeness = sum(1 for metric_value in explanation_metrics.values() if metric_value) / len(explanation_metrics)
                
                # Check explanation depth (average items per section)
                section_item_counts = [
                    len(data.get("path_options", [])),
                    len(data.get("timeline", [])),
                    len(data.get("challenges", [])),
                    len(data.get("solutions", [])),
                    len(data.get("trends", []))
                ]
                # Normalize depth score (max 3 items per section as benchmark)
                explanation_depth = min(1.0, sum(min(count, 3) for count in section_item_counts) / (3 * len(section_item_counts)))
                
                # Check for specificity in explanations
                detailed_count = 0
                total_items = 0
                for section in ["path_options", "timeline", "challenges", "solutions", "trends"]:
                    items = data.get(section, [])
                    total_items += len(items)
                    # Count items with specific details (more than 10 words)
                    detailed_count += sum(1 for item in items if len(item.split()) > 10)
                
                explanation_specificity = detailed_count / max(total_items, 1)
                
                # Overall explainability score
                self.results["explainability"]["score"] = (explanation_completeness * 0.4) + (explanation_depth * 0.3) + (explanation_specificity * 0.3)
                
                self.log(f"Explanation completeness: {explanation_completeness:.2f}")
                self.log(f"Explanation depth: {explanation_depth:.2f}")
                self.log(f"Explanation specificity: {explanation_specificity:.2f}")
                self.log(f"Overall explainability score: {self.results['explainability']['score']:.2f}")
            else:
                self.log("Failed to generate career path for explainability evaluation")
                self.results["explainability"]["score"] = 0.0
                
        except Exception as e:
            self.log(f"Error evaluating explainability: {str(e)}")
            self.results["explainability"]["score"] = 0.0
    
    def evaluate_adaptability(self):
        """Evaluate the system's ability to adapt to different user inputs"""
        self.log("Evaluating adaptability...")
        
        try:
            # Test adaptability with variations of the same query
            query_variations = [
                "How do I become a data scientist?",
                "What skills do I need for data science?",
                "Career path to data scientist role",
                "Help me transition to data science from software engineering",
                "Data science career advice"
            ]
            
            response_lengths = []
            unique_content_scores = []
            
            previous_response = None
            for query in query_variations:
                response = self.career_chatbot.get_response(
                    user_input=query,
                    chat_history=[]
                )
                
                if response and "content" in response:
                    content = response["content"]
                    response_lengths.append(len(content))
                    
                    # Compare with previous response to check content uniqueness
                    if previous_response:
                        # Count of unique sentences relative to previous response
                        current_sentences = [s.strip() for s in content.split('.') if s.strip()]
                        prev_sentences = [s.strip() for s in previous_response.split('.') if s.strip()]
                        
                        unique_sentences = sum(1 for s in current_sentences if s not in prev_sentences)
                        uniqueness_score = unique_sentences / max(len(current_sentences), 1)
                        unique_content_scores.append(uniqueness_score)
                    
                    previous_response = content
            
            # Consistency in response length
            if response_lengths:
                avg_length = sum(response_lengths) / len(response_lengths)
                length_variance = statistics.variance(response_lengths) if len(response_lengths) > 1 else 0
                length_consistency = max(0, 1.0 - (length_variance / (avg_length ** 2)))
            else:
                length_consistency = 0.0
            
            # Content uniqueness for similar queries
            uniqueness_score = sum(unique_content_scores) / len(unique_content_scores) if unique_content_scores else 0.0
            
            # Overall adaptability score
            self.results["adaptability"]["score"] = (length_consistency * 0.4) + (uniqueness_score * 0.6)
            
            self.log(f"Response length consistency: {length_consistency:.2f}")
            self.log(f"Content uniqueness for similar queries: {uniqueness_score:.2f}")
            self.log(f"Overall adaptability score: {self.results['adaptability']['score']:.2f}")
            
        except Exception as e:
            self.log(f"Error evaluating adaptability: {str(e)}")
            self.results["adaptability"]["score"] = 0.0
    
    def evaluate_reliability(self, num_iterations=5):
        """Evaluate system reliability by testing operation success rates"""
        self.log("Evaluating reliability...")
        
        operation_results = {
            "resume_analysis": {"success": 0, "total": 0},
            "career_path": {"success": 0, "total": 0},
            "skills_assessment": {"success": 0, "total": 0},
            "chatbot_response": {"success": 0, "total": 0}
        }
        
        try:
            # Test resume analysis reliability
            test_resume = "test_resume.pdf"
            for _ in range(num_iterations):
                operation_results["resume_analysis"]["total"] += 1
                try:
                    result = self.resume_analyzer.process_resume(test_resume)
                    if result and "structured_data" in result:
                        operation_results["resume_analysis"]["success"] += 1
                except:
                    pass
            
            # Test career path reliability
            for _ in range(num_iterations):
                operation_results["career_path"]["total"] += 1
                try:
                    result = self.career_navigator.create_career_path(
                        current_role="Software Developer",
                        experience="2 years",
                        skills=["Python", "JavaScript"],
                        interests=["AI", "Cloud"],
                        goals=["Senior Developer"]
                    )
                    if result and "structured_data" in result:
                        operation_results["career_path"]["success"] += 1
                except:
                    pass
            
            # Test skills assessment reliability
            for _ in range(num_iterations):
                operation_results["skills_assessment"]["total"] += 1
                try:
                    result = self.skills_advisor.assess_skills(
                        current_skills=["Python", "JavaScript"],
                        target_role="Data Scientist"
                    )
                    if result and "structured_data" in result:
                        operation_results["skills_assessment"]["success"] += 1
                except:
                    pass
            
            # Test chatbot reliability
            for _ in range(num_iterations):
                operation_results["chatbot_response"]["total"] += 1
                try:
                    result = self.career_chatbot.get_response(
                        user_input="Career advice for data science",
                        chat_history=[]
                    )
                    if result and "content" in result:
                        operation_results["chatbot_response"]["success"] += 1
                except:
                    pass
            
            # Calculate success rates
            success_rates = {}
            for operation, results in operation_results.items():
                if results["total"] > 0:
                    success_rates[operation] = results["success"] / results["total"]
                else:
                    success_rates[operation] = 0.0
            
            # Overall reliability score
            self.results["reliability"]["success_rates"] = success_rates
            self.results["reliability"]["score"] = sum(success_rates.values()) / len(success_rates) if success_rates else 0.0
            
            self.log("Operation success rates:")
            for operation, rate in success_rates.items():
                self.log(f"  - {operation}: {rate:.2f}")
            self.log(f"Overall reliability score: {self.results['reliability']['score']:.2f}")
            
        except Exception as e:
            self.log(f"Error evaluating reliability: {str(e)}")
            self.results["reliability"]["score"] = 0.0
    
    def simulate_user_satisfaction(self, num_personas=3):
        """Simulate user satisfaction based on system performance"""
        self.log("Simulating user satisfaction...")
        
        # Define user personas with different priorities
        personas = [
            {
                "name": "Technical Professional",
                "priorities": {
                    "accuracy": 0.4,
                    "response_time": 0.2,
                    "explainability": 0.2,
                    "reliability": 0.2
                }
            },
            {
                "name": "Career Changer",
                "priorities": {
                    "accuracy": 0.3,
                    "response_time": 0.1,
                    "explainability": 0.4,
                    "reliability": 0.2
                }
            },
            {
                "name": "Student/Early Career",
                "priorities": {
                    "accuracy": 0.2,
                    "response_time": 0.3,
                    "explainability": 0.3,
                    "reliability": 0.2
                }
            }
        ]
        
        satisfaction_scores = {}
        
        for persona in personas:
            # Calculate weighted satisfaction score based on persona priorities
            score = (
                self.results["accuracy"].get("recommendation", 0) * persona["priorities"]["accuracy"] +
                self.results["system_efficiency"].get("response_time_score", 0) * persona["priorities"]["response_time"] +
                self.results["explainability"].get("score", 0) * persona["priorities"]["explainability"] +
                self.results["reliability"].get("score", 0) * persona["priorities"]["reliability"]
            )
            
            # Convert to scale of 1-5 with some randomization to simulate real user variability
            user_score = min(5, max(1, score * 5 * (0.9 + 0.2 * np.random.random())))
            
            satisfaction_scores[persona["name"]] = user_score
            
            self.log(f"Simulated satisfaction for {persona['name']}: {user_score:.1f}/5.0")
        
        # Calculate average satisfaction and NPS
        avg_satisfaction = sum(satisfaction_scores.values()) / len(satisfaction_scores)
        
        # Net Promoter Score simulation
        # Promoters: score > 4
        # Passives: 3 <= score <= 4
        # Detractors: score < 3
        promoters = sum(1 for score in satisfaction_scores.values() if score > 4)
        detractors = sum(1 for score in satisfaction_scores.values() if score < 3)
        nps = (promoters / len(satisfaction_scores) - detractors / len(satisfaction_scores)) * 100
        
        self.results["user_satisfaction"] = {
            "average_score": avg_satisfaction,
            "nps": nps,
            "persona_scores": satisfaction_scores
        }
        
        self.log(f"Average user satisfaction: {avg_satisfaction:.1f}/5.0")
        self.log(f"Simulated Net Promoter Score: {nps:.1f}")
    
    def generate_report(self):
        """Generate a comprehensive performance report"""
        self.log("Generating performance report...")
        
        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "overall_scores": {
                "accuracy": (self.results["accuracy"].get("nlp", 0) + self.results["accuracy"].get("recommendation", 0)) / 2,
                "efficiency": self.results["system_efficiency"].get("response_time_score", 0),
                "user_satisfaction": self.results["user_satisfaction"].get("average_score", 0) / 5.0,  # Normalize to 0-1
                "explainability": self.results["explainability"].get("score", 0),
                "adaptability": self.results["adaptability"].get("score", 0),
                "reliability": self.results["reliability"].get("score", 0)
            },
            "detailed_results": self.results
        }
        
        # Calculate overall system score
        weights = {
            "accuracy": 0.25,
            "efficiency": 0.15,
            "user_satisfaction": 0.25,
            "explainability": 0.15,
            "adaptability": 0.1,
            "reliability": 0.1
        }
        
        overall_score = sum(score * weights[metric] for metric, score in report["overall_scores"].items())
        report["overall_score"] = overall_score
        
        self.log("\n=== Performance Evaluation Results ===\n")
        self.log(f"Overall System Score: {overall_score:.2f}")
        
        for metric, score in report["overall_scores"].items():
            self.log(f"{metric.capitalize()} Score: {score:.2f}")
        
        self.log("\nDetailed Scores:")
        self.log(f"NLP Accuracy: {self.results['accuracy'].get('nlp', 0):.2f}")
        self.log(f"Recommendation Precision: {self.results['accuracy'].get('recommendation', 0):.2f}")
        self.log(f"Response Time Efficiency: {self.results['system_efficiency'].get('response_time_score', 0):.2f}")
        self.log(f"User Satisfaction: {self.results['user_satisfaction'].get('average_score', 0):.1f}/5.0")
        self.log(f"Net Promoter Score: {self.results['user_satisfaction'].get('nps', 0):.1f}")
        self.log(f"Explainability: {self.results['explainability'].get('score', 0):.2f}")
        self.log(f"Adaptability: {self.results['adaptability'].get('score', 0):.2f}")
        self.log(f"Reliability: {self.results['reliability'].get('score', 0):.2f}")
        
        return report
    
    def visualize_results(self, report):
        """Visualize performance evaluation results"""
        try:
            # Spider chart for overall scores
            categories = list(report["overall_scores"].keys())
            values = [report["overall_scores"][category] for category in categories]
            
            # Ensure the list wraps around for a complete polygon
            values += values[:1]
            categories += categories[:1]
            
            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]
            
            fig, ax = plt.subplots(figsize=(10, 6), subplot_kw=dict(polar=True))
            ax.plot(angles, values, linewidth=2)
            ax.fill(angles, values, alpha=0.25)
            ax.set_thetagrids(np.degrees(angles[:-1]), categories[:-1])
            ax.set_ylim(0, 1)
            ax.set_title("Career Assistant System Performance", size=15)
            ax.grid(True)
            
            plt.tight_layout()
            plt.savefig("performance_metrics.png")
            self.log("Performance visualization saved as performance_metrics.png")
        except Exception as e:
            self.log(f"Error creating visualization: {str(e)}")
    
    def run_evaluation(self):
        """Run all performance evaluations"""
        self.log("Starting comprehensive performance evaluation...")
        
        # Run all evaluations
        self.evaluate_nlp_accuracy()
        self.evaluate_recommendation_precision()
        self.evaluate_response_time()
        self.evaluate_explainability()
        self.evaluate_adaptability()
        self.evaluate_reliability()
        self.simulate_user_satisfaction()
        
        # Generate report
        report = self.generate_report()
        
        # Visualize results
        try:
            self.visualize_results(report)
        except:
            self.log("Could not visualize results (matplotlib may not be available)")
        
        return report

def main():
    # Validate configuration
    Config.validate_config()
    
    # Run performance evaluation
    evaluator = PerformanceEvaluation(verbose=True)
    evaluator.run_evaluation()

if __name__ == "__main__":
    main() 