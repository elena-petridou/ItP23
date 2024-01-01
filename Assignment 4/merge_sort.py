import person
from person import create_persons_list

keys = {"name": 0, "age": 1, "height": 2, "weight": 3}

class CustomKeyError():
    def __init__(self):
        raise Exception("Sorry, key argument not recognised. You may use: age, weight, height, name, specify no key, or a number between 0 and 3 (inclusive)")

class ReverseError():
    def __init__(self):
        raise Exception("Argument 'reverse' can be only True = 1, False = 0, or left out. No other inputs are recognised. Please try again")


def check_reverse(reverse):
    if reverse == True or reverse == False or reverse == 1 or reverse == 0 or reverse == 'True' or reverse == 'False':
        return reverse
    else:
        raise ReverseError()

def check_numeric_key(key):
    if key == 0 or key == 1 or key == 2 or key == 3:
        return key
    else:
        raise CustomKeyError()


def key_selection(key):
    if type(key) == str:
        lower_key = key.lower()
        if lower_key in keys:
            return keys[lower_key]
        elif key.isnumeric():
            numeric_key = int(lower_key)
            response = check_numeric_key(numeric_key)
            return response
        else:
            raise CustomKeyError()
    elif type(key) == int or type(key) == float:
        numeric_key = int(key)
        response = check_numeric_key(numeric_key)
        return response
    else:
        raise CustomKeyError
            


def mergesort(lst, key = None, reverse = False):
    """
    This function implements the recursive part of merge sort.
    For a full explanation see assignment3 -> Merge sort
    """
    key = key_selection(key)
    reverse = check_reverse(reverse)
    no_of_elements = len(lst)
    if no_of_elements > 1:
        halfway_point = int(no_of_elements/2)
        left_list = mergesort(lst[:halfway_point], key, reverse)
        right_list = mergesort(lst[halfway_point:], key, reverse)
        sorted_array = merge(left_list, right_list, key, reverse)
        return sorted_array
    else:
        return lst


def sort_with_key(left_element, right_element, key = None):
    if key != None:
        left_element = left_element[key]
        right_element = right_element[key]
    return left_element, right_element

    
def reverse_sort(left_element, right_element, reverse = False):
    match reverse:
        case False:
            return left_element <= right_element
        case True:
            return left_element >= right_element


def merge(lst1, lst2, key = None, reverse = False):
    """
    This function implements the merging part of merge sort.
    Here, two sorted lists are merged into one sorted list.
    You can either use Algorithm 1 or 2 explained in assignment4.
    """
    sorted_list = []
    i = 0
    j = 0
    while i<len(lst1) and j<len(lst2):
        left_element, right_element = sort_with_key(lst1[i], lst2[j], key)
        if reverse_sort(left_element, right_element, reverse):
            sorted_list.append(lst1[i])
            i += 1
        else:
            sorted_list.append(lst2[j])
            j += 1
    for ele in lst1[i:]:
        sorted_list.append(ele)
    for ele in lst2[j:]:
        sorted_list.append(ele)
    return sorted_list

def main():
    array = create_persons_list(10)
    # sorted_array = mergesort(array, key="weight", reverse='False')  
    

    
if __name__ == "__main__":
    main()


