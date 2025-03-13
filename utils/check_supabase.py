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
    
    test_user_id = "test_user_123"
    test_data = {
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
        # Save test data
        print(f"Saving test data for user '{test_user_id}'...")
        data_to_save = {
            "id": test_user_id,
            **test_data
        }
        
        response = supabase.table('users').upsert(data_to_save).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"❌ Error saving test data: {response.error}")
            return
        
        print(f"✅ Successfully saved test data")
        
        # Load test data
        print(f"Loading test data for user '{test_user_id}'...")
        response = supabase.table('users').select("*").eq("id", test_user_id).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"❌ Error loading test data: {response.error}")
            return
        
        if response.data and len(response.data) > 0:
            print(f"✅ Successfully loaded test data")
            print("\nSample of loaded data:")
            print(json.dumps(response.data[0], indent=2)[:200] + "...")
        else:
            print(f"❌ No data found for test user")
    
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