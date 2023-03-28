
def printTree(tree):
    for j in len(tree):
        print('{(' + j + ')')
        if (len(j) == 1):
            print(j)
        else:
            printTree(tree[j])
        print('},')
