import person
from person import create_persons_list

def key_selection(key):
    if type(key) == str:
        lower_key = key.lower()
        match lower_key:
            case "name":
                return 0
            case "age":
                return 1
            case "height":
                return 2
            case "weight":
                return 3
    else:
        return key
            


def mergesort(lst, key, reverse=False):
    """
    This function implements the recursive part of merge sort.
    For a full explanation see assignment3 -> Merge sort
    """
    key = key_selection(key)
    no_of_elements = len(lst)
    if no_of_elements > 1:
        halfway_point = int(no_of_elements/2)
        left_list = mergesort(lst[:halfway_point], key, reverse=False)
        right_list = mergesort(lst[halfway_point:], key, reverse=False)
        sorted_array = merge(left_list, right_list, key, reverse=False)
        return sorted_array
    else:
        return lst


def sort_with_key(key, left_element, right_element):
    if key != None:
        left_element = left_element[key]
        right_element = right_element[key]
    return left_element, right_element

    

def merge(lst1, lst2, key, reverse=False):
    """
    This function implements the merging part of merge sort.
    Here, two sorted lists are merged into one sorted list.
    You can either use Algorithm 1 or 2 explained in assignment4.
    """
    sorted_list = []
    i = 0
    j = 0
    while i<len(lst1) and j<len(lst2):
        left_element, right_element = sort_with_key(key, lst1[i], lst2[j])
        if left_element <= right_element:
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
    array = create_persons_list()
    sorted_array = mergesort(array, key=3, reverse=False)
    print(sorted_array)

    
if __name__ == "__main__":
    main()

# TODO finish the script here,
#  if you want you can also use a main function and the if __name__ == "__main__": control flow.



'''
PSEUDOCODE

- Split original list until only lists of length 1 remain
- Check lists of length 1, and see whether 

'''