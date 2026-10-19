import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps
from pathlib import Path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ImageConverter(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Image Converter")
        self.geometry("850x620")
        self.minsize(700, 550)

        self.source_path = None
        self.source_image = None
        self.preview_image = None

        self.formats = [
            "ICO (Favicon)",
            "JPEG",
            "PNG",
            "WebP",
            "BMP",
            "GIF",
            "TIFF",
        ]

        self.build_ui()

    def build_ui(self):
        # Main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkLabel(
            self,
            text="IMAGE CONVERTER",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        header.grid(row=0, column=0, pady=(25, 5))

        content = ctk.CTkFrame(self, corner_radius=15)
        content.grid(
            row=1, column=0, padx=25, pady=20,
            sticky="nsew"
        )
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        self.file_label = ctk.CTkLabel(
            content,
            text="No image selected",
            font=ctk.CTkFont(size=14),
            wraplength=650,
        )
        self.file_label.grid(row=0, column=0, pady=15)

        # Preview area
        self.preview_label = ctk.CTkLabel(
            content,
            text="Open an image to preview it",
            width=400,
            height=280,
            fg_color=("gray90", "gray17"),
            corner_radius=10,
        )
        self.preview_label.grid(
            row=1, column=0, padx=20, pady=10,
            sticky="nsew"
        )

        controls = ctk.CTkFrame(content, fg_color="transparent")
        controls.grid(row=2, column=0, padx=20, pady=20)

        self.open_button = ctk.CTkButton(
            controls,
            text="Open Image",
            command=self.open_image,
        )
        self.open_button.grid(
            row=0, column=0, padx=8, pady=8
        )

        self.format_menu = ctk.CTkOptionMenu(
            controls,
            values=self.formats,
            command=self.on_format_change,
            width=155,
        )
        self.format_menu.set("PNG")
        self.format_menu.grid(
            row=0, column=1, padx=8, pady=8
        )

        self.convert_button = ctk.CTkButton(
            controls,
            text="Convert & Save",
            command=self.convert_image,
            width=150,
        )
        self.convert_button.grid(
            row=0, column=2, padx=8, pady=8
        )

        self.options_label = ctk.CTkLabel(
            content,
            text="Select a format and open an image.",
            text_color="gray",
        )
        self.options_label.grid(row=3, column=0, pady=(0, 15))

    def open_image(self):
        path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                (
                    "Supported images",
                    "*.png *.jpg *.jpeg *.webp *.bmp "
                    "*.gif *.tif *.tiff *.ico",
                ),
                ("All files", "*.*"),
            ],
        )

        if not path:
            return

        try:
            with Image.open(path) as img:
                # Copy the first frame into memory.
                # Animated formats are not preserved as animations.
                self.source_image = ImageOps.exif_transpose(
                    img
                ).convert("RGBA")

            self.source_path = Path(path)
            self.file_label.configure(
                text=(
                    f"{self.source_path.name} | "
                    f"{self.source_image.width} × "
                    f"{self.source_image.height}"
                )
            )
            self.show_preview()
            self.update_options()

        except Exception as exc:
            messagebox.showerror(
                "Image Error",
                f"Could not open this image:\n{exc}",
            )

    def show_preview(self):
        if self.source_image is None:
            return

        preview = self.source_image.copy()
        preview.thumbnail((500, 300), Image.Resampling.LANCZOS)

        # Keep the CTkImage referenced to prevent it disappearing.
        self.preview_image = ctk.CTkImage(
            light_image=preview,
            dark_image=preview,
            size=preview.size,
        )

        self.preview_label.configure(
            image=self.preview_image,
            text="",
        )

    def on_format_change(self, _choice):
        self.update_options()

    def update_options(self):
        selected = self.format_menu.get()

        if selected == "ICO (Favicon)":
            text = (
                "Favicon mode: generates an ICO with "
                "16, 32, 48, 64, 128 and 256 px sizes."
            )
        elif selected == "JPEG":
            text = (
                "JPEG does not support transparency; "
                "transparent pixels will become white."
            )
        elif selected == "GIF":
            text = (
                "GIF supports a limited palette of 256 colors "
                "per frame. Animation is not preserved."
            )
        else:
            text = f"Output format: {selected}"

        self.options_label.configure(text=text)

    def convert_image(self):
        if self.source_image is None or self.source_path is None:
            messagebox.showwarning(
                "No Image",
                "Open an image before converting.",
            )
            return

        selected = self.format_menu.get()

        extensions = {
            "ICO (Favicon)": ".ico",
            "JPEG": ".jpg",
            "PNG": ".png",
            "WebP": ".webp",
            "BMP": ".bmp",
            "GIF": ".gif",
            "TIFF": ".tiff",
        }

        extension = extensions[selected]

        output_path = filedialog.asksaveasfilename(
            title="Save converted image",
            initialfile=(
                f"{self.source_path.stem}{extension}"
            ),
            defaultextension=extension,
            filetypes=[
                (f"{selected} files", f"*{extension}"),
                ("All files", "*.*"),
            ],
        )

        if not output_path:
            return

        try:
            image = self.source_image.copy()

            if selected == "ICO (Favicon)":
                image.save(
                    output_path,
                    format="ICO",
                    sizes=[
                        (16, 16),
                        (32, 32),
                        (48, 48),
                        (64, 64),
                        (128, 128),
                        (256, 256),
                    ],
                )

            elif selected == "JPEG":
                # Composite transparency onto a white background.
                background = Image.new(
                    "RGB", image.size, (255, 255, 255)
                )
                background.paste(image, mask=image.getchannel("A"))
                background.save(
                    output_path,
                    format="JPEG",
                    quality=95,
                    optimize=True,
                )

            elif selected == "PNG":
                image.save(output_path, format="PNG", optimize=True)

            elif selected == "WebP":
                image.save(
                    output_path,
                    format="WEBP",
                    quality=95,
                )

            elif selected == "BMP":
                image.convert("RGB").save(
                    output_path, format="BMP"
                )

            elif selected == "GIF":
                image.convert("RGB").convert("P", palette=Image.Palette.ADAPTIVE).save(
                    output_path, format="GIF"
                )

            elif selected == "TIFF":
                image.save(output_path, format="TIFF")

            messagebox.showinfo(
                "Conversion Successful",
                f"Image saved successfully:\n{output_path}",
            )

        except Exception as exc:
            messagebox.showerror(
                "Conversion Error",
                f"Could not convert this image:\n{exc}",
            )


if __name__ == "__main__":
    app = ImageConverter()
    app.mainloop()
