import person
from person import create_persons_list

keys = {"name": 0, "age": 1, "weight": 2, "height": 3}
arguments = {number: argument for argument, number in keys.items()}

# Errors and checks to handle unrecognised user input
class CustomKeyError():
    def __init__(self):
        raise Exception("Sorry, key argument not recognised. You may use: age, weight, height, name, specify no key, or a number between 0 and 3 (inclusive)")

class ReverseError():
    def __init__(self):
        raise Exception("Argument 'reverse' can be only True = 1, False = 0, or left out. No other inputs are recognised. Please try again")


def check_reverse(reverse):
    if reverse == True or reverse == False or reverse == 1 or reverse == 0:
        return reverse
    if reverse.lower() == 'true':
        return True
    if reverse.lower() == 'false':
        return False
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
    elif key == None:
        pass
    else:
        raise CustomKeyError()

def determine_reverse(reverse):
    if reverse == True:
        return " from Z to A"
    if reverse == False:
        return " from A to Z"

def produce_sorting_explanation(var_type, key = False, reverse = False):
    reverse_sorted = " from lowest to highest"
    if type(key) == int:
        key_str = arguments[key]
        key_sorted_with = "on " + key_str
        if key_str == "name":
            key_sorted_with = "alphabetically on name"
            reverse_sorted = determine_reverse(reverse)
    elif key == None and (var_type == tuple or var_type == list):
        key_sorted_with = "alphabetically on name"
        reverse_sorted = determine_reverse(reverse)
    else:
        key_sorted_with = "on height"
    match reverse:
        case True:
            reverse_sorted = " from highest to lowest"
    sorting_explanation = "The following list was sorted " + key_sorted_with + reverse_sorted
    return sorting_explanation            



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


def mergesort(lst, key = None, reverse = False):
    """
    This function implements the recursive part of merge sort.
    For a full explanation see assignment3 -> Merge sort
    """
    key = key_selection(key)
    reverse = check_reverse(reverse)
    no_of_elements = len(lst)
    sorting_explanation = produce_sorting_explanation(type(lst[0]),key, reverse)

    if no_of_elements > 1:
        halfway_point = int(no_of_elements/2)
        left_list, sorting_explanation = mergesort(lst[:halfway_point], key, reverse)
        right_list, sorting_explanation = mergesort(lst[halfway_point:], key, reverse)
        sorted_array = merge(left_list, right_list, key, reverse)
        return sorted_array, sorting_explanation
    else:
        return lst, sorting_explanation
    


# Implementing key sorting in a way that does not change the code required to sort without a key
def sort_with_key(left_element, right_element, key = None):
    if key != None:
        left_element = left_element[key]
        right_element = right_element[key]
    return left_element, right_element

# As above, implementing reverse_sort so that it flips the logic when reverse argument is specified, so that sorting with/without the key in 
# mergesort itself uses the same code    
def reverse_sort(left_element, right_element, reverse = False):
    match reverse:
        case False:
            return left_element <= right_element
        case True:
            return left_element >= right_element


'''In main(), I left some tests to demonstrate functionality. I tried others too, but ommitted them for brevity
'''

def main():
    array = create_persons_list(10)
    # Cast to tuple and sort with no arguments: (results in sorting by name)
    tuple_array = []
    for person in array:
        tuple_array.append(tuple(person))
    sorted_array, sorting_explanation = mergesort(tuple_array)
    print("Tuple sorting without parameter: ", sorting_explanation, sorted_array)

    # Sort tuple with weight as parameter, in reverse:
    sorted_2, explanation_2 = mergesort(tuple_array, key = "weight", reverse=True)
    print("Tuple sorting with weight as parameter, in reverse: ", explanation_2, sorted_2)
    
    # Cast to list and sort with no arguments (sorting alphabetically by name)
    list_array = []
    for person in array:
        list_array.append(list(person))
    sorted_3, explanation_3 = mergesort(list_array)
    print("List sorting with no parameters: ", explanation_3, sorted_3)

    # Sort lists of persons based on weight
    sorted_4, explanation_4 = mergesort(list_array, key = "weight")
    print ("List sorting with weight as argument: ", explanation_4, sorted_4)

    # Sort lists of persons based on index position 1 (age)
    sorted_5, explanation_5 = mergesort(list_array, key= 1)
    print("List sorting on index position 1 (age): ", explanation_5, sorted_5)

    # Sort person objects on age, reversed
    sorted_6, explanation_6 = mergesort(array, key = "age", reverse=True)
    print("Uncasted objects sorted on age in reverse: ", explanation_6, sorted_6)

    # Results of casting the person object into various types:
    print("Integer: ", int(array[0]))
    print("Float: ", float(array[0]))
    print("List: ", list(array[0]))
    print("String: ", str(array[0]))

    # Result of printing objects (__repr__):
    print(array)


    
if __name__ == "__main__":
    main()


