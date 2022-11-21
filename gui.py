import tkinter as tk    # python 3
from tkinter import *
from tkinter import filedialog
from screeninfo import get_monitors


root = Tk()  # Assignation of root window
root.title('DocClone')  # Assignation of the window title

# Getting main monitor resolution
main_monitor = None
for m in get_monitors():
    if m.is_primary:
        main_monitor = m

global windowWidth
windowWidth = int(main_monitor.width / 2)
global windowHeight
windowHeight = int(main_monitor.height / 2)

root.geometry(str(windowWidth) + "x" + str(windowHeight))  # Setting the window size based on the resolution


class Gui(tk.Frame):
    """Illustrate how to drag items on a Tkinter canvas"""

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # create a canvas
        self.canvas = tk.Canvas(width=400, height=400, background="bisque")
        self.canvas.pack(fill="both", expand=True)

        # this data is used to keep track of an
        # item being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # create a couple of movable objects
        self.create_token(100, 100, "green")
        self.create_token(200, 100, "green")
        self.create_token(100, 200, "green")
        self.create_token(200, 200, "green")

        # add bindings for clicking, dragging and releasing over
        # any object with the "token" tag
        self.canvas.tag_bind("token", "<ButtonPress-1>", self.drag_start)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self.drag_stop)
        self.canvas.tag_bind("token", "<B1-Motion>", self.drag)

    def create_token(self, x, y, color):
        """Create a token at the given coordinate in the given color"""
        self.canvas.create_oval(
            x - 10,
            y - 10,
            x + 10,
            y + 10,
            outline=color,
            fill=color,
            tags=("token",),
        )

    def drag_start(self, event):
        """Begining drag of an object"""
        # record the item and its location
        self._drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def drag_stop(self, event):
        """End drag of an object"""
        # reset the drag information
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def drag(self, event):
        """Handle dragging of an object"""
        # compute how much the mouse has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        # move the object the appropriate amount
        self.canvas.move(self._drag_data["item"], delta_x, delta_y)
        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y


root = tk.Tk()
Gui(root).pack(fill="both", expand=True)
root.mainloop()