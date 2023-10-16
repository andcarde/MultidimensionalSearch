import tkinter as tk


class TreeNode:

    def __init__(self, value):
        self.value = value
        self.sons = []
        self.descendants = 0
        self.father = None

    def add_son(self, son):
        son.father = self
        self.sons.append(son)
        new_descendants = 0
        if self.descendants > 0:
            if son.descendants > 0:
                self.descendants += son.descendants
                new_descendants += son.descendants
            else:
                self.descendants += 1
                new_descendants += 1
        elif son.descendants > 0:
            self.descendants += son.descendants
            new_descendants += son.descendants - 1
        else:
            self.descendants += 1
        if self.father is not None:
            self.father.descendants += new_descendants

    def get_long(self):
        if self.descendants > 0:
            return self.descendants
        else:
            return 1


def list_to_tree(list1):
    if not isinstance(list1, tuple) and not isinstance(list1, list):
        return TreeNode(list1)
    else:
        if isinstance(list1[0], tuple) or isinstance(list1[0], list):
            tree = TreeNode('[]')
            for i in range(0, len(list1)):
                tree.add_son(list_to_tree(list1[i]))
            return tree
        else:
            tree = TreeNode(list1[0])
            for i in range(1, len(list1)):
                tree.add_son(list_to_tree(list1[i]))
            return tree


def create_tree1():
    root = TreeNode(1)

    node2 = TreeNode(2)
    # Adding node2 to root before adding sons to node2
    root.add_son(node2)
    node2.add_son(TreeNode(4))
    node2.add_son(TreeNode(5))

    node3 = TreeNode(3)
    node3.add_son(TreeNode(6))
    node3.add_son(TreeNode(7))
    node3.add_son(TreeNode(8))
    # Adding node3 to root after adding sons to node2
    root.add_son(node3)

    return root


def create_tree2():
    list1 = ('MUL', 2, ('AND', 'x', 'y'), (('SUM', '='), 1, 2))
    return list_to_tree(list1)


class TreeDrawer:

    def __init__(self, canvas):
        self.canvas = canvas
        self.x_offset = 30
        self.y_offset = 30
        # self.x_initial = 400
        self.x_initial = 700
        self.y_initial = 100

    def draw_tree(self, tree):
        if isinstance(tree, TreeNode):
            self.draw_node(tree, self.x_initial, self.y_initial)

    def draw_node(self, node, x, y):
        # Draw the node as a rectangle with its value
        self.canvas.create_rectangle(x - self.x_offset, y - self.y_offset,
                                     x + self.x_offset, y + self.y_offset, fill="white")
        self.canvas.create_text(x, y, text=str(node.value))
        # Draw branches to child nodes
        if len(node.sons) > 0:
            x_son = x - (node.get_long() * (self.x_offset * 3) - self.x_offset) / 2
            y_son = y + 3 * self.y_offset
            for son in node.sons:
                x_space = (son.get_long() * (self.x_offset * 3) - self.x_offset) / 2
                x_son += x_space
                self.canvas.create_line(x, y + self.y_offset, x_son, y_son - self.y_offset)
                self.draw_node(son, x_son, y_son)
                x_son += x_space + self.x_offset


def view_tree(tree):
    root = tk.Tk()
    root.title("Tree Viewer")

    # canvas = tk.Canvas(root, width=800, height=600)
    canvas = tk.Canvas(root, width=1400, height=700)
    canvas.pack()

    TreeDrawer(canvas).draw_tree(tree)

    root.mainloop()


def tree_viewer_test():
    tree1 = create_tree1()
    view_tree(tree1)
    tree2 = create_tree2()
    view_tree(tree2)


if __name__ == "__main__":
    tree_viewer_test()
