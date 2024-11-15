import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from lab2 import *

def start_download():
    """
    Запускає процес завантаження фотографій на основі введених користувачем даних.
    """
    # Отримуємо дані з полів
    earth_date = date_entry.get()
    camera = camera_combobox.get()
    api_key = api_key_entry.get()
    save_directory = save_dir_label.cget("text")
    show_images = show_images_var.get()  # Отримуємо стан галочки для перегляду зображень

    # Перевіряємо дату
    is_valid_date, error_message = validate_date(earth_date)
    if not is_valid_date:
        messagebox.showerror("Invalid Date", error_message)
        return

    # Перевіряємо вибір камери
    if camera not in AVAILABLE_CAMERAS:
        messagebox.showerror("Invalid Camera", "Please select a valid camera from the dropdown list.")
        return

    # Перевіряємо, чи обрано директорію
    if save_directory == "No folder selected":
        messagebox.showerror("No Folder Selected", "Please select a folder to save the photos.")
        return

    # Завантажуємо фотографії
    try:
        download_mars_photos_by_date(earth_date, camera, api_key, show_images, save_directory)
        messagebox.showinfo("Download Complete", f"Photos downloaded successfully to: {save_directory}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


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
    root = tk.Tk()
    root.title("Mars Rover Photo Downloader")

    # Поле для введення дати
    tk.Label(root, text="Enter Earth Date (YYYY-MM-DD):", font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
    global date_entry
    date_entry = tk.Entry(root, font=("Arial", 12))
    date_entry.grid(row=0, column=1, padx=10, pady=5)

    # Випадаючий список для вибору камери
    tk.Label(root, text="Select Camera:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
    global camera_combobox
    camera_combobox = ttk.Combobox(root, values=AVAILABLE_CAMERAS, font=("Arial", 12), state="readonly")
    camera_combobox.grid(row=1, column=1, padx=10, pady=5)
    camera_combobox.set("FHAZ")  # Значення за замовчуванням

    # Поле для введення API ключа
    tk.Label(root, text="NASA API Key:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
    global api_key_entry
    api_key_entry = tk.Entry(root, font=("Arial", 12))
    api_key_entry.grid(row=2, column=1, padx=10, pady=5)
    api_key_entry.insert(0, "DEMO_KEY")  # Значення за замовчуванням

    # Вибір директорії для збереження файлів
    tk.Label(root, text="Save Folder:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
    global save_dir_label
    save_dir_label = tk.Label(root, text="No folder selected", font=("Arial", 12), fg="gray")
    save_dir_label.grid(row=3, column=1, sticky="w", padx=10, pady=5)
    tk.Button(root, text="Browse", command=select_directory, font=("Arial", 10)).grid(row=3, column=2, padx=10, pady=5)

    # Додано Checkbutton для вибору перегляду зображень
    global show_images_var
    show_images_var = tk.BooleanVar()
    show_images_checkbutton = tk.Checkbutton(root, text="Show images after download", variable=show_images_var, font=("Arial", 12))
    show_images_checkbutton.grid(row=4, column=0, columnspan=3, pady=10)

    # Кнопка для запуску завантаження
    tk.Button(root, text="Download Photos", command=start_download, font=("Arial", 14), bg="green", fg="white").grid(row=5, column=0, columnspan=2, pady=20)

    # Кнопка для виходу
    tk.Button(root, text="Exit", command=root.quit, font=("Arial", 14), bg="red", fg="white").grid(row=5, column=2, pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()


