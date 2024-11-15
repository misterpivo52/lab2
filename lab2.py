import os
import argparse
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime

# Список доступних камер для запитів до NASA API
AVAILABLE_CAMERAS = [
    "FHAZ",  # Front Hazard Avoidance Camera (Передня камера запобігання небезпеці)
    "RHAZ",  # Rear Hazard Avoidance Camera (Задня камера запобігання небезпеці)
    "MAST",  # Mast Camera (Камера на щоглі)
    "CHEMCAM",  # Chemistry and Camera Complex (Хімічна камера)
    "MAHLI",  # Mars Hand Lens Imager (Камера ручної лінзи Марса)
    "MARDI",  # Mars Descent Imager (Камера спуску на Марс)
    "NAVCAM",  # Navigation Camera (Камера навігації)
    "PANCAM",  # Panoramic Camera (Панорамна камера)
    "MINITES",  # Miniature Thermal Emission Spectrometer (Мініатюрний тепловий спектрометр)
]

# Мінімальна допустима дата для запитів до NASA API (6 серпня 2012 року — дата посадки Curiosity)
MIN_DATE = datetime(2012, 8, 6)

# Форматований опис доступних камер для відображення у підказках
CAMERA_HELP_TEXT = "\n".join(
    [f"  {key}: {desc}" for key, desc in {
        "FHAZ": "Front Hazard Avoidance Camera (Передня камера запобігання небезпеці)",
        "RHAZ": "Rear Hazard Avoidance Camera (Задня камера запобігання небезпеці)",
        "MAST": "Mast Camera (Камера на щоглі)",
        "CHEMCAM": "Chemistry and Camera Complex (Хімічна камера)",
        "MAHLI": "Mars Hand Lens Imager (Камера ручної лінзи Марса)",
        "MARDI": "Mars Descent Imager (Камера спуску на Марс)",
        "NAVCAM": "Navigation Camera (Камера навігації)",
        "PANCAM": "Panoramic Camera (Панорамна камера)",
        "MINITES": "Miniature Thermal Emission Spectrometer (Мініатюрний тепловий спектрометр)"
    }.items()]
)

# Функція для створення директорії, якщо вона ще не існує
def create_directory(directory):
    """
    Створює директорію, якщо вона ще не існує.

    :param directory: Назва директорії, яку потрібно створити.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

# Функція для перевірки формату дати та її допустимого діапазону
def validate_date(date_text):
    """
    Перевіряє коректність введеної дати.

    :date_text: Дата у форматі "YYYY-MM-DD".
    :return: Кортеж (bool, str), де bool вказує на валідність дати, а str — на помилку (якщо є).
    """
    try:
        user_date = datetime.strptime(date_text, "%Y-%m-%d")
        today = datetime.now()

        # Перевірка, чи дата не раніше за мінімальну допустиму
        if user_date < MIN_DATE:
            return False, f"The date must not be earlier than {MIN_DATE.strftime('%Y-%m-%d')}."

        # Перевірка, чи дата не в майбутньому
        if user_date > today:
            return False, "The date cannot be in the future."

        return True, ""
    except ValueError:
        return False, "Invalid date format. Please use YYYY-MM-DD."

# Функція для завантаження фотографій Марса
def download_mars_photos_by_date(earth_date, camera, api_key, show, save_directory):
    """
    Завантажує фотографії Марса за вказаною датою, камерою та ключем API.

    earth_date: Дата у форматі "YYYY-MM-DD".
    camera: Назва камери.
    api_key: Ключ для доступу до NASA API.
    show: Чи потрібно показувати завантажені фотографії.
    save_directory: Шлях до папки для збереження файлів.
    """
    # Перевірка, чи вказано існуючу директорію
    if not save_directory or not os.path.isdir(save_directory):
        print(f"Warning: The specified directory '{save_directory}' is invalid or not provided. Saving to the project directory.")
        save_directory = os.getcwd()

    base_url = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos"
    params = {
        "earth_date": earth_date,
        "camera": camera,
        "api_key": api_key
    }

    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        print(f"Request failed with status code: {response.status_code}. Reason: {response.reason}")
        return

    photos = response.json().get('photos', [])
    if not photos:
        print(f"No photos found for the date {earth_date} and camera {camera}.")
        return

    # Отримуємо назву ровера
    rover_name = photos[0]['rover']['name']
    directory_name = f"{earth_date}_{rover_name}_{camera}"
    full_path = os.path.join(save_directory, directory_name)  # Зберігаємо у вибраній папці або у проєктній
    create_directory(full_path)

    print(f"Downloading {len(photos)} photos...")
    for photo in photos:
        img_url = photo['img_src']
        img_name = os.path.basename(img_url)
        img_path = os.path.join(full_path, img_name)

        print(f"Downloading: {img_url}")
        img_data = requests.get(img_url).content
        with open(img_path, 'wb') as img_file:
            img_file.write(img_data)

        # Показ фото, якщо вказано
        if show:
            image = Image.open(BytesIO(img_data))
            image.show()

    print(f"Photos saved in the directory: {full_path}")

# Головна функція програми
def main():
    """
    Обробляє аргументи командного рядка та запускає завантаження фотографій.
    """
    parser = argparse.ArgumentParser(
        description="A script to download Mars surface photos using NASA API.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--earth-date", required=True, help="Date in the format YYYY-MM-DD. Minimum date: 2012-08-06.")
    parser.add_argument("--camera", required=True, help=f"Camera (choose one from the list below):\n{CAMERA_HELP_TEXT}")
    parser.add_argument("--key", default="DEMO_KEY", help="NASA API key (default is DEMO_KEY).")
    parser.add_argument("--show", action="store_true", help="Display photos after downloading.")
    parser.add_argument("--output-dir", help="Directory to save the downloaded photos(not necessary).")

    args = parser.parse_args()

    # Перевірка введеної дати
    is_valid_date, date_error = validate_date(args.earth_date)
    if not is_valid_date:
        print(f"Error: {date_error}")
        return

    # Перевірка введеної камери
    if args.camera.upper() not in AVAILABLE_CAMERAS:
        print(f"Error: Camera '{args.camera}' is not available.")
        print("Available cameras:", ", ".join(AVAILABLE_CAMERAS))
        return

    # Завантаження фотографій
    download_mars_photos_by_date(args.earth_date, args.camera.upper(), args.key, args.show, args.output_dir)

if __name__ == "__main__":
    main()

