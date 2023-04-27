import customtkinter
from screeninfo import get_monitors


def configure_geometry():
    main_monitor = None
    for m in get_monitors():
        if m.is_primary:
            main_monitor = m

    width = int(2 * main_monitor.width / 4)
    height = int(2 * main_monitor.height / 4)

    return width, height


class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        width, height = configure_geometry()

        self.geometry(f"{width}x{height}")

    def init_tabs(self, images):
        # TODO: Make it receive images as a dictionary containing all the developer images we are trying to display
        if not images:
            label = customtkinter.CTkLabel(self, text="Nothing to see here...")
            label.pack()
        else:
            tabview = customtkinter.CTkTabview(self)
            tabview.pack(padx=5, pady=5)
            for l, i in images.items():
                tabview.add(l)

            tabview.set(images[0])  # set currently visible tab
