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

def check_table_schema(supabase, table_name):
    """Check the schema of a table in Supabase"""
    print(f"\nChecking schema for table '{table_name}'...")
    
    try:
        # Try to get the schema of the table
        # This is a workaround since Supabase doesn't have a direct API for schema inspection
        # We'll try to select a single row and check the response
        response = supabase.table(table_name).select('*').limit(1).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"❌ Error accessing table '{table_name}': {response.error}")
            return False
        
        # If we get here, the table exists
        print(f"✅ Table '{table_name}' exists")
        
        # Try to get column information by examining the response
        if response.data:
            print(f"Columns in '{table_name}':")
            for column_name in response.data[0].keys():
                print(f"  - {column_name}")
        else:
            # If there's no data, we can't determine the columns
            print(f"No data in table '{table_name}', cannot determine columns")
            
            # Try to insert a dummy row to get column information
            try:
                print(f"Attempting to get column information by inserting a dummy row...")
                
                # Create a dummy row with minimal data
                dummy_data = {"id": "00000000-0000-0000-0000-000000000000"}
                
                # Try to insert the dummy row
                dummy_response = supabase.table(table_name).insert(dummy_data).execute()
                
                if hasattr(dummy_response, 'error') and dummy_response.error:
                    print(f"❌ Error inserting dummy row: {dummy_response.error}")
                    
                    # Try to parse the error message to get column information
                    error_msg = str(dummy_response.error)
                    if "missing" in error_msg and "column" in error_msg:
                        print(f"Required columns based on error message:")
                        # Extract column names from error message
                        # This is a crude approach and may not work for all error messages
                        import re
                        columns = re.findall(r'"([^"]+)"', error_msg)
                        for column in columns:
                            print(f"  - {column}")
                else:
                    print(f"Columns in '{table_name}' based on dummy row:")
                    for column_name in dummy_response.data[0].keys():
                        print(f"  - {column_name}")
                    
                    # Delete the dummy row
                    supabase.table(table_name).delete().eq("id", "00000000-0000-0000-0000-000000000000").execute()
            except Exception as e:
                print(f"❌ Error getting column information: {str(e)}")
        
        return True
    except Exception as e:
        print(f"❌ Error checking schema for table '{table_name}': {str(e)}")
        return False

def main():
    """Main function to check Supabase schema"""
    print("=" * 50)
    print("Supabase Schema Checker")
    print("=" * 50)
    
    # Connect to Supabase
    supabase = connect_to_supabase()
    if not supabase:
        return
    
    # Check schema for required tables
    tables = ['users', 'learning_paths', 'skill_analyses']
    
    for table in tables:
        check_table_schema(supabase, table)
    
    print("\n" + "=" * 50)
    print("Schema check completed")
    print("=" * 50)
    print("\nIMPORTANT: If any tables or columns are missing, run the following SQL in your Supabase SQL Editor:")
    print("""
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    user_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS learning_paths (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    path_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS skill_analyses (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    analysis_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
    """)

if __name__ == "__main__":
    main() 