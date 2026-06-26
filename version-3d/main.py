import sys
import os

# Add parent for shared utils if needed
sys.path.insert(0, os.path.dirname(__file__))

from pet3d_app import main

if __name__ == "__main__":
    main()
