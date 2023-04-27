import customtkinter


class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry(f"{self.winfo_width()/2}x{self.winfo_height()/2}")

        tabview = customtkinter.CTkTabview(self)
        tabview.pack(padx=5, pady=5)

        # TODO: Make it receive images as a dictionary containing all the developer images we are trying to display
        if not images:
            label = customtkinter.CTkLabel(self, text="Nothing to see here...")
            label.pack()
        else:
            for l, i in images.items():
                tabview.add(l)

            tabview.set(images[0])  # set currently visible tab

