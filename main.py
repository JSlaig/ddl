import tkinter
import tkinter.messagebox
import customtkinter

from screeninfo import get_monitors

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"


# Initial window size based on resolution
def configure_geometry():
    main_monitor = None
    for m in get_monitors():
        if m.is_primary:
            main_monitor = m

    width = int(3 * main_monitor.width / 4)
    height = int(3 * main_monitor.height / 4)

    return width, height


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("DDL")
        # self.wm_iconbitmap('Assets/DDL.ico')  # Setting an icon for the application

        window_width, window_height = configure_geometry()
        self.geometry(f"{str(window_width)}x{str(window_height)}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="DDL",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.load_button = customtkinter.CTkButton(self.sidebar_frame, text="Load", command=self.sidebar_button_event)
        self.load_button.grid(row=1, column=0, padx=20, pady=10)

        self.camera_button = customtkinter.CTkButton(self.sidebar_frame, text="Camera", command=self.sidebar_button_event)
        self.camera_button.grid(row=2, column=0, padx=20, pady=10)

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_option_menu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                                       values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_option_menu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_option_menu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                               values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_option_menu.grid(row=8, column=0, padx=20, pady=(10, 20))



        # TODO: Add in this frame when neccesary
        # Frame for future sliders
        self.slider_frame = customtkinter.CTkFrame(self)
        self.slider_frame.grid(row=1, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")

        # TODO: Modify in order to be able to swap through stages?
        self.stage_buttons = customtkinter.CTkSegmentedButton(self.slider_frame)
        self.stage_buttons.grid(row=0, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")

        # TODO: Add and remove these when necessary
        self.slider_1 = customtkinter.CTkSlider(self.slider_frame, from_=0, to=255, number_of_steps=255)
        self.slider_1.grid(row=3, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")



        # TODO: Bottom bar will be use to print on it the pictures of the process
        # create main entry and button
        self.developer_logs_button = customtkinter.CTkButton(self, text="Developer Logs",
                                                             command=self.open_dev_image_dialog_event)
        self.developer_logs_button.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")

        # TODO: Set dev mode flag on function here
        self.switch = customtkinter.CTkSwitch(master=self, text=f"Developer Mode")
        self.switch.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # set default values
        self.appearance_mode_option_menu.set("Dark")
        self.scaling_option_menu.set("100%")

        # TODO: Config will depend on whether we are on camera or load image version
        self.stage_buttons.configure(values=["Image Adjustment", "Image Crop Preview", "Paragraph Adjustment"])
        self.stage_buttons.set("Image Adjusting")

    # TODO: Make this function show the developer stage pictures
    def open_dev_image_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")


if __name__ == "__main__":
    app = App()
    app.mainloop()
