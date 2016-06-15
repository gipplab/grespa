import random


def pop_random(list):
    """ Pops a random item from the given list in constant time.

    :param list: list to pop one random item from
    :return: random item from the given list
    """
    num = len(list)
    if num == 0:
        return None
    # pop(idx) is O(n), so we select and swap, then pop at the back
    i = random.randrange(num)
    list[i], list[-1] = list[-1], list[i] # swap position with last pos in O(1)
    return list.pop() # pop last element in O(1)
