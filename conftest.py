import sys
import os

# This tells PyTest to look in the current directory for modules like 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))