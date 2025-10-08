#!/usr/bin/env python3

# Test basic functionality without imports
print("Test starting")

# Test file operations
import os
print(f"Current directory: {os.getcwd()}")

# List files
files = os.listdir('.')
print(f"Files in directory: {len(files)}")

# Check for specific files
db_files = [f for f in files if f.endswith('.db')]
print(f"Database files found: {db_files}")

# Test basic import
try:
    import sys
    print("Basic imports work")

    # Try app imports
    sys.path.append('.')
    print("Path updated")

    from app.database import Base
    print("Database import successful")

except Exception as e:
    print(f"Import error: {e}")

print("Test completed")