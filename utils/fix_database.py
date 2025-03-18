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

def main():
    """Main function to fix Supabase schema"""
    print("=" * 50)
    print("Supabase Database Fix Script")
    print("=" * 50)
    
    # Connect to Supabase
    supabase = connect_to_supabase()
    if not supabase:
        return
    
    print("\nIMPORTANT: The database schema needs to be fixed.")
    print("Please run the following SQL in your Supabase SQL Editor:")
    print("""
-- First, let's back up the existing data
CREATE TABLE IF NOT EXISTS users_backup AS SELECT * FROM users;
CREATE TABLE IF NOT EXISTS learning_paths_backup AS SELECT * FROM learning_paths;
CREATE TABLE IF NOT EXISTS skill_analyses_backup AS SELECT * FROM skill_analyses;

-- Drop existing tables
DROP TABLE IF EXISTS learning_paths;
DROP TABLE IF EXISTS skill_analyses;
DROP TABLE IF EXISTS users;

-- Create tables with correct schema
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

-- Migrate data from backup tables (if needed)
-- This is a simplified example and may need to be adjusted based on your actual data
INSERT INTO users (id, user_data, created_at, updated_at)
SELECT 
    COALESCE(id, gen_random_uuid()) as id,
    jsonb_build_object(
        'user_context', jsonb_build_object(
            'user_role', user_role,
            'target_role', target_role,
            'experience', experience,
            'skills', CASE WHEN skills IS NULL THEN '[]'::jsonb ELSE to_jsonb(skills) END,
            'interests', CASE WHEN interests IS NULL THEN '[]'::jsonb ELSE to_jsonb(interests) END,
            'career_goals', career_goals
        ),
        'profile_completed', true,
        'last_updated', last_updated
    ) as user_data,
    created_at,
    last_updated as updated_at
FROM users_backup
WHERE user_role IS NOT NULL OR target_role IS NOT NULL OR experience IS NOT NULL;

-- Note: You may need to adjust the migration for learning_paths and skill_analyses
-- based on your actual data structure
    """)
    
    print("\nAfter running the SQL, run the following command to verify the schema:")
    print("python utils/check_schema.py")
    
    print("\n" + "=" * 50)
    print("Database fix instructions completed")
    print("=" * 50)

if __name__ == "__main__":
    main() 