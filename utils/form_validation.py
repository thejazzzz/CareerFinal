from typing import Dict, List, Tuple, Optional

class FormValidation:
    @staticmethod
    def validate_profile_form(
        current_role: str,
        experience: str,
        skills: str,
        interests: str,
        career_goals: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate profile form inputs
        Returns: (is_valid, error_messages)
        """
        errors = []
        
        # Current role validation
        if not current_role:
            errors.append("Current role is required")
        elif len(current_role) < 2:
            errors.append("Current role must be at least 2 characters")
        
        # Experience validation
        if not experience:
            errors.append("Years of experience is required")
        else:
            try:
                exp_value = float(experience.split()[0])
                if exp_value < 0:
                    errors.append("Experience cannot be negative")
            except ValueError:
                errors.append("Experience must be a number followed by optional units (e.g., '5 years')")
        
        # Skills validation
        if not skills:
            errors.append("At least one skill is required")
        else:
            skill_list = [s.strip() for s in skills.split(",") if s.strip()]
            if len(skill_list) < 1:
                errors.append("Please enter at least one skill")
            elif len(skill_list) > 20:
                errors.append("Maximum 20 skills allowed")
        
        # Interests validation
        if interests:
            interest_list = [i.strip() for i in interests.split(",") if i.strip()]
            if len(interest_list) > 10:
                errors.append("Maximum 10 interests allowed")
        
        # Career goals validation
        if not career_goals:
            errors.append("Career goals are required")
        elif len(career_goals) < 10:
            errors.append("Please provide more detailed career goals")
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def validate_skill_level(skill: str, level: str) -> bool:
        """Validate skill level input"""
        valid_levels = ["beginner", "intermediate", "advanced", "expert"]
        return level.lower() in valid_levels
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: Optional[str] = None) -> bool:
        """Validate date range input"""
        try:
            from datetime import datetime
            start = datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                end = datetime.strptime(end_date, "%Y-%m-%d")
                return start <= end
            return True
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input"""
        # Remove potentially harmful characters
        import re
        return re.sub(r'[<>{}]', '', text.strip())
    
    @staticmethod
    def format_skills(skills_str: str) -> List[str]:
        """Format skills input into a clean list"""
        return [
            s.strip().capitalize()
            for s in skills_str.split(",")
            if s.strip()
        ] 