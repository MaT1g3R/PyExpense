from random import choice
from string import printable

def random_str(length):
    return ''.join(choice(printable) for _ in range(length))


def rand_strs(length, amt, unique):
    res = []
    for _ in range(amt):
        rand = random_str(length)
        if unique:
            while rand in res:
                rand = random_str(length)
        res.append(rand)
    return res
