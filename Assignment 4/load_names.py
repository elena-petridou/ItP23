from pathlib import Path
import numpy as np

"""
This file provides includes a function to load in the names from the text file names.txt.

Finish, the code in load_names. 
"""

def make_names_into_list(txt):
    ls_of_names = []
    word = []
    for letter in txt:
        if letter != "\n":
            word.append(letter)
        else:
            word_str = ''.join(word)
            ls_of_names.append(word_str)
            word = []
    return ls_of_names




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
    f = open(path, 'r')
    names = f.read()
    name_list = make_names_into_list(names)
    return name_list

    



