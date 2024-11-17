import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
from lab2 import *  # Імпортуємо ваші функції

def start_download():
    """
    Запускає процес завантаження фотографій на основі введених користувачем даних.
    """
    earth_date = date_entry.get()
    camera = camera_combobox.get()
    api_key = api_key_entry.get()
    save_directory = save_dir_label.cget("text")
    show_images = show_images_var.get()  # Перевірка стану галочки "Show Images"

    is_valid_date, error_message = validate_date(earth_date)
    if not is_valid_date:
        messagebox.showerror("Invalid Date", error_message)
        return

    if camera not in AVAILABLE_CAMERAS:
        messagebox.showerror("Invalid Camera", "Please select a valid camera.")
        return

    if save_directory == "No folder selected":
        messagebox.showerror("No Folder Selected", "Please select a folder to save the photos.")
        return

    try:
        photo_paths = download_and_return_photo_paths(earth_date, camera, api_key, save_directory)
        if not photo_paths:
            messagebox.showerror("No Photos Found", f"No photos found for the date {earth_date} and camera {camera}.")
        elif show_images:
            display_photos(photo_paths)  # Показуємо зображення, лише якщо вибрано "Show Images"
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def download_and_return_photo_paths(earth_date, camera, api_key, save_directory):
    """
    Завантажує фотографії та повертає список шляхів до файлів.
    """
    base_url = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos"
    params = {"earth_date": earth_date, "camera": camera, "api_key": api_key}
    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        print(f"Request failed with status code: {response.status_code}. Reason: {response.reason}")
        return []

    photos = response.json().get('photos', [])
    if not photos:
        return []

    rover_name = photos[0]['rover']['name']
    directory_name = f"{earth_date}_{rover_name}_{camera}"
    full_path = os.path.join(save_directory, directory_name)
    create_directory(full_path)

    photo_paths = []
    for photo in photos:
        img_url = photo['img_src']
        img_name = os.path.basename(img_url)
        img_path = os.path.join(full_path, img_name)

        img_data = requests.get(img_url).content
        with open(img_path, 'wb') as img_file:
            img_file.write(img_data)

        photo_paths.append(img_path)

    return photo_paths

def display_photos(photo_paths):
    """
    Відображає завантажені фотографії в межах програми.
    """
    for widget in image_frame.winfo_children():
        widget.destroy()  # Очищуємо попередні зображення

    for photo_path in photo_paths:
        img = Image.open(photo_path)
        img = img.resize((300, 300))  # Змінюємо розмір для відображення
        img_tk = ImageTk.PhotoImage(img)

        label = tk.Label(image_frame, image=img_tk)
        label.image = img_tk  # Зберігаємо посилання, щоб уникнути збору сміття
        label.pack(side="left", padx=10, pady=10)

def select_directory():
    """
    Дозволяє користувачу вибрати директорію для збереження файлів.
    """
    folder = filedialog.askdirectory(title="Select Folder to Save Photos")
    if folder:
        save_dir_label.config(text=folder)

def main():
    """
    Створює графічний інтерфейс для взаємодії з користувачем.
    """
    global date_entry, camera_combobox, api_key_entry, save_dir_label, image_frame, show_images_var

    root = tk.Tk()
    root.title("Mars Rover Photo Downloader")

    tk.Label(root, text="Enter Earth Date (YYYY-MM-DD):", font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
    date_entry = tk.Entry(root, font=("Arial", 12))
    date_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Select Camera:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
    camera_combobox = ttk.Combobox(root, values=AVAILABLE_CAMERAS, font=("Arial", 12), state="readonly")
    camera_combobox.grid(row=1, column=1, padx=10, pady=5)
    camera_combobox.set("FHAZ")

    tk.Label(root, text="NASA API Key:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
    api_key_entry = tk.Entry(root, font=("Arial", 12))
    api_key_entry.grid(row=2, column=1, padx=10, pady=5)
    api_key_entry.insert(0, "DEMO_KEY")

    tk.Label(root, text="Save Folder:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
    save_dir_label = tk.Label(root, text="No folder selected", font=("Arial", 12), fg="gray")
    save_dir_label.grid(row=3, column=1, sticky="w", padx=10, pady=5)
    tk.Button(root, text="Browse", command=select_directory, font=("Arial", 10)).grid(row=3, column=2, padx=10, pady=5)

    # Галочка для вибору "Show Images"
    show_images_var = tk.BooleanVar(value=True)
    show_images_checkbutton = tk.Checkbutton(root, text="Show Images", variable=show_images_var, font=("Arial", 12))
    show_images_checkbutton.grid(row=4, column=0, columnspan=3, pady=10)

    tk.Button(root, text="Download Photos", command=start_download, font=("Arial", 14), bg="green", fg="white").grid(row=5, column=0, columnspan=3, pady=20)

    image_frame = tk.Frame(root)
    image_frame.grid(row=6, column=0, columnspan=3, pady=20)

    tk.Button(root, text="Exit", command=root.quit, font=("Arial", 14), bg="red", fg="white").grid(row=7, column=0, columnspan=3, pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()

