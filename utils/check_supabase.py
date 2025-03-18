import os
import sys
import json
from dotenv import load_dotenv
from supabase import create_client, Client

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def check_supabase_connection():
    """Check if we can connect to Supabase"""
    print("Checking Supabase connection...")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: Supabase credentials not found in .env file")
        print("Please ensure SUPABASE_URL and SUPABASE_KEY are set in your .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Successfully connected to Supabase at {SUPABASE_URL}")
        return supabase
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {str(e)}")
        return False

def check_tables(supabase):
    """Check if required tables exist in Supabase"""
    print("\nChecking Supabase tables...")
    
    required_tables = ['users', 'learning_paths', 'skill_analyses']
    
    try:
        # This is a simple query to check if tables exist
        for table in required_tables:
            try:
                # Try to select a single row from each table
                response = supabase.table(table).select('*').limit(1).execute()
                print(f"✅ Table '{table}' exists and is accessible")
            except Exception as e:
                print(f"❌ Error accessing table '{table}': {str(e)}")
                print(f"You may need to create the '{table}' table in your Supabase project")
    except Exception as e:
        print(f"❌ Error checking tables: {str(e)}")

def test_save_and_load(supabase):
    """Test saving and loading data from Supabase"""
    print("\nTesting data saving and loading...")

    # Test data for users table
    test_user_id = "test_user_123"
    user_data = {
        "user_context": {
            "user_role": "Test User",
            "experience": "5 years",
            "skills": ["testing", "debugging", "python"],
            "interests": ["automation", "data science"],
            "career_goals": "Become a test engineer"
        },
        "profile_completed": True,
        "test_timestamp": "2025-03-13T12:00:00"
    }

    try:
        # Save test data for users
        print(f"Saving test data for user '{test_user_id}'...")
        data_to_save = {
            "id": test_user_id,
            **user_data
        }

        response = supabase.table('users').upsert(data_to_save).execute()

        if hasattr(response, 'error') and response.error:
            print(f"❌ Error saving test data to users: {response.error}")
            return

        print(f"✅ Successfully saved test data to users")

        # Load test data for users
        print(f"Loading test data for user '{test_user_id}'...")
        response = supabase.table('users').select("*").eq("id", test_user_id).execute()

        if hasattr(response, 'error') and response.error:
            print(f"❌ Error loading test data from users: {response.error}")
            return

        if response.data and len(response.data) > 0:
            print(f"✅ Successfully loaded test data from users")
            print("\nSample of loaded data from users:")
            print(json.dumps(response.data[0], indent=2)[:200] + "...")
        else:
            print(f"❌ No data found for test user in users")

        # Test data for learning_paths table
        learning_path_id = "test_learning_path_123"
        learning_path_data = {
            "id": learning_path_id,
            "user_id": test_user_id,
            "skill": "Python",
            "current_level": "Intermediate",
            "target_level": "Advanced",
            "created_at": "2025-03-13T12:00:00",
            "modified_at": "2025-03-13T12:00:00",
            "structured_data": {"steps": ["Learn OOP", "Build Projects"]},
            "progress": {"completed": 50}
        }

        # Save test data for learning_paths
        print(f"Saving test data for learning path '{learning_path_id}'...")
        response = supabase.table('learning_paths').upsert(learning_path_data).execute()

        if hasattr(response, 'error') and response.error:
            print(f"❌ Error saving test data to learning_paths: {response.error}")
            return

        print(f"✅ Successfully saved test data to learning_paths")

        # Load test data for learning_paths
        print(f"Loading test data for learning path '{learning_path_id}'...")
        response = supabase.table('learning_paths').select("*").eq("id", learning_path_id).execute()

        if hasattr(response, 'error') and response.error:
            print(f"❌ Error loading test data from learning_paths: {response.error}")
            return

        if response.data and len(response.data) > 0:
            print(f"✅ Successfully loaded test data from learning_paths")
            print("\nSample of loaded data from learning_paths:")
            print(json.dumps(response.data[0], indent=2)[:200] + "...")
        else:
            print(f"❌ No data found for test learning path in learning_paths")

        # Test data for skill_analyses table
        skill_analysis_id = "test_skill_analysis_123"
        skill_analysis_data = {
            "id": skill_analysis_id,
            "user_id": test_user_id,
            "created_at": "2025-03-13T12:00:00",
            "target_role": "Senior Developer",
            "structured_data": {"analysis": "Good skills in Python"},
            "raw_analysis": "User is proficient in Python and needs to improve on algorithms."
        }

        # Save test data for skill_analyses
        print(f"Saving test data for skill analysis '{skill_analysis_id}'...")
        response = supabase.table('skill_analyses').upsert(skill_analysis_data).execute()

        if hasattr(response, 'error') and response.error:
            print(f"❌ Error saving test data to skill_analyses: {response.error}")
            return

        print(f"✅ Successfully saved test data to skill_analyses")

        # Load test data for skill_analyses
        print(f"Loading test data for skill analysis '{skill_analysis_id}'...")
        response = supabase.table('skill_analyses').select("*").eq("id", skill_analysis_id).execute()

        if hasattr(response, 'error') and response.error:
            print(f"❌ Error loading test data from skill_analyses: {response.error}")
            return

        if response.data and len(response.data) > 0:
            print(f"✅ Successfully loaded test data from skill_analyses")
            print("\nSample of loaded data from skill_analyses:")
            print(json.dumps(response.data[0], indent=2)[:200] + "...")
        else:
            print(f"❌ No data found for test skill analysis in skill_analyses")

        # Test data for skill_progress table
        skill_progress_id = "test_skill_progress_123"
        skill_progress_data = {
            "id": skill_progress_id,
            "user_id": test_user_id,
            "skill_name": "Python",
            "current_level": "Intermediate",
            "target_level": "Advanced",
            "start_date": "2025-01-01",
            "learning_path": {"path_id": learning_path_id},
            "completed_objectives": ["Learn OOP", "Build a project"],
            "progress_percentage": 50
        }

        # Save test data for skill_progress
        print(f"Saving test data for skill progress '{skill_progress_id}'...")
        response = supabase.table('skill_progress').upsert(skill_progress_data).execute()

        if hasattr(response, 'error') and response.error:
            print(f"❌ Error saving test data to skill_progress: {response.error}")
            return

        print(f"✅ Successfully saved test data to skill_progress")

        # Load test data for skill_progress
        print(f"Loading test data for skill progress '{skill_progress_id}'...")
        response = supabase.table('skill_progress').select("*").eq("id", skill_progress_id).execute()

        if hasattr(response, 'error') and response.error:
            print(f"❌ Error loading test data from skill_progress: {response.error}")
            return

        if response.data and len(response.data) > 0:
            print(f"✅ Successfully loaded test data from skill_progress")
            print("\nSample of loaded data from skill_progress:")
            print(json.dumps(response.data[0], indent=2)[:200] + "...")
        else:
            print(f"❌ No data found for test skill progress in skill_progress")

    except Exception as e:
        print(f"❌ Error testing data operations: {str(e)}")

def main():
    """Main function to check Supabase setup"""
    print("=" * 50)
    print("Supabase Connection Checker")
    print("=" * 50)
    
    # Check connection
    supabase = check_supabase_connection()
    if not supabase:
        return
    
    # Check tables
    check_tables(supabase)
    
    # Test data operations
    test_save_and_load(supabase)
    
    print("\n" + "=" * 50)
    print("Supabase check completed")
    print("=" * 50)

if __name__ == "__main__":
    main() 