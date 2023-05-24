import os
import sys

def get_homedir():
    """Get home dir of project."""
    if sys.platform == 'win32':
        homedir = os.environ['USERPROFILE']
    elif sys.platform == 'linux' or sys.platform == 'darwin':
        homedir = os.environ['HOME']

    return homedir