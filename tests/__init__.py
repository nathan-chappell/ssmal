import sys
from pathlib import Path

def path_fix():
    MAX_PATH_SEARCH_DEPTH = 6
    p = Path()
    i = 0
    while not (p / '.git').exists() and i < MAX_PATH_SEARCH_DEPTH:
        p = p.parent
        i += 1
    
    if i == MAX_PATH_SEARCH_DEPTH:
        raise Exception('Maximum depth reached while fixing sys.path.  Execute tests from the repo directory.')
    if not (p / 'src' / 'processors').exists():
        raise Exception('Error searching for repo root.  Execute tests from the repo directory.')
    
    p = p / 'src'
    sys.path.insert(0, str(p.resolve()))