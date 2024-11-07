import os
import urllib.parse

def read_keyword_file() -> str:
    # Get the absolute path of the current file
    current_dir = os.path.dirname(__file__)
    
    # Construct the absolute path to keywords.txt
    path = os.path.join(current_dir, '..', 'constans', 'keywords.txt')

    # If file exists, read it and return otherwise return None
    if os.path.exists(path):
        with open(path, 'r') as file:
            return urllib.parse.quote(file.read())
    else:
        return None
      