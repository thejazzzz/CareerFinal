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

def check_table_data(supabase, table_name):
    """Check if a table has any data"""
    try:
        response = supabase.table(table_name).select("*").limit(10).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"❌ Error querying {table_name}: {response.error}")
            return False, []
        
        data = response.data
        has_data = len(data) > 0
        
        if has_data:
            print(f"✅ Table '{table_name}' has {len(data)} rows of data")
            print(f"Sample data: {json.dumps(data[0], indent=2)}")
        else:
            print(f"ℹ️ Table '{table_name}' is empty")
        
        return has_data, data
    except Exception as e:
        print(f"❌ Error checking data in {table_name}: {str(e)}")
        return False, []

def main():
    """Main function to check data in Supabase tables"""
    print("=" * 50)
    print("Supabase Data Check Script")
    print("=" * 50)
    
    # Connect to Supabase
    supabase = connect_to_supabase()
    if not supabase:
        return
    
    # Check data in each table
    tables = ['users', 'learning_paths', 'skill_analyses']
    
    for table in tables:
        print(f"\n{'-' * 30}")
        print(f"Checking data in '{table}' table:")
        has_data, data = check_table_data(supabase, table)
    
    print("\n" + "=" * 50)
    print("Data check completed")
    print("=" * 50)

if __name__ == "__main__":
    main() 