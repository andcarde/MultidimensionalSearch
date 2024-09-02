
"""
--- Tests / Language ---
El modulo Tests/Language es un visualizador de árboles (estructuras de datos). Su utilidad en este proyecto es la de
comprobar la correcta traducción entre los lenguajes STLE1 y STLE3 (aplicación de STLE2).

--- gui.py ---
Contedor de la vista, utiliza la biblioteca 'tkinter'.
"""

import tkinter as tk
from tkinter import ttk


def draw_tree(canvas, node, x, y, x_space, y_space):
    # Dibujar el nodo actual
    canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="red")
    canvas.create_text(x, y, text=node.data)

    # Dibujar las líneas hacia los hijos
    if node.children:
        x_start = x - (x_space * (len(node.children) - 1)) / 2
        x_end = x + (x_space * (len(node.children) - 1)) / 2

        for child in node.children:
            canvas.create_line(x, y + 10, x_start, y + y_space - 10)
            draw_tree(canvas, child, x_start, y + y_space, x_space, y_space)
            x_start += x_space

        canvas.create_line(x, y + 10, x_end, y + y_space - 10)


def init_gui(tree):
    # Crear la ventana
    window = tk.Tk()
    window.title("Árbol Visual")

    # Crear el lienzo para dibujar
    canvas = tk.Canvas(window, width=800, height=600)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Agregar barras de desplazamiento
    x_scrollbar = ttk.Scrollbar(window, orient=tk.HORIZONTAL, command=canvas.xview)
    x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    y_scrollbar = ttk.Scrollbar(window, orient=tk.VERTICAL, command=canvas.yview)
    y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Crear el marco para el contenido del lienzo
    canvas_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=canvas_frame, anchor=tk.NW)

    # Crear el árbol y dibujarlo en el lienzo
    root = tree
    draw_tree(canvas, root, 400, 50, 200, 100)

    def on_key_press(event):
        if event.state == 4:  # Comprueba si se presionó la tecla CONTROL
            if event.keysym == "minus":
                resize_tree(canvas, 0.9)  # Hace el árbol más pequeño
                print('Intentando disminuir tamaño')
            elif event.keysym == "plus":
                resize_tree(canvas, 1.1)  # Hace el árbol más grande
                print('Intentando aumentar tamaño')

    # Asociar la función on_key_press() al evento <KeyPress> del lienzo
    canvas.bind("<KeyPress>", on_key_press)

    # Iniciar el bucle principal de la aplicación
    window.mainloop()


def resize_tree(canvas, factor):
    # Obtiene las dimensiones actuales del canvas
    current_width = canvas.winfo_width()
    current_height = canvas.winfo_height()

    # Calcula las nuevas dimensiones en base al factor de escala
    new_width = int(current_width * factor)
    new_height = int(current_height * factor)

    # Actualiza las dimensiones del canvas
    canvas.config(width=new_width, height=new_height)
    canvas.scale("all", 0, 0, factor, factor)
