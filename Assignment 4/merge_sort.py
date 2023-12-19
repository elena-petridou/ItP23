import person


def mergesort(lst, key, reverse):
    """
    This function implements the recursive part of merge sort.
    For a full explanation see assignment3 -> Merge sort
    """
    no_of_elements = len(lst)
    if no_of_elements > 1:
        halfway_point = int(no_of_elements/2)
        left_list = mergesort(lst[:halfway_point], key=False, reverse=False)
        right_list = mergesort(lst[halfway_point:], key=False, reverse=False)
        sorted_array = merge(left_list, right_list, key=False, reverse=False)
        return sorted_array
    else:
        return lst




def merge(lst1, lst2, key, reverse):
    """
    This function implements the merging part of merge sort.
    Here, two sorted lists are merged into one sorted list.
    You can either use Algorithm 1 or 2 explained in assignment4.
    """
    sorted_list = []
    i = 0
    j = 0
    while i<len(lst1) and j<len(lst2):
        if lst1[i] <= lst2[j]:
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
    array = [1,4,5,5,2,4454]
    sorted_array = mergesort(array, key=False,reverse=False)
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