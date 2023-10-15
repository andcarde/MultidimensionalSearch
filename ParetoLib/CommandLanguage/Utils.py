# <Utils.py>

def print_dot_n_times(n):
    for i in range(n):
        print('·')


def print_tree(tree, deep=0):
    print_dot_n_times(tree[0])
    for i in range(1, len(tree)):
        if isinstance(tree[i], list):
            print_tree(list, deep + 1)
        else:
            print_dot_n_times(deep + 1)
