import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np
import time

def resize_image(input_path, output_path, width=None, height=None, quality=80):
    with Image.open(input_path) as image:
        if not width and not height:
            width, height = image.size
        elif not height:
            height = int(image.height * (width / image.width))
        elif not width:
            width = int(image.width * (width / image.height))
        
        resized_image = image.resize((width, height))
        resized_image.save(output_path, optimize=True, quality=quality)
        return resized_image

def is_transparent(image_path):
    try:
        image = Image.open(image_path)
        if 'A' in image.getbands():
            return True  # Image has transparency
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def remove_background(input_path, output_path):
    image = cv2.imread(input_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    result = np.zeros_like(image, dtype=np.uint8)
    result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
    result[..., 3] = mask_inv
    result[:, :, :3] = image
    cv2.imwrite(output_path, result)
    return result
def process_images():
    input_path = input_directory_entry.get()
    output_directory = output_directory_entry.get()
    if not input_path or not output_directory:
        return
    
    width = int(width_entry.get())
    height = int(height_entry.get())

    if os.path.isfile(input_path):
        if input_path.endswith(".png") or input_path.endswith(".jpg") or input_path.endswith(".jpeg"):
            output_path = os.path.join(output_directory, os.path.basename(input_path))
            resize_image(input_path, output_path, width, height)
            processing_status_label.config(text=f"Resized: {os.path.basename(input_path)}")
            if not is_transparent(output_path):
                remove_background(output_path, output_path)
                processing_status_label.config(text=f"Processed: {os.path.basename(input_path)}")
            else:
                processing_status_label.config(text="Image already has transparency")
        else:
            processing_status_label.config(text="Invalid file type")
    elif os.path.isdir(input_path):
        processing_status_label.config(text="Processing directory...")
        start_time = time.time()
        for filename in os.listdir(input_path):
            if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg"):
                input_file_path = os.path.join(input_path, filename)
                output_file_path = os.path.join(output_directory, filename)
                
                resize_image(input_file_path, output_file_path, width, height)
                processing_status_label.config(text=f"Resized: {filename}")
                
                if not is_transparent(output_file_path):
                    remove_background(output_file_path, output_file_path)
                    processing_status_label.config(text=f"Processed: {filename}")
                else:
                    processing_status_label.config(text=f"Skipped (Transparent): {filename}")
        end_time = time.time()
        processing_status_label.config(text=f"Processing complete. Time taken: {end_time - start_time:.2f} seconds")
        
        
        input_directory_entry.delete(0, tk.END)
        output_directory_entry.delete(0, tk.END)
        width_entry.delete(0, tk.END)
        height_entry.delete(0, tk.END)
    else:
        processing_status_label.config(text="Invalid input path")


def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        input_directory_entry.delete(0, tk.END)
        input_directory_entry.insert(0, file_path)

def select_directory():
    directory_path = filedialog.askdirectory()
    if directory_path:
        input_directory_entry.delete(0, tk.END)
        input_directory_entry.insert(0, directory_path)


root = tk.Tk()
root.title("Image Resizer and Background Remover")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

input_directory_label = tk.Label(frame, text="Input File/Directory:")
input_directory_label.grid(row=0, column=0, padx=5, pady=5)

input_directory_entry = tk.Entry(frame)
input_directory_entry.grid(row=0, column=1, padx=5, pady=5)

file_button = tk.Button(frame, text="Select File", command=select_file)
file_button.grid(row=0, column=2, padx=5, pady=5)

directory_button = tk.Button(frame, text="Select Directory", command=select_directory)
directory_button.grid(row=0, column=3, padx=5, pady=5)

output_directory_label = tk.Label(frame, text="Output Directory:")
output_directory_label.grid(row=1, column=0, padx=5, pady=5)

output_directory_entry = tk.Entry(frame)
output_directory_entry.grid(row=1, column=1, padx=5, pady=5)

output_directory_button = tk.Button(frame, text="Select", command=lambda: output_directory_entry.insert(tk.END, filedialog.askdirectory()))
output_directory_button.grid(row=1, column=2, padx=5, pady=5)

width_label = tk.Label(frame, text="Width:")
width_label.grid(row=2, column=0, padx=5, pady=5)

width_entry = tk.Entry(frame)
width_entry.grid(row=2, column=1, padx=5, pady=5)
width_entry.insert(0,"499")

height_label = tk.Label(frame, text="Height:")
height_label.grid(row=3, column=0, padx=5, pady=5)

height_entry = tk.Entry(frame)
height_entry.grid(row=3, column=1, padx=5, pady=5)
height_entry.insert(0,"499")

process_button = tk.Button(frame, text="Process Images", command=process_images)
process_button.grid(row=4, columnspan=4, padx=5, pady=5)

processing_status_label = tk.Label(root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
processing_status_label.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()
