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

def connect_to_supabase():
    """Connect to Supabase and return client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: Supabase credentials not found in .env file")
        print("Please ensure SUPABASE_URL and SUPABASE_KEY are set in your .env file")
        return None
    
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Successfully connected to Supabase at {SUPABASE_URL}")
        return supabase
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {str(e)}")
        return None

def create_test_data(supabase):
    """Create test data in Supabase"""
    print("\nCreating test data...")
    
    test_user_id = "test_user_123"
    test_data = {
        "user_context": {
            "user_id": test_user_id,
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
        
        # Convert to JSON string for user_data column
        user_data_json = json.dumps(test_data)
        
        data_to_save = {
            "id": test_user_id,
            "user_data": user_data_json
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
        print(f"❌ Error creating test data: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Main function to set up Supabase tables"""
    print("=" * 50)
    print("Supabase Setup Script")
    print("=" * 50)
    
    # Connect to Supabase
    supabase = connect_to_supabase()
    if not supabase:
        return
    
    # Create test data
    create_test_data(supabase)
    
    print("\n" + "=" * 50)
    print("Supabase setup completed")
    print("=" * 50)
    print("\nIMPORTANT: Make sure to create the following tables in your Supabase project:")
    print("1. users - with columns: id (primary key), user_data (jsonb)")
    print("2. learning_paths - with columns: id (primary key), user_id (foreign key), path_data (jsonb)")
    print("3. skill_analyses - with columns: id (primary key), user_id (foreign key), analysis_data (jsonb)")
    print("\nYou can create these tables through the Supabase dashboard.")

if __name__ == "__main__":
    main() 