from pathlib import Path
import numpy as np

"""
This file provides includes a function to load in the names from the text file names.txt.

Finish, the code in load_names. 
"""


def remove_newline(name):
    if '\n' in name:
        new_name = name.replace('\n', '')
        return new_name
    else:
        return name


def load_names():
    """
    Load the file names.txt and return an array or list with the names.
    """
    # Find the text file on your computer and make it operating system insensitive.
    # path can be used to load the text file.
    # This finds the directory where you run the python interpreter with the name __main__.
    path = Path.cwd()
    # This finds the correct path to names.txt from where you run the python file
    path = path.glob('**/names.txt').__next__()
    with open(path, 'r') as txt:
        names = txt.readlines()
    formatted_names = [remove_newline(name) for name in names]
    return formatted_names



