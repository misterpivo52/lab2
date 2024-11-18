import os
import argparse
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime

# Список доступних камер для запитів до NASA API
AVAILABLE_CAMERAS = [
    "FHAZ",  # Front Hazard Avoidance Camera
    "RHAZ",  # Rear Hazard Avoidance Camera
    "MAST",  # Mast Camera
    "CHEMCAM",  # Chemistry and Camera Complex
    "MAHLI",  # Mars Hand Lens Imager
    "MARDI",  # Mars Descent Imager
    "NAVCAM",  # Navigation Camera
    "PANCAM",  # Panoramic Camera
    "MINITES",  # Miniature Thermal Emission Spectrometer
]

# Мінімальна дата, яку можна використовувати для запитів (дата посадки ровера Curiosity)
MIN_DATE = datetime(2012, 8, 6)

# Опис камер для допомоги у виборі
CAMERA_HELP_TEXT = "\n".join(
    [f"  {key}: {desc}" for key, desc in {
        "FHAZ": "Front Hazard Avoidance Camera",
        "RHAZ": "Rear Hazard Avoidance Camera",
        "MAST": "Mast Camera",
        "CHEMCAM": "Chemistry and Camera Complex",
        "MAHLI": "Mars Hand Lens Imager",
        "MARDI": "Mars Descent Imager",
        "NAVCAM": "Navigation Camera",
        "PANCAM": "Panoramic Camera",
        "MINITES": "Miniature Thermal Emission Spectrometer"
    }.items()]
)

# Функція для створення директорії
def create_directory(directory):
    """
    Створює папку, якщо вона ще не існує.

    :param directory: Назва папки, яку необхідно створити.
    """
    if not os.path.exists(directory):  # Перевіряємо, чи існує папка
        os.makedirs(directory)  # Якщо не існує, створюємо

# Функція для перевірки формату дати
def validate_date(date_text):
    """
    Перевіряє дату на коректність і допустимість.

    :param date_text: Дата у форматі "YYYY-MM-DD".
    :return: Кортеж (bool, str), де bool — валідність, str — помилка (якщо є).
    """
    try:
        user_date = datetime.strptime(date_text, "%Y-%m-%d")  # Пробуємо розпарсити дату
        today = datetime.now()  # Отримуємо поточну дату

        if user_date < MIN_DATE:  # Якщо дата раніше за мінімально допустиму
            return False, f"The date must not be earlier than {MIN_DATE.strftime('%Y-%m-%d')}."
        if user_date > today:  # Якщо дата в майбутньому
            return False, "The date cannot be in the future."

        return True, ""  # Дата коректна
    except ValueError:  # Якщо формат дати некоректний
        return False, "Invalid date format. Please use YYYY-MM-DD."

# Функція для завантаження фотографій
def download_mars_photos_by_date(earth_date, camera, api_key, show, save_directory):
    """
    Завантажує фотографії Марса з NASA API.

    :param earth_date: Дата у форматі "YYYY-MM-DD".
    :param camera: Камера, з якої потрібні знімки.
    :param api_key: Ключ NASA API.
    :param show: Прапор для показу зображень.
    :param save_directory: Шлях для збереження файлів.
    """
    if not save_directory or not os.path.isdir(save_directory):  # Перевіряємо, чи директорія вказана і існує
        print(f"Warning: The specified directory '{save_directory}' is invalid or not provided. Saving to the project directory.")
        save_directory = os.getcwd()  # Використовуємо поточну директорію

    base_url = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos"  # URL для запитів до NASA API
    params = {  # Параметри для запиту
        "earth_date": earth_date,
        "camera": camera,
        "api_key": api_key
    }

    response = requests.get(base_url, params=params)  # Виконуємо HTTP-запит

    if response.status_code != 200:  # Перевіряємо статус запиту
        print(f"Request failed with status code: {response.status_code}. Reason: {response.reason}")
        return

    photos = response.json().get('photos', [])  # Отримуємо список фото з відповіді
    if not photos:  # Якщо фото немає
        print(f"No photos found for the date {earth_date} and camera {camera}.")
        return

    rover_name = photos[0]['rover']['name']  # Отримуємо назву ровера
    directory_name = f"{earth_date}_{rover_name}_{camera}"  # Формуємо ім'я папки
    full_path = os.path.join(save_directory, directory_name)  # Повний шлях до папки
    create_directory(full_path)  # Створюємо папку

    print(f"Downloading {len(photos)} photos...")
    for photo in photos:
        img_url = photo['img_src']  # URL фото
        img_name = os.path.basename(img_url)  # Ім'я файлу
        img_path = os.path.join(full_path, img_name)  # Повний шлях до збереження

        print(f"Downloading: {img_url}")
        img_data = requests.get(img_url).content  # Завантажуємо дані фото
        with open(img_path, 'wb') as img_file:  # Зберігаємо файл
            img_file.write(img_data)

        if show:  # Якщо потрібно показувати фото
            image = Image.open(BytesIO(img_data))
            image.show()

    print(f"Photos saved in the directory: {full_path}")
    #print(photos) debug

# Головна функція
def main():
    """
    Обробляє аргументи командного рядка і запускає завантаження фото.
    """
    parser = argparse.ArgumentParser(
        description="A script to download Mars surface photos using NASA API.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--earth-date", required=True, help="Date in the format YYYY-MM-DD. Minimum date: 2012-08-06.")
    parser.add_argument("--camera", required=True, help=f"Camera (choose one from the list below):\n{CAMERA_HELP_TEXT}")
    parser.add_argument("--key", default="DEMO_KEY", help="NASA API key (default is DEMO_KEY).")
    parser.add_argument("--show", action="store_true", help="Display photos after downloading.")
    parser.add_argument("--output-dir", help="Directory to save the downloaded photos.")

    args = parser.parse_args()

    is_valid_date, date_error = validate_date(args.earth_date)  # Перевірка дати
    if not is_valid_date:
        print(f"Error: {date_error}")
        return

    if args.camera.upper() not in AVAILABLE_CAMERAS:  # Перевірка камери
        print(f"Error: Camera '{args.camera}' is not available.")
        print("Available cameras:", ", ".join(AVAILABLE_CAMERAS))
        return

    download_mars_photos_by_date(args.earth_date, args.camera.upper(), args.key, args.show, args.output_dir)

if __name__ == "__main__":
    main()
