from tkinter import Label

import customtkinter
import imutils
from PIL import ImageTk, Image
from screeninfo import get_monitors


def configure_geometry():
    main_monitor = None
    for m in get_monitors():
        if m.is_primary:
            main_monitor = m

    width = int(2.5 * main_monitor.width / 4)
    height = int(2.5 * main_monitor.height / 4)

    return width, height


class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.width, self.height = configure_geometry()

        self.geometry(f"{self.width}x{self.height}")

    def init_tabs(self, images):
        # TODO: Make it receive images as a dictionary containing all the developer images we are trying to display
        if not images:
            label = customtkinter.CTkLabel(self, text="Nothing to see here...")
            label.pack()
        else:
            tabview = customtkinter.CTkTabview(self)
            tabview.pack(padx=5, pady=5)
            for title, image in images.items():
                tabview.add(title)

                current_tab = tabview.tab(title)

                image_ds = imutils.resize(image, height=self.height)

                image_p = Image.fromarray(image_ds)
                image_tk = ImageTk.PhotoImage(image=image_p)

                image_label = Label(current_tab, bg="black", image=image_tk)
                image_label.pack(padx=5, pady=5)

            tabview.set(next(iter(images)))
