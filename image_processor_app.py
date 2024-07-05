import cv2
import numpy as np
from tkinter import Tk, Label, Button, filedialog, simpledialog, Canvas, StringVar, Entry, Toplevel, messagebox
from PIL import Image, ImageTk


class ImageProcessor:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Processor")
        self.canvas = Canvas(master, cursor="cross")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Motion>", self.motion)
        self.canvas.bind("<Button-1>", self.get_click_coordinates)

        self.load_button = Button(master, text="Load Image", command=self.load_image)
        self.load_button.pack()

        self.capture_button = Button(master, text="Capture from Webcam", command=self.capture_image)
        self.capture_button.pack()

        self.red_channel_button = Button(master, text="Show Red Channel", command=lambda: self.show_channel(2))
        self.red_channel_button.pack()

        self.green_channel_button = Button(master, text="Show Green Channel", command=lambda: self.show_channel(1))
        self.green_channel_button.pack()

        self.blue_channel_button = Button(master, text="Show Blue Channel", command=lambda: self.show_channel(0))
        self.blue_channel_button.pack()

        self.original_button = Button(master, text="Show Original", command=self.show_original)
        self.original_button.pack()

        self.crop_button = Button(master, text="Crop Image", command=self.crop_image)
        self.crop_button.pack()

        self.rotate_button = Button(master, text="Rotate Image", command=self.rotate_image)
        self.rotate_button.pack()

        self.draw_circle_button = Button(master, text="Draw Circle", command=self.show_circle_dialog)
        self.draw_circle_button.pack()

        self.save_button = Button(master, text="Save Image", command=self.save_image)
        self.save_button.pack()

        self.image = None
        self.original_image = None
        self.current_crop_image = None
        self.circle_dialog = None
        self.crop_dialog = None

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = cv2.imread(file_path)
            self.original_image = self.image.copy()
            self.current_crop_image = self.image.copy()
            self.show_image(self.image)

    def capture_image(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open webcam.")
            return
        ret, frame = cap.read()
        cap.release()
        if not ret:
            messagebox.showerror("Error", "Could not read frame.")
            return
        self.image = frame
        self.original_image = self.image.copy()
        self.current_crop_image = self.image.copy()
        self.show_image(self.image)

    def resize_image(self, img, max_size=800):
        h, w, _ = img.shape
        if max(h, w) > max_size:
            scale = max_size / float(max(h, w))
            img = cv2.resize(img, (int(w * scale), int(h * scale)))
        return img

    def show_image(self, img):
        img = self.resize_image(img)
        self.current_img = img
        b, g, r = cv2.split(img)
        img = cv2.merge((r, g, b))
        im = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=im)
        self.canvas.create_image(0, 0, anchor="nw", image=imgtk)
        self.canvas.imgtk = imgtk

        # Update window size to fit the image
        self.master.geometry(f"{img.shape[1]}x{img.shape[0]}")

    def show_channel(self, channel):
        if self.image is not None:
            channels = cv2.split(self.image)
            zeros = np.zeros_like(channels[0])
            if channel == 0:  # Blue
                channel_img = cv2.merge([channels[0], zeros, zeros])
            elif channel == 1:  # Green
                channel_img = cv2.merge([zeros, channels[1], zeros])
            elif channel == 2:  # Red
                channel_img = cv2.merge([zeros, zeros, channels[2]])
            self.show_image(channel_img)

    def show_original(self):
        if self.original_image is not None:
            self.image = self.original_image.copy()
            self.current_crop_image = self.original_image.copy()
            self.show_image(self.image)

    def show_crop_dialog(self):
        self.crop_dialog = Toplevel(self.master)
        self.crop_dialog.title("Enter Crop Coordinates")

        self.x1_var = StringVar()
        self.y1_var = StringVar()
        self.x2_var = StringVar()
        self.y2_var = StringVar()

        Label(self.crop_dialog, text="X1:").grid(row=0, column=0)
        Entry(self.crop_dialog, textvariable=self.x1_var).grid(row=0, column=1)
        Label(self.crop_dialog, text="Y1:").grid(row=1, column=0)
        Entry(self.crop_dialog, textvariable=self.y1_var).grid(row=1, column=1)
        Label(self.crop_dialog, text="X2:").grid(row=2, column=0)
        Entry(self.crop_dialog, textvariable=self.x2_var).grid(row=2, column=1)
        Label(self.crop_dialog, text="Y2:").grid(row=3, column=0)
        Entry(self.crop_dialog, textvariable=self.y2_var).grid(row=3, column=1)
        Button(self.crop_dialog, text="OK", command=self.get_crop_coords).grid(row=4, column=0, columnspan=2)

    def crop_image(self):
        self.show_crop_dialog()

    def get_crop_coords(self):
        try:
            x1 = int(self.x1_var.get())
            y1 = int(self.y1_var.get())
            x2 = int(self.x2_var.get())
            y2 = int(self.y2_var.get())

            # Ensure x1 < x2 and y1 < y2
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1

            self.image = self.current_crop_image[y1:y2, x1:x2]
            self.current_crop_image = self.image.copy()
            self.show_image(self.image)
            self.crop_dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integer coordinates")

    def rotate_image(self):
        if self.image is not None:
            angle = simpledialog.askfloat("Input", "Enter angle:")
            if angle is not None:
                h, w = self.image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                self.image = cv2.warpAffine(self.image, M, (w, h))
                self.current_crop_image = self.image.copy()
                self.show_image(self.image)

    def show_circle_dialog(self):
        self.circle_dialog = Toplevel(self.master)
        self.circle_dialog.title("Enter Circle Coordinates and Radius")

        self.x_var = StringVar()
        self.y_var = StringVar()
        self.radius_var = StringVar()

        Label(self.circle_dialog, text="X:").grid(row=0, column=0)
        self.x_entry = Entry(self.circle_dialog, textvariable=self.x_var)
        self.x_entry.grid(row=0, column=1)
        Label(self.circle_dialog, text="Y:").grid(row=1, column=0)
        self.y_entry = Entry(self.circle_dialog, textvariable=self.y_var)
        self.y_entry.grid(row=1, column=1)
        Label(self.circle_dialog, text="Radius:").grid(row=2, column=0)
        Entry(self.circle_dialog, textvariable=self.radius_var).grid(row=2, column=1)
        Button(self.circle_dialog, text="OK", command=self.draw_circle).grid(row=3, column=0, columnspan=2)

    def draw_circle(self):
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            radius = int(self.radius_var.get())
            if x is not None and y is not None and radius is not None:
                cv2.circle(self.image, (x, y), radius, (0, 0, 255), 2)
                self.current_crop_image = self.image.copy()
                self.show_image(self.image)
                self.circle_dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integer values")

    def motion(self, event):
        if self.image is not None:
            x, y = event.x, event.y
            h, w, _ = self.current_img.shape
            img_h, img_w, _ = self.image.shape
            scale_x = img_w / w
            scale_y = img_h / h
            real_x = int(x * scale_x)
            real_y = int(y * scale_y)
            self.master.title(f"Image Processor - Coordinates: ({real_x}, {real_y})")

            self.canvas.delete("coord")
            self.canvas.create_text(x + 10, y + 10, text=f"({real_x}, {real_y})", anchor="nw", fill="white",
                                    tags="coord")

            if self.circle_dialog:
                focused_widget = self.circle_dialog.focus_get()
                if isinstance(focused_widget, Entry):
                    self.last_focused_widget = focused_widget

    def get_click_coordinates(self, event):
        if self.image is not None and self.circle_dialog:
            x, y = event.x, event.y
            h, w, _ = self.current_img.shape
            img_h, img_w, _ = self.image.shape
            scale_x = img_w / w
            scale_y = img_h / h
            real_x = int(x * scale_x)
            real_y = int(y * scale_y)

            self.x_var.set(real_x)
            self.y_var.set(real_y)

        if self.image is not None and self.crop_dialog:
            x, y = event.x, event.y
            h, w, _ = self.current_img.shape
            img_h, img_w, _ = self.image.shape
            scale_x = img_w / w
            scale_y = img_h / h
            real_x = int(x * scale_x)
            real_y = int(y * scale_y)

            if self.x1_var.get() == "":
                self.x1_var.set(real_x)
                self.y1_var.set(real_y)
            else:
                self.x2_var.set(real_x)
                self.y2_var.set(real_y)

    def save_image(self):
        if self.image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                     filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"),
                                                                ("All files", "*.*")])
            if file_path:
                cv2.imwrite(file_path, self.image)
                messagebox.showinfo("Success", f"Image saved as {file_path}")


if __name__ == "__main__":
    root = Tk()
    processor = ImageProcessor(root)
    root.mainloop()
