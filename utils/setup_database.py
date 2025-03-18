import os
import sys
import json
import uuid
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
    try:
        # Create a test user
        user_id = str(uuid.uuid4())
        user_data = {
            "user_context": {
                "user_id": user_id,
                "user_role": "Software Developer",
                "target_role": "Senior Software Engineer",
                "experience": "5 years",
                "skills": ["Python", "JavaScript", "SQL"],
                "interests": ["Machine Learning", "Web Development"],
                "career_goals": "Become a technical leader in AI applications"
            },
            "profile_completed": True,
            "last_updated": "2023-01-01T00:00:00"
        }
        
        # Save user data
        user_response = supabase.table('users').upsert({
            "id": user_id,
            "user_data": user_data
        }).execute()
        
        if hasattr(user_response, 'error') and user_response.error:
            print(f"❌ Error creating test user: {user_response.error}")
            return False
        
        print(f"✅ Created test user with ID: {user_id}")
        
        # Create a test learning path
        path_id = str(uuid.uuid4())
        path_data = {
            "id": path_id,
            "title": "Becoming a Senior Software Engineer",
            "description": "A learning path to advance from mid-level to senior software engineer",
            "skills": ["System Design", "Architecture", "Leadership"],
            "resources": [
                {"title": "Clean Code", "type": "Book", "url": "https://example.com/clean-code"},
                {"title": "System Design Interview", "type": "Course", "url": "https://example.com/system-design"}
            ],
            "progress": {"completed": 0, "total": 2}
        }
        
        # Save learning path
        path_response = supabase.table('learning_paths').upsert({
            "id": path_id,
            "user_id": user_id,
            "path_data": path_data
        }).execute()
        
        if hasattr(path_response, 'error') and path_response.error:
            print(f"❌ Error creating test learning path: {path_response.error}")
            return False
        
        print(f"✅ Created test learning path with ID: {path_id}")
        
        # Create a test skill analysis
        analysis_id = str(uuid.uuid4())
        analysis_data = {
            "id": analysis_id,
            "created_at": "2023-01-01T00:00:00",
            "target_role": "Senior Software Engineer",
            "skills_gap": ["System Design", "Leadership", "Mentoring"],
            "strengths": ["Python", "Problem Solving", "Algorithms"],
            "recommendations": [
                "Take a course on system design",
                "Volunteer for team lead opportunities",
                "Mentor junior developers"
            ]
        }
        
        # Save skill analysis
        analysis_response = supabase.table('skill_analyses').upsert({
            "id": analysis_id,
            "user_id": user_id,
            "analysis_data": analysis_data
        }).execute()
        
        if hasattr(analysis_response, 'error') and analysis_response.error:
            print(f"❌ Error creating test skill analysis: {analysis_response.error}")
            return False
        
        print(f"✅ Created test skill analysis with ID: {analysis_id}")
        
        return True
    except Exception as e:
        print(f"❌ Error creating test data: {str(e)}")
        return False

def migrate_local_data(supabase):
    """Migrate local user data to Supabase"""
    try:
        data_dir = "data"
        if not os.path.exists(data_dir):
            print(f"ℹ️ No local data directory found at {data_dir}")
            return True
        
        # Get all JSON files in the data directory
        json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        
        if not json_files:
            print(f"ℹ️ No JSON files found in {data_dir}")
            return True
        
        print(f"Found {len(json_files)} JSON files to migrate")
        
        for file_name in json_files:
            try:
                file_path = os.path.join(data_dir, file_name)
                
                # Extract user_id from filename
                if file_name.startswith("user_") and file_name.endswith(".json"):
                    user_id_part = file_name[5:-5]  # Remove "user_" prefix and ".json" suffix
                    
                    # Handle the legacy "anonymous" user
                    if user_id_part == "anonymous":
                        user_id = str(uuid.uuid4())
                        print(f"Converting anonymous user to UUID: {user_id}")
                    else:
                        # Validate UUID format
                        try:
                            uuid.UUID(user_id_part)
                            user_id = user_id_part
                        except ValueError:
                            user_id = str(uuid.uuid4())
                            print(f"Invalid UUID in filename {file_name}, generating new UUID: {user_id}")
                else:
                    user_id = str(uuid.uuid4())
                    print(f"File {file_name} doesn't follow naming convention, generating UUID: {user_id}")
                
                # Load the JSON data
                with open(file_path, 'r') as f:
                    user_data = json.load(f)
                
                # Update user_id in user_context if it exists
                if "user_context" in user_data:
                    user_data["user_context"]["user_id"] = user_id
                
                # Save to Supabase
                response = supabase.table('users').upsert({
                    "id": user_id,
                    "user_data": user_data
                }).execute()
                
                if hasattr(response, 'error') and response.error:
                    print(f"❌ Error migrating data from {file_name}: {response.error}")
                else:
                    print(f"✅ Successfully migrated data from {file_name} to Supabase")
            
            except Exception as e:
                print(f"❌ Error processing file {file_name}: {str(e)}")
        
        return True
    except Exception as e:
        print(f"❌ Error migrating local data: {str(e)}")
        return False

def main():
    """Main function to set up Supabase database"""
    print("=" * 50)
    print("Supabase Database Setup Script")
    print("=" * 50)
    
    # Connect to Supabase
    supabase = connect_to_supabase()
    if not supabase:
        return
    
    # Check if tables exist by trying to query them
    try:
        users_response = supabase.table('users').select("*").limit(1).execute()
        learning_paths_response = supabase.table('learning_paths').select("*").limit(1).execute()
        skill_analyses_response = supabase.table('skill_analyses').select("*").limit(1).execute()
        
        tables_exist = (
            not (hasattr(users_response, 'error') and users_response.error) and
            not (hasattr(learning_paths_response, 'error') and learning_paths_response.error) and
            not (hasattr(skill_analyses_response, 'error') and skill_analyses_response.error)
        )
        
        if tables_exist:
            print("✅ All required tables exist in Supabase")
        else:
            print("❌ Some tables are missing in Supabase")
            print("\nPlease run the following SQL in your Supabase SQL Editor to create the necessary tables:")
            print("""
CREATE TABLE users (
    id UUID PRIMARY KEY,
    user_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE learning_paths (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    path_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE skill_analyses (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    analysis_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
            """)
            print("\nAfter creating the tables, run this script again to continue setup.")
            return
    except Exception as e:
        print(f"❌ Error checking tables: {str(e)}")
        print("\nPlease run the following SQL in your Supabase SQL Editor to create the necessary tables:")
        print("""
CREATE TABLE users (
    id UUID PRIMARY KEY,
    user_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE learning_paths (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    path_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE skill_analyses (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    analysis_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
        """)
        print("\nAfter creating the tables, run this script again to continue setup.")
        return
    
    # Migrate local data to Supabase
    print("\nMigrating local user data to Supabase...")
    migrate_success = migrate_local_data(supabase)
    
    if migrate_success:
        print("✅ Local data migration completed")
    else:
        print("❌ Error migrating local data")
    
    # Create test data
    print("\nCreating test data in Supabase...")
    test_data_success = create_test_data(supabase)
    
    if test_data_success:
        print("✅ Test data creation completed")
    else:
        print("❌ Error creating test data")
    
    print("\n" + "=" * 50)
    print("Database setup completed")
    print("=" * 50)

if __name__ == "__main__":
    main() 