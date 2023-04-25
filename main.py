import math
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
        self.grid_columnconfigure(1, weight=4)
        self.grid_columnconfigure(2, weight=1)
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
        self.display_frame.grid(row=0, column=1, rowspan=2, columnspan=2, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # Frame for thresholds and buttons
        self.r_sidebar_frame = customtkinter.CTkFrame(self)
        self.r_sidebar_frame.grid(row=0, column=3, rowspan=2, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.r_sidebar_frame.grid_rowconfigure(0, weight=1)
        self.r_sidebar_frame.grid_rowconfigure(1, weight=8)
        self.r_sidebar_frame.grid_rowconfigure(2, weight=1)

        self.stage_frame = customtkinter.CTkFrame(self.r_sidebar_frame)
        self.stage_frame.grid(row=0, column=0, rowspan=1, padx=(20, 20), pady=(10, 10), sticky="new")

        self.slider_frame = customtkinter.CTkFrame(self.r_sidebar_frame, height=350)
        self.slider_frame.grid(row=1, column=0, rowspan=1, padx=(20, 20), pady=(10, 10), sticky="ew")

        self.next_button_frame = customtkinter.CTkFrame(self.r_sidebar_frame, height=48)
        self.next_button_frame.grid(row=2, column=0, rowspan=1, padx=(20, 20), pady=(10, 10), sticky="sew")

        self.stage_buttons = customtkinter.CTkSegmentedButton(self.stage_frame)
        self.stage_buttons.grid(row=0, column=0, padx=40, pady=(10, 10), sticky="nsew")

        # TODO: Add and remove these when necessary
        # Preset will be needed with some labels in the case of the webcam and in paragraph detection
        # self.slider_1 = customtkinter.CTkSlider(self.slider_frame, from_=0, to=255, number_of_steps=255)
        # self.slider_1.grid(row=3, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")

        # TODO: Bottom bar will be use to print on it the pictures of the process
        # create main entry and button
        self.developer_logs_button = customtkinter.CTkButton(self, text="Developer Logs",
                                                             command=self.show_dev)
        self.developer_logs_button.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")

        # TODO: Set dev mode flag on function here
        self.switch = customtkinter.CTkSwitch(master=self, text=f"Developer Mode")
        self.switch.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # set default values
        self.appearance_mode_option_menu.set("Dark")
        self.scaling_option_menu.set("100%")

        # TODO: Config will depend on whether we are on camera or load image version
        self.stage_buttons.configure(values=["Crop", "Warp", "Paragraph"], state=DISABLED)

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

        btn_next = customtkinter.CTkButton(self.next_button_frame, width=self.next_button_frame.winfo_width() - 20,
                                           text="Next",
                                           command=lambda: self.display_warped(cropper.get_tokens(),
                                                                               img_preview.width,
                                                                               img_preview.height))
        btn_next.grid(column=1, row=0, columnspan=3, padx=(10, 10), pady=(10, 10), sticky="NSEW")

        self.stage_buttons.set("Crop")

    def display_warped(self, tokens, img_width, img_height):
        # Get cropped coordinates
        new_downscaled_points = tokens

        self.points = self.upscale_points(new_downscaled_points)

        # TODO: change this to be a new class that displays the warped image
        # Remove elements then put new in
        self.clear_frame()

        # This is the warped image over which we will operate
        warped_image = ipp.img_warp(self.points, self.img, img_width, img_height)

        aspect_ratio = 1 / math.sqrt(2)

        a4_height = Image.fromarray(warped_image).height
        a4_width = int(a4_height * aspect_ratio)

        # This is the image over which we need to do stuff later
        warped_image = cv2.resize(warped_image, (a4_width, a4_height))

        image_height = self.display_frame.winfo_height() - 20

        warped_downscaled = imutils.resize(warped_image, height=image_height)

        warped_preview = Image.fromarray(warped_downscaled)
        warped_preview_TK = ImageTk.PhotoImage(image=warped_preview)

        warp_label = Label(self.display_frame, image=warped_preview_TK)

        pad_x = int((self.display_frame.winfo_width()) / 2)
        pad_y = int((self.display_frame.winfo_height()) / 2)

        warp_label.grid(column=0, row=0, padx=pad_x, pady=pad_y)

        btn_next = customtkinter.CTkButton(self.next_button_frame, width=self.next_button_frame.winfo_width() - 20, text="next",
                                           command=lambda: self.display_paragraph_segmented(warped_image))

        btn_next.grid(column=1, row=0, columnspan=3, padx=(10, 10), pady=(10, 10), sticky="NSEW")

        self.stage_buttons.set("Warp")

        # Everytime That an image load is needed
        self.stage_frame.mainloop()

    # TODO: Make this function show the developer stage pictures
    def show_dev(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def sidebar_button_event(self):
        print("sidebar_button click")

    # ///////////////////////////////// AUXILIARY /////////////////////////////////
    def clear_frame(self):
        for child in self.display_frame.winfo_children():
            child.destroy()

        for child in self.slider_frame.winfo_children():
            child.destroy()

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

    @staticmethod
    def change_appearance_mode_event(new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    @staticmethod
    def change_scaling_event(new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)


if __name__ == "__main__":
    app = App()
    app.mainloop()
