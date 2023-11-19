# <Utils.py>

def print_dot_n_times(n):
    for i in range(n):
        print('·')


def print_tree(tree, deep=0):
    if isinstance(tree, list) or isinstance(tree, tuple):
        for i in range(len(tree)):
            print_tree(tree[i], deep + 1)
    else:
        print_dot_n_times(deep)
        print(str(tree))
