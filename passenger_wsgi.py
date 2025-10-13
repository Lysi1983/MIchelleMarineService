import os
import sys

# Add the application's directory to the system path
sys.path.insert(0, os.path.dirname(__file__))

# Import the application object
# Replace 'app' with the name of your Python file (e.g., main.py becomes 'main')
# Replace the second 'app' with the name of your Flask instance variable
from app import app as application
