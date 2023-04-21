import tkinter as tk  # python 3
from tkinter import *

from PIL import Image
from PIL import ImageTk
from PIL import ImageDraw


class ShapeCropper(tk.Frame):
    """Illustrate how to drag items on a Tkinter canvas"""

    def __init__(self, root, parent, width, height, points, img):
        tk.Frame.__init__(self, parent)

        # Image we are setting as a background
        self.image = img

        # Init values for width and height of the canvas
        self.width = width
        self.height = height

        # create a canvas
        pad_x = parent.winfo_width()/3
        self.canvas = tk.Canvas(parent, width=self.width, height=self.height, background="black")
        self.canvas.grid(column=0, row=0, padx=pad_x, pady=5, sticky="EW")

        # Creation of the image in the canvas
        self.canvas.create_image(0, 0, image=self.image, anchor='nw', tags='image')

        # This data is used to keep track of an item being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # Flag for checking if mag glass can appear or not
        self.visible = False

        # Creation of the original points

        # TODO: Change the way these points work once they arent double listed
        self.p1 = points[0][0]
        self.p2 = points[1][0]
        self.p3 = points[2][0]
        self.p4 = points[3][0]

        self.create_tokens(self.p1, self.p2, self.p3, self.p4, "lightblue")
        self.draw_lines(self.p1, self.p2, self.p3, self.p4)

        self.z_img = None
        self.z_cycle = 0
        self.z_img_id = None

        # Event handling for the token drag
        self.canvas.tag_bind("token", "<ButtonPress-1>", self.drag_start)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self.drag_stop)
        self.canvas.tag_bind("token", "<B1-Motion>", self.drag)

        # Event handling for the magnifying glass
        root.bind("<ButtonPress-1>", self.zoomer)
        root.bind("<ButtonRelease-1>", self.unzoomer)
        self.canvas.bind("<Motion>", self.crop)

    def create_tokens(self, p1, p2, p3, p4, color):
        """Create a token at the given coordinate in the given color"""
        self.canvas.create_oval(
            p1[0] - 10,
            p1[1] - 10,
            p1[0] + 10,
            p1[1] + 10,
            outline=color,
            fill=color,
            tags=("token",),
        )
        self.canvas.create_oval(
            p2[0] - 10,
            p2[1] - 10,
            p2[0] + 10,
            p2[1] + 10,
            outline=color,
            fill=color,
            tags=("token",),
        )
        self.canvas.create_oval(
            p3[0] - 10,
            p3[1] - 10,
            p3[0] + 10,
            p3[1] + 10,
            outline=color,
            fill=color,
            tags=("token",),
        )
        self.canvas.create_oval(
            p4[0] - 10,
            p4[1] - 10,
            p4[0] + 10,
            p4[1] + 10,
            outline=color,
            fill=color,
            tags=("token",),
        )

    def draw_lines(self, p1, p2, p3, p4):
        self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="lightblue", width=2, tags="line")
        self.canvas.create_line(p2[0], p2[1], p3[0], p3[1], fill="lightblue", width=2, tags="line")
        self.canvas.create_line(p3[0], p3[1], p4[0], p4[1], fill="lightblue", width=2, tags="line")
        self.canvas.create_line(p4[0], p4[1], p1[0], p1[1], fill="lightblue", width=2, tags="line")
        self.canvas.tag_lower("line")
        self.canvas.tag_lower("image")

    def erase_lines(self):
        self.canvas.delete("line")

    def get_tokens(self):

        tokens = self.canvas.find_withtag("token")

        t1 = self.canvas.coords(tokens[0])
        t2 = self.canvas.coords(tokens[1])
        t3 = self.canvas.coords(tokens[2])
        t4 = self.canvas.coords(tokens[3])

        p1 = [int((t1[0] + t1[2]) / 2), int((t1[1] + t1[3]) / 2)]
        p2 = [int((t2[0] + t2[2]) / 2), int((t2[1] + t2[3]) / 2)]
        p3 = [int((t3[0] + t3[2]) / 2), int((t3[1] + t3[3]) / 2)]
        p4 = [int((t4[0] + t4[2]) / 2), int((t4[1] + t4[3]) / 2)]

        return p1, p2, p3, p4

    def drag_start(self, event):
        """Begining drag of an object"""
        # record the item and its location
        item = self.canvas.find_closest(event.x, event.y)[0]

        cords = self.canvas.coords(item)
        cord_x = (cords[0] + cords[2]) / 2
        cord_y = (cords[1] + cords[3]) / 2

        if item != 1:
            self._drag_data["token"] = item
            self._drag_data["x"] = cord_x
            self._drag_data["y"] = cord_y

            # Flag for magnifying glass visibility
            self.visible = True

    def drag_stop(self, event):
        """End drag of an object"""
        # reset the drag information
        self._drag_data["token"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

        # Flag for magnifying glass visibility
        self.visible = False

    def drag(self, event):
        """Handle dragging of an object"""
        # compute how much the mouse has moved

        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]

        # move the object the appropriate amount taking into account the boundaries of the image
        if event.x < 0 or event.x > self.width:
            delta_x = 0

        if event.y < 0 or event.y > self.height:
            delta_y = 0

        self.canvas.move(self._drag_data["token"], delta_x, delta_y)

        self.erase_lines()
        p1, p2, p3, p4 = self.get_tokens()
        self.draw_lines(p1, p2, p3, p4)

        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def zoomer(self, event):
        if self.visible:
            if self.z_cycle != 4:
                self.z_cycle += 1
            self.crop(event)

    def unzoomer(self, event):
        if self.z_cycle != 0:
            self.z_cycle -= 1
        self.crop(event)

    def crop(self, event):
        if self.z_img_id:
            self.canvas.delete(self.z_img_id)
        if self.z_cycle != 0:

            x, y = self._drag_data["x"], self._drag_data["y"]

            if self.z_cycle == 1:
                # convert PhotoImage to PIL Image
                pil_image = ImageTk.getimage(self.image)

                tmp = pil_image.crop(
                    (x - (self.width / 10), y - (self.height / 10), x + (self.width / 10), y + (self.height / 10)))

                # Draw circular mask
                mask = Image.new("L", tmp.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0) + tmp.size, fill=255)

                # Apply the mask to the cropped image
                tmp.putalpha(mask)

                # Paint vudu crosshair
                draw_ch = ImageDraw.Draw(tmp)

                # Center cross
                draw_ch.line((tmp.width / 2, tmp.height * (6 / 14), tmp.width / 2, tmp.height * (8 / 14)), fill="red")
                draw_ch.line((tmp.width * (6 / 14), tmp.height / 2, tmp.width * (8 / 14), tmp.height / 2), fill="red")

                # Outer crosses
                draw_ch.line((tmp.width / 2, tmp.height * (2 / 10), tmp.width / 2, tmp.height * (3 / 10)), fill="red")
                draw_ch.line((tmp.width * (2 / 10), tmp.height / 2, tmp.width * (3 / 10), tmp.height / 2), fill="red")
                draw_ch.line((tmp.width / 2, tmp.height * (7 / 10), tmp.width / 2, tmp.height * (8 / 10)), fill="red")
                draw_ch.line((tmp.width * (7 / 10), tmp.height / 2, tmp.width * (8 / 10), tmp.height / 2), fill="red")

                # Ring
                center_x, center_y = tmp.width / 2, tmp.height / 2

                # Draw the outer circle
                draw_ch.ellipse((center_x - tmp.width / 5, center_y - tmp.height / 5,
                                 center_x + tmp.width / 5, center_y + tmp.height / 5),
                                outline="red", width=1)

            size = int(self.width / 4), int(self.width / 4)
            self.z_img = ImageTk.PhotoImage(tmp.resize(size))

            if event.x < 25 * (self.width / 100) and event.y < 20 * (
                    self.height / 100):  # Case it gets close upper left corner
                self.z_img_id = self.canvas.create_image(event.x + 10 * (self.width / 100),
                                                         event.y + 10 * (self.height / 100),
                                                         image=self.z_img)  # Move down right
            elif event.x < 25 * (self.width / 100):  # Case it gets close on the left
                self.z_img_id = self.canvas.create_image(event.x + 10 * (self.width / 100),
                                                         event.y - 10 * (self.height / 100),
                                                         image=self.z_img)  # Move only right
            elif event.y < 22 * (self.height / 100):  # Case in gets close up
                self.z_img_id = self.canvas.create_image(event.x - 10 * (self.width / 100),
                                                         event.y + 10 * (self.height / 100),
                                                         image=self.z_img)  # Move only down
            else:  # Normal case or disappear
                self.z_img_id = self.canvas.create_image(event.x - 10 * (self.width / 100),
                                                         event.y - 10 * (self.height / 100), image=self.z_img)
