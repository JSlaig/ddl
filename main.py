import tkinter
import tkinter.messagebox
import customtkinter

from tkinter import *
from tkinter import filedialog

import cv2
import imutils

from PIL import Image, ImageTk

from Preprocessors import preprocess_image as ipp
from Preprocessors import preprocess_document as ppd

from UI import shape_cropper as sp
from Utils import utlis

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

        # Globals
        self.height_ratio = None
        self.width_ratio = None
        self.img_downscaled = None
        self.points = None
        self.img = None

        # configure window        
        self.title("DDL")
        # self.wm_iconbitmap('Assets/DDL.ico')  # Setting an icon for the application

        window_width, window_height = configure_geometry()
        self.geometry(f"{str(window_width)}x{str(window_height)}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure(1, weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="DDL",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.load_button = customtkinter.CTkButton(self.sidebar_frame, text="Load",
                                                   command=lambda: self.display_image(True))
        self.load_button.grid(row=1, column=0, padx=20, pady=10)

        self.camera_button = customtkinter.CTkButton(self.sidebar_frame, text="Camera",
                                                     command=self.sidebar_button_event)
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

        # Create frame where image will be displayed
        self.display_frame = customtkinter.CTkFrame(self)
        self.display_frame.grid(row=1, column=1, columnspan=2, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # TODO: Add in this frame when neccesary
        # Frame for future sliders
        self.r_sidebar_frame = customtkinter.CTkFrame(self)
        self.r_sidebar_frame.grid(row=1, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.r_sidebar_frame.grid_rowconfigure(0, weight=10)
        self.r_sidebar_frame.grid_rowconfigure(1, weight=1)

        self.param_frame = customtkinter.CTkFrame(self.r_sidebar_frame)
        self.param_frame.grid(row=0, column=0, padx=(20, 20), pady=(10, 10), sticky="new")

        self.next_button_frame = customtkinter.CTkFrame(self.r_sidebar_frame)
        self.next_button_frame.grid(row=1, column=0, padx=(20, 20), pady=(20, 0), sticky="sew")

        # TODO: Modify in order to be able to swap through stages?
        self.stage_buttons = customtkinter.CTkSegmentedButton(self.param_frame)
        self.stage_buttons.grid(row=0, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")

        # TODO: Add and remove these when necessary
        self.slider_1 = customtkinter.CTkSlider(self.param_frame, from_=0, to=255, number_of_steps=255)
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
        self.stage_buttons.set("Image Adjustment")

    def display_image(self, load_from_filesystem):
        if load_from_filesystem:
            self.load_image()

        # Get the original vertices
        # Needs to be changed in order to be outputted as np array
        self.points, default = ipp.detect_document_vertices(self.img)

        preview_height = self.display_frame.winfo_height() - 20

        self.img_downscaled = imutils.resize(self.img, height=preview_height)

        # Translate to tkinter
        img_preview = Image.fromarray(self.img)

        img_downscale_preview = Image.fromarray(self.img_downscaled)
        img_downscale_preview_TK = ImageTk.PhotoImage(image=img_downscale_preview)

        # Calculation of ratio between original and downsized picture
        self.width_ratio = img_preview.width / img_downscale_preview.width
        self.height_ratio = img_preview.height / img_downscale_preview.height

        # Calculate the position of the points in the downscaled image
        points_downscaled = self.downscale_points(self.points)

        # TODO: Might want to alter this to be class oriented as well
        self.clear_frame()

        pad_x = int((self.display_frame.winfo_width()) / 2)
        pad_y = int((self.display_frame.winfo_height()) / 2)

        cropper = sp.ShapeCropper(self, self.display_frame, img_downscale_preview.width, img_downscale_preview.height,
                                  points_downscaled,
                                  img_downscale_preview_TK)
        cropper.grid(column=0, row=0, padx=pad_x, pady=pad_y, sticky="EW")

        btn_next = customtkinter.CTkButton(self.next_button_frame, text="Next",
                                           command=lambda: self.display_warped(cropper.get_tokens(),
                                                                               img_preview.width,
                                                                               img_preview.height))
        btn_next.grid(column=1, row=0, columnspan=3, padx=(10, 10), pady=(10, 10), sticky="NSEW")

    # TODO: Make this function show the developer stage pictures
    def open_dev_image_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    @staticmethod
    def change_appearance_mode_event(new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    @staticmethod
    def change_scaling_event(new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")

    # ///////////////////////////////// AUXILIARY /////////////////////////////////

    # TODO: Must clear the frame with widgets for changing params as well
    def clear_frame(self):
        for child in self.display_frame.winfo_children():
            child.destroy()

        # Missing elements from upper frame in slider one

        for child in self.next_button_frame.winfo_children():
            child.destroy()

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("image", ".jpg"),
                                                     ("image", ".jpeg"),
                                                     ("image", ".png")])

        if len(path) > 0:
            # Read image on opencv
            img_file = cv2.imread(path)

            # Adjust color
            self.img = cv2.cvtColor(img_file, cv2.COLOR_BGR2RGB)

    def downscale_points(self, points):
        # TODO: Once the structure of the array is no longer double-bracketed
        #   change the way they work from points[2][0][1] to points[2][1]

        points[0][0][0] = points[0][0][0] / self.width_ratio
        points[0][0][1] = points[0][0][1] / self.height_ratio

        points[1][0][0] = points[1][0][0] / self.width_ratio
        points[1][0][1] = points[1][0][1] / self.height_ratio

        points[2][0][0] = points[2][0][0] / self.width_ratio
        points[2][0][1] = points[2][0][1] / self.height_ratio

        points[3][0][0] = points[3][0][0] / self.width_ratio
        points[3][0][1] = points[3][0][1] / self.height_ratio

        return points

    def upscale_points(self, points):
        points[0][0] = points[0][0] * self.width_ratio
        points[0][1] = points[0][1] * self.height_ratio

        points[1][0] = points[1][0] * self.width_ratio
        points[1][1] = points[1][1] * self.height_ratio

        points[2][0] = points[2][0] * self.width_ratio
        points[2][1] = points[2][1] * self.height_ratio

        points[3][0] = points[3][0] * self.width_ratio
        points[3][1] = points[3][1] * self.height_ratio

        return points


if __name__ == "__main__":
    app = App()
    app.mainloop()
