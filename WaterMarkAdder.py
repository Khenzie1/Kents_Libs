import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import os # Imported for os.path.basename in case needed for cleaner names, though not strictly used in current file handling

class ImageWatermarkerApp:
    def __init__(self, root):
        # Initialize the main Tkinter window
        self.root = root
        self.root.title("Batch Image Watermarker")
        self.root.geometry("800x700") # Set a default window size
        self.root.minsize(700, 600) # Set minimum size

        # Variables to store selected paths and settings
        self.image_paths = []
        self.logo_path = None
        self.output_dir = None
        self.logo_scale = tk.DoubleVar(value=0.2) # Default logo scale (20% of original logo size)
        self.pos_x = tk.IntVar(value=20) # Default X position (with padding)
        self.pos_y = tk.IntVar(value=20) # Default Y position (with padding)
        self.position_var = tk.StringVar(value="Top Left") # Default position
        self.padding = 20 # Padding from edges for predefined positions

        # --- Setup UI Layout ---
        # Use a main frame for padding
        main_frame = ttk.Frame(root, padding="10 10 10 10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Configure columns for responsiveness
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1) # Make image listbox expand

        # --- Input Section ---
        input_frame = ttk.LabelFrame(main_frame, text="Input Files", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        input_frame.columnconfigure(0, weight=1) # Make buttons span

        # Select Images Button
        ttk.Button(input_frame, text="Select Images (JPG/PNG)", command=self.select_images).grid(row=0, column=0, sticky="ew", pady=2)
        # Select Logo Button
        ttk.Button(input_frame, text="Select Logo (PNG Recommended)", command=self.select_logo).grid(row=1, column=0, sticky="ew", pady=2)
        # Output Directory Button
        ttk.Button(input_frame, text="Select Output Directory", command=self.select_output_dir).grid(row=2, column=0, sticky="ew", pady=2)

        # --- Settings Section ---
        settings_frame = ttk.LabelFrame(main_frame, text="Logo Settings", padding="10")
        settings_frame.grid(row=1, column=0, sticky="nsew", pady=5, padx=5)
        settings_frame.columnconfigure(1, weight=1) # Allow controls to expand

        # Logo Size Slider
        ttk.Label(settings_frame, text="Logo Scale (0.01-1.0):").grid(row=0, column=0, sticky="w", pady=2)
        self.scale_slider = ttk.Scale(settings_frame, from_=0.01, to=1.0, orient="horizontal",
                                     variable=self.logo_scale, command=self.update_preview_from_slider)
        self.scale_slider.grid(row=0, column=1, sticky="ew", pady=2)
        self.scale_label = ttk.Label(settings_frame, textvariable=self.logo_scale)
        self.scale_label.grid(row=0, column=2, sticky="w", padx=5)

        # Position Selection Dropdown
        ttk.Label(settings_frame, text="Position:").grid(row=1, column=0, sticky="w", pady=2)
        self.position_options = ["Top Left", "Top Right", "Bottom Left", "Bottom Right", "Center", "Custom"]
        self.position_dropdown = ttk.Combobox(settings_frame, textvariable=self.position_var,
                                              values=self.position_options, state="readonly")
        self.position_dropdown.grid(row=1, column=1, columnspan=2, sticky="ew", pady=2)
        self.position_dropdown.bind("<<ComboboxSelected>>", self._update_position_fields_and_preview)

        # Position X
        ttk.Label(settings_frame, text="Position X:").grid(row=2, column=0, sticky="w", pady=2)
        self.pos_x_entry = ttk.Entry(settings_frame, textvariable=self.pos_x, width=8)
        self.pos_x_entry.grid(row=2, column=1, sticky="w", pady=2, padx=(0,5))
        self.pos_x_entry.bind("<KeyRelease>", self.update_preview_from_entry)

        # Position Y
        ttk.Label(settings_frame, text="Position Y:").grid(row=3, column=0, sticky="w", pady=2)
        self.pos_y_entry = ttk.Entry(settings_frame, textvariable=self.pos_y, width=8)
        self.pos_y_entry.grid(row=3, column=1, sticky="w", pady=2, padx=(0,5))
        self.pos_y_entry.bind("<KeyRelease>", self.update_preview_from_entry)

        # --- Selected Images Display ---
        images_display_frame = ttk.LabelFrame(main_frame, text="Selected Images", padding="10")
        images_display_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=5)
        images_display_frame.rowconfigure(0, weight=1)
        images_display_frame.columnconfigure(0, weight=1)

        self.image_listbox = tk.Listbox(images_display_frame, height=5, selectmode=tk.EXTENDED) # Changed to EXTENDED for multi-select
        self.image_listbox.grid(row=0, column=0, sticky="nsew")
        self.image_listbox.bind("<<ListboxSelect>>", self.display_preview) # Bind for preview on selection

        # Scrollbar for listbox
        list_scrollbar = ttk.Scrollbar(images_display_frame, orient="vertical", command=self.image_listbox.yview)
        list_scrollbar.grid(row=0, column=1, sticky="ns")
        self.image_listbox.config(yscrollcommand=list_scrollbar.set)

        # New: Remove Selected Images Button
        ttk.Button(images_display_frame, text="Remove Selected Image(s)", command=self.remove_selected_images).grid(row=1, column=0, sticky="ew", pady=5)

        # --- Preview Section ---
        preview_frame = ttk.LabelFrame(main_frame, text="Preview (First Selected Image)", padding="10")
        preview_frame.grid(row=1, column=1, sticky="nsew", pady=5, padx=5)
        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)

        # Canvas for image preview
        self.canvas = tk.Canvas(preview_frame, bg="lightgray", bd=2, relief="groove")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Button-1>", self.on_canvas_click) # To drag and set position
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        # --- Action Button ---
        ttk.Button(main_frame, text="Add Watermark to All Images", command=self.add_watermark, style="Accent.TButton").grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)

        # --- Status Bar ---
        self.status_label = ttk.Label(root, text="Ready", relief=tk.SUNKEN, anchor="w")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Apply a modern theme
        style = ttk.Style()
        style.theme_use("clam") # Or "alt", "default", "vista", "xpnative" (Windows)
        style.configure("Accent.TButton", font=("Arial", 12, "bold"), background="#4CAF50", foreground="white")
        style.map("Accent.TButton", background=[("active", "#45a049")])

        # Initial update of position fields based on default selection
        self._update_position_fields_and_preview()

    def select_images(self):
        # Open file dialog to select multiple images
        paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        if paths:
            # Add only new paths, avoid duplicates
            new_paths = [p for p in paths if p not in self.image_paths]
            self.image_paths.extend(new_paths)
            # Re-populate listbox to ensure consistency and unique entries
            self.image_listbox.delete(0, tk.END)
            for p in self.image_paths:
                self.image_listbox.insert(tk.END, p)
            self.status_label.config(text=f"Selected {len(self.image_paths)} images.")
            self.display_preview() # Display preview of the first selected image

    def remove_selected_images(self):
        selected_indices = self.image_listbox.curselection() # Get indices of selected items
        if not selected_indices:
            messagebox.showinfo("No Selection", "Please select image(s) to remove.")
            return

        # Convert tuple of indices to a list and sort in reverse order
        # This is crucial to avoid issues when deleting items from the listbox
        # (deleting from the end first prevents indices from shifting)
        indices_to_remove = sorted(list(selected_indices), reverse=True)

        for index in indices_to_remove:
            # Remove from internal list first
            if index < len(self.image_paths): # Safety check
                del self.image_paths[index]
            # Then remove from the listbox display
            self.image_listbox.delete(index)

        self.status_label.config(text=f"Removed {len(selected_indices)} image(s). {len(self.image_paths)} images remaining.")
        self.display_preview() # Update preview after removal

    def select_logo(self):
        # Open file dialog to select logo image
        path = filedialog.askopenfilename(
            title="Select Logo Image",
            filetypes=[("PNG files", "*.png"), ("Image files", "*.jpg *.jpeg *.gif"), ("All files", "*.*")]
        )
        if path:
            self.logo_path = path
            self.status_label.config(text=f"Selected logo: {os.path.basename(path)}")
            self.display_preview() # Update preview with new logo

    def select_output_dir(self):
        # Open directory dialog to select output folder
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir = directory
            self.status_label.config(text=f"Output directory: {directory}")

    def update_preview_from_slider(self, value):
        # Update scale label and redraw preview when slider moves
        self.logo_scale.set(float(value))
        self.display_preview()

    def update_preview_from_entry(self, event=None):
        # Update preview when X/Y entry changes (only if position is Custom)
        if self.position_var.get() == "Custom":
            try:
                # Attempt to get values, but don't error out on incomplete input
                _ = int(self.pos_x_entry.get())
                _ = int(self.pos_y_entry.get())
                self.display_preview()
            except ValueError:
                pass # Ignore invalid input while typing, will be caught during actual processing

    def _update_position_fields_and_preview(self, event=None):
        # Enable/disable X/Y entry fields based on position selection
        if self.position_var.get() == "Custom":
            self.pos_x_entry.config(state="normal")
            self.pos_y_entry.config(state="normal")
        else:
            self.pos_x_entry.config(state="readonly")
            self.pos_y_entry.config(state="readonly")
        self.display_preview() # Always update preview after position change

    def calculate_logo_position(self, image_width, image_height, logo_width, logo_height):
        """
        Calculates the top-left (x, y) coordinates for the logo based on selected position.
        Args:
            image_width, image_height: Dimensions of the base image.
            logo_width, logo_height: Dimensions of the logo.
        Returns:
            (x, y) tuple for logo placement.
        """
        position_choice = self.position_var.get()
        x, y = 0, 0 # Default (will be overwritten)

        # Ensure logo doesn't go off-screen if it's too large for the padding
        effective_padding_x = min(self.padding, max(0, (image_width - logo_width) // 2))
        effective_padding_y = min(self.padding, max(0, (image_height - logo_height) // 2))

        if position_choice == "Top Left":
            x = effective_padding_x
            y = effective_padding_y
        elif position_choice == "Top Right":
            x = image_width - logo_width - effective_padding_x
            y = effective_padding_y
        elif position_choice == "Bottom Left":
            x = effective_padding_x
            y = image_height - logo_height - effective_padding_y
        elif position_choice == "Bottom Right":
            x = image_width - logo_width - effective_padding_x
            y = image_height - logo_height - effective_padding_y
        elif position_choice == "Center":
            x = (image_width - logo_width) // 2
            y = (image_height - logo_height) // 2
        elif position_choice == "Custom":
            try:
                x = self.pos_x.get()
                y = self.pos_y.get()
            except tk.TclError: # Handle cases where entry might be empty or invalid
                x, y = 0, 0 # Fallback
                self.status_label.config(text="Invalid X/Y custom input. Defaulting to (0,0).")
                self.pos_x.set(0)
                self.pos_y.set(0)


        # Clamp coordinates to ensure logo stays within bounds (important for custom or tiny images/large logos)
        x = max(0, min(x, image_width - logo_width))
        y = max(0, min(y, image_height - logo_height))

        # Update the entry fields if not in custom mode to show calculated values
        if position_choice != "Custom":
            self.pos_x.set(x)
            self.pos_y.set(y)

        return x, y


    def display_preview(self, event=None):
        # Clear canvas
        self.canvas.delete("all")
        self.canvas_image_tk = None # Clear previous Tkinter PhotoImage reference

        if not self.image_paths:
            self.status_label.config(text="No images selected for preview.")
            # Display a message on the canvas when no images are selected
            self.canvas.create_text(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2,
                                     text="No images selected for preview.", fill="gray", font=("Arial", 10))
            return
        if not self.logo_path:
            self.status_label.config(text="No logo selected for preview.")
            # Display a message specific to missing logo
            self.canvas.create_text(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2,
                                     text="Please select a logo to enable preview.", fill="gray", font=("Arial", 10))
            return

        # Get the currently selected image in the listbox, or the first one if none selected
        selected_indices = self.image_listbox.curselection()
        if selected_indices:
            preview_image_path = self.image_paths[selected_indices[0]]
        else:
            preview_image_path = self.image_paths[0] # Default to the first image if none are selected

        try:
            original_image_for_preview = Image.open(preview_image_path).convert("RGBA")
            logo_image = Image.open(self.logo_path).convert("RGBA")

            # Get actual canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Fallback for initial draw before canvas has concrete dimensions
            if canvas_width < 100 or canvas_height < 100: # Arbitrary small value
                canvas_width = 400
                canvas_height = 350


            # Calculate aspect ratio to fit image within canvas
            img_width_orig, img_height_orig = original_image_for_preview.size
            ratio = min(canvas_width / img_width_orig, canvas_height / img_height_orig)
            new_width = int(img_width_orig * ratio)
            new_height = int(img_height_orig * ratio)

            preview_image_scaled = original_image_for_preview.resize((new_width, new_height), Image.LANCZOS)

            # Calculate logo size based on scale slider value for the original logo
            logo_width_orig, logo_height_orig = logo_image.size
            scaled_logo_width_orig_res = int(logo_width_orig * self.logo_scale.get())
            scaled_logo_height_orig_res = int(logo_height_orig * self.logo_scale.get())

            if scaled_logo_width_orig_res == 0: scaled_logo_width_orig_res = 1 # Prevent zero dimensions
            if scaled_logo_height_orig_res == 0: scaled_logo_height_orig_res = 1

            # Get the logo position based on original image dimensions
            logo_x_orig_res, logo_y_orig_res = self.calculate_logo_position(
                img_width_orig, img_height_orig, scaled_logo_width_orig_res, scaled_logo_height_orig_res
            )

            # Resize the logo for the preview (applying the overall scaling ratio)
            resized_logo_for_preview = logo_image.resize(
                (int(scaled_logo_width_orig_res * ratio), int(scaled_logo_height_orig_res * ratio)),
                Image.LANCZOS
            )

            # Adjust logo position for the preview (scaled image)
            preview_logo_x = int(logo_x_orig_res * ratio)
            preview_logo_y = int(logo_y_orig_res * ratio)

            # Create a transparent layer for the logo if it's placed outside bounds
            # This handles pasting with alpha channel
            temp_img = Image.new('RGBA', preview_image_scaled.size, (0, 0, 0, 0))
            temp_img.paste(resized_logo_for_preview, (preview_logo_x, preview_logo_y), resized_logo_for_preview)
            composite = Image.alpha_composite(preview_image_scaled, temp_img)

            # Convert to Tkinter PhotoImage
            self.canvas_image_tk = ImageTk.PhotoImage(composite)

            # Calculate position to center the image on the canvas
            x_center = (canvas_width - new_width) / 2
            y_center = (canvas_height - new_height) / 2

            self.canvas.create_image(x_center, y_center, anchor="nw", image=self.canvas_image_tk)

            # Store image scaling info for dragging
            self.canvas.image_x_offset = x_center # Canvas offset of the image
            self.canvas.image_y_offset = y_center
            self.canvas.image_width = new_width # Displayed image width on canvas
            self.canvas.image_height = new_height
            self.canvas.original_image_ratio = ratio # Ratio of original image to displayed preview
            self.canvas.logo_original_dimensions = (scaled_logo_width_orig_res, scaled_logo_height_orig_res) # Logo size at original resolution
            self.canvas.current_logo_pos_on_original = (logo_x_orig_res, logo_y_orig_res) # Current logo pos (original image coords)

        except Exception as e:
            self.status_label.config(text=f"Preview error: {e}")
            self.canvas.create_text(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2,
                                     text=f"Error displaying preview:\n{e}", fill="red")

    def on_canvas_click(self, event):
        # Only allow dragging if position is Custom
        if self.position_var.get() == "Custom":
            self.canvas.last_x = event.x
            self.canvas.last_y = event.y

    def on_canvas_drag(self, event):
        # Only allow dragging if position is Custom and drag has started
        if self.position_var.get() != "Custom" or not hasattr(self.canvas, 'last_x'):
            return

        dx = event.x - self.canvas.last_x
        dy = event.y - self.canvas.last_y
        self.canvas.last_x = event.x
        self.canvas.last_y = event.y

        # Get current logo position relative to original image dimensions
        current_logo_x_orig, current_logo_y_orig = self.canvas.current_logo_pos_on_original

        # Convert drag delta (canvas pixels) back to original image resolution pixels
        original_dx = int(dx / self.canvas.original_image_ratio)
        original_dy = int(dy / self.canvas.original_image_ratio)

        new_logo_x_orig = current_logo_x_orig + original_dx
        new_logo_y_orig = current_logo_y_orig + original_dy

        # Clamp new position to stay within original image bounds
        img_width_orig, img_height_orig = (self.canvas.image_width / self.canvas.original_image_ratio,
                                           self.canvas.image_height / self.canvas.original_image_ratio)
        logo_width_orig, logo_height_orig = self.canvas.logo_original_dimensions

        new_logo_x_orig = max(0, min(new_logo_x_orig, int(img_width_orig - logo_width_orig)))
        new_logo_y_orig = max(0, min(new_logo_y_orig, int(img_height_orig - logo_height_orig)))


        # Update the Tkinter IntVars
        self.pos_x.set(new_logo_x_orig)
        self.pos_y.set(new_logo_y_orig)

        # Update the stored current position
        self.canvas.current_logo_pos_on_original = (new_logo_x_orig, new_logo_y_orig)

        # Redraw preview
        self.display_preview()

    def on_canvas_release(self, event):
        if hasattr(self.canvas, 'last_x'):
            delattr(self.canvas, 'last_x')
            delattr(self.canvas, 'last_y')


    def add_watermark(self):
        if not self.image_paths:
            messagebox.showerror("Error", "Please select images first.")
            return
        if not self.logo_path:
            messagebox.showerror("Error", "Please select a logo first.")
            return
        if not self.output_dir:
            messagebox.showerror("Error", "Please select an output directory first.")
            return

        try:
            logo_img = Image.open(self.logo_path).convert("RGBA")
            original_logo_width, original_logo_height = logo_img.size

            # Get settings from UI
            scale = self.logo_scale.get()

            # Calculate actual logo size based on scale
            scaled_logo_width = int(original_logo_width * scale)
            scaled_logo_height = int(original_logo_height * scale)

            if scaled_logo_width == 0: scaled_logo_width = 1 # Prevent zero dimensions
            if scaled_logo_height == 0: scaled_logo_height = 1

            resized_logo = logo_img.resize((scaled_logo_width, scaled_logo_height), Image.LANCZOS)

            total_images = len(self.image_paths)
            processed_count = 0

            self.status_label.config(text="Processing images...")
            self.root.update_idletasks() # Update GUI to show message

            for i, image_path in enumerate(self.image_paths):
                try:
                    base_image = Image.open(image_path).convert("RGBA")
                    img_width_actual, img_height_actual = base_image.size

                    # Calculate logo position for the actual image
                    logo_x_actual, logo_y_actual = self.calculate_logo_position(
                        img_width_actual, img_height_actual, scaled_logo_width, scaled_logo_height
                    )

                    # Create a transparent layer the size of the base image
                    temp_img = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
                    temp_img.paste(resized_logo, (logo_x_actual, logo_y_actual), resized_logo)

                    # Composite the base image and the logo layer
                    watermarked_image = Image.alpha_composite(base_image, temp_img)

                    # Save the watermarked image
                    file_name = os.path.basename(image_path) # Using os.path.basename for cleaner file names
                    output_path = os.path.join(self.output_dir, f"watermarked_{file_name}")
                    # Convert back to RGB for saving if original was JPG, to avoid transparency issues
                    if watermarked_image.mode != 'RGB':
                        watermarked_image = watermarked_image.convert('RGB')
                    watermarked_image.save(output_path)
                    processed_count += 1
                    self.status_label.config(text=f"Processing... {processed_count}/{total_images} images processed.")
                    self.root.update_idletasks() # Update GUI
                except Exception as e:
                    self.status_label.config(text=f"Error processing {image_path}: {e}")
                    messagebox.showwarning("Processing Error", f"Could not process {image_path}:\n{e}")
                    self.root.update_idletasks() # Update GUI

            self.status_label.config(text=f"Batch watermarking complete! Processed {processed_count} images.")
            messagebox.showinfo("Success", f"Successfully watermarked {processed_count} images and saved to {self.output_dir}")

        except Exception as e:
            self.status_label.config(text=f"An unexpected error occurred: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred during watermarking: {e}")

# Entry point of the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageWatermarkerApp(root)

    # Call display_preview after the window has been rendered to get correct canvas dimensions
    root.update_idletasks()
    app.display_preview() # Initial display call after GUI is laid out

    root.mainloop()
