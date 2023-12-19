import numpy as np
import load_names
import random
from functools import total_ordering

"""
This files includes all functionality for the class Person.
The Person class stores the name, age, weight, and height of a person.
create_persons_list provides a way to randomly create a list of dummy persons.
This is mainly meant to make testing easier.

Complete, the rest of the Person class and the function create_persons_list.
"""

# NAMES is a list or array with common first names.
NAMES = load_names.load_names()  # Variables in the global namespace should be capitalized.


# Decorator to make code dryer, fills in the rest of the orderings after we explicitly define equality, inequality and greater than/less than
# Reference: https://portingguide.readthedocs.io/en/latest/comparisons.html
@total_ordering 
class Person():
    """
    Here, you will create the class Person.

    The __init__ method is already given and it is not allowed to create new object attribute (self.some_name = ...).

    Add all the needed (magic) methods described in the grading criteria.
    This includes a method such that printed objects are readable for the end user.
    Also, this class should also be made:
    comparable, sortable, subscriptable, iterable, and castable (to float, int, and string)
    """
    def __init__(self, name, age, height, weight):
        self.__name__ = name
        self.__age__ = age
        self.__height__ = height
        self.__weight__= weight
    def attributes(self):
        return [self.__name__, self.__age__, self.__height__, self.__weight__]
    def __repr__(self):
        return "Name: " + str(self.__name__) + " Age: " + str(self.__age__) + " Height: " + str(self.__height__) + "cm" + " Weight: " + str(self.__weight__) + "kg"
    def __str__(self):
        return self.__name__
    def __int__(self):
        return self.__age__
    def __float__(self):
        return self.__age__
    def __eq__(self, other):
        return self.__height__ == other.__height__
    def __gt__(self, other):
        return self.__height__ > other.__height__
    def __iter__(self):
        for attr in self.attributes():
            yield attr
    def __getitem__(self, idx):
        return self.attributes()[idx]


def random_selection(entry_list):
    return random.choice(entry_list)
    

def create_persons_list(n=10):
    """
    Create a function that returns a list containing `n` Person objects.

    Each Person object should be randomly initialized with:
     - A name from the global list NAMES.
     - An age between 18 and 100.
     - A height between 150 and 200 cm.
     - A weight between 45 and 100 kg.
    """
    person_list = []
    for n in range(n):
        name = random.choice(NAMES)
        age = random.randint(18,100)
        height = random.randint(150,200)	
        weight = random.randint(45,100)
        person = Person(name, age, height, weight)
        person_list.append(person)
    return person_list






