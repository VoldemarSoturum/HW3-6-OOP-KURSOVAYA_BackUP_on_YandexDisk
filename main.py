# Coursework on object-oriented programming, theme "Backup from API dog.ceo"


# Курсовая работа «Резервное копирование»

# Возможна такая ситуация, что мы хотим показать друзьям фотографии из Интернета, но иногда сайты могут быть недоступны. Давайте защитимся от такого.
# Нужно написать программу для резервного копирования картинок с сайта про собак в облачное хранилище Яндекс.Диск.
# Для названий картинок использовать название породы + имя файла из url'а.
# Информацию по сохраненным фотографиям сохранить в json-файл.
# Задание:

# Нужно написать программу, которая будет:

#     Получать картинки по API с сайта dog.ceo. Пример api для получения Ирландского спаниеля.
#     Если у породы есть под-породы, то необходимо загрузить по одной картинки всех под-пород. Для получения картинок всех под-пород есть API метод.
#     Сохранить картинки в папку на Яндекс.Диск. Папка должна иметь название породы собаки.
#     Для названий картинки использовать название породы + имя файла из url'а.
#     Сохранять информацию по фотографиям в json-файл с результатами.

# Входные данные:

# Пользователь вводит:

#     Название породы.
#     Токен с Полигона Яндекс.Диска. Важно: Токен публиковать в github не нужно!

# Выходные данные:

#     json-файл с информацией по загруженным файлам:

# [
#   {
#     "file_name": "irish_spaniel_02102973_603.jpg",
#   },
#   {
#     "file_name": "irish_spaniel_7967686.jpg",
#   },
#   ...
# ]

#     Измененный Я.диск, куда добавились фотографии. ​ ​

# Обязательные требования к программе:

#     Использовать REST API Я.Диска и ключ, полученный с полигона.
#     Для загруженных картинок нужно создать свою папку на Я.Диске.
#     Загрузка картинок осуществляется по воздуху, т.е. локально фотографии не сохраняются. В Я.Полигоне есть необходимый метод.
#     Сделать прогресс-бар или логирование для отслеживания процесса программы.
#     Код программы должен удовлетворять PEP8.
#     У программы должен быть свой отдельный репозиторий.
#     Все зависимости должны быть указаны в файле requiremеnts.txt.


import os
import requests
import json
import importlib.util
import logging
from tqdm import tqdm

CONFIG_FILE = 'config.py'
YANDEX_FOLDER = 'dogs_picture'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


def create_config_with_token():
    token = input("Введите ваш токен Яндекс.Диска: ").strip()
    if not token:
        logging.error("Ошибка: токен не может быть пустым.")
        return False
    content = f"YANDEX_TOKEN = '{token}'\n"
    with open(CONFIG_FILE, 'w') as f:
        f.write(content)
    logging.info(f"Токен сохранён в {CONFIG_FILE}.")
    return True


def load_token():
    if not os.path.exists(CONFIG_FILE):
        logging.warning(f"Файл {CONFIG_FILE} не найден. Запрашиваем токен.")
        if not create_config_with_token():
            exit(1)

    spec = importlib.util.spec_from_file_location("config", CONFIG_FILE)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)

    token = getattr(config, "YANDEX_TOKEN", None)
    if not token:
        logging.error(f"В {CONFIG_FILE} не найден токен.")
        if not create_config_with_token():
            exit(1)
        spec.loader.exec_module(config)
        token = getattr(config, "YANDEX_TOKEN", None)
        if not token:
            logging.critical("Ошибка при загрузке токена.")
            exit(1)
    return token


def validate_token(token: str) -> bool:
    headers = {"Authorization": f"OAuth {token}"}
    response = requests.get("https://cloud-api.yandex.net/v1/disk", headers=headers)
    return response.status_code == 200


def get_valid_token():
    """Загружает и валидирует токен, при недействительности запрашивает новый."""
    token = load_token()
    while not validate_token(token):
        logging.warning("Недействительный токен. Пожалуйста, введите новый.")
        if not create_config_with_token():
            continue
        # Перезагружаем config.py после обновления токена
        spec = importlib.util.spec_from_file_location("config", CONFIG_FILE)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        token = getattr(config, "YANDEX_TOKEN", None)
    logging.info("⛤ Токен валиден.")
    return token


def ensure_yandex_folder(yandex_token: str, folder_name: str):
    headers = {"Authorization": f"OAuth {yandex_token}"}
    check_url = "https://cloud-api.yandex.net/v1/disk/resources"
    params = {"path": folder_name}
    response = requests.get(check_url, headers=headers, params=params)

    if response.status_code == 200:
        logging.info(f"Папка '{folder_name}' уже существует.")
    elif response.status_code == 404:
        create_response = requests.put(check_url, headers=headers, params=params)
        if create_response.status_code == 201:
            logging.info(f"Создана папка '{folder_name}' на Яндекс.Диске.")
        else:
            logging.error(f"Не удалось создать папку '{folder_name}': {create_response.status_code}")
            exit(1)
    else:
        logging.error(f"Ошибка при проверке папки '{folder_name}': {response.status_code}")
        exit(1)


def get_sub_breeds(breed: str):
    url = f'https://dog.ceo/api/breed/{breed}/list'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            return data['message']
    return []


def get_breed_image(breed: str):
    url = f'https://dog.ceo/api/breed/{breed}/images/random'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            return data['message']
    return None


def get_sub_breed_image(breed: str, sub_breed: str):
    url = f'https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            return data['message']
    return None


def upload_to_yandex_disk(yandex_token: str, image_url: str, folder: str, filename: str):
    try:
        img_data = requests.get(image_url).content
        yandex_path = f"{folder}/{filename}"

        headers = {"Authorization": f"OAuth {yandex_token}"}
        params = {"path": yandex_path, "overwrite": "true"}
        response = requests.get(
            "https://cloud-api.yandex.net/v1/disk/resources/upload",
            headers=headers,
            params=params
        )

        if response.status_code == 200:
            upload_url = response.json()["href"]
            upload_response = requests.put(upload_url, files={"file": img_data})
            if upload_response.status_code in (201, 202):
                logging.info(f"⛤ Загружено: {yandex_path}")
                return filename
            else:
                logging.error(f"⛧ Ошибка загрузки файла: {upload_response.status_code}")
        else:
            logging.error(f"⛧ Ошибка получения upload URL: {response.status_code}")
    except Exception as e:
        logging.exception(f"⛧ Ошибка при загрузке {filename}: {e}")

    return None


def main():
    token = get_valid_token()
    ensure_yandex_folder(token, YANDEX_FOLDER)

    user_input = input(
        "Введите породу или под-породу собаки (например, 'bulldog' или 'english bulldog'): "
    ).strip().lower()
    parts = user_input.split()
    if len(parts) == 2:
        sub_breed, breed = parts[0], parts[1]
    else:
        breed = parts[0]
        sub_breed = None

    sub_breeds = get_sub_breeds(breed)
    images_info = []

    if sub_breeds:
        if sub_breed and sub_breed in sub_breeds:
            logging.info(f"Загружаем картинку под-породы '{sub_breed}' породы '{breed}'")
            url = get_sub_breed_image(breed, sub_breed)
            if url:
                filename = f"{breed}_{sub_breed}_{url.split('/')[-1]}"
                saved_name = upload_to_yandex_disk(token, url, YANDEX_FOLDER, filename)
                if saved_name:
                    images_info.append({'file_name': saved_name})
        else:
            logging.info(f"Загружаем картинки всех под-пород породы '{breed}'")
            for sb in tqdm(sub_breeds, desc=f"Под-породы {breed}"):
                url = get_sub_breed_image(breed, sb)
                if url:
                    filename = f"{breed}_{sb}_{url.split('/')[-1]}"
                    saved_name = upload_to_yandex_disk(token, url, YANDEX_FOLDER, filename)
                    if saved_name:
                        images_info.append({'file_name': saved_name})
    else:
        logging.info(f"Загружаем картинку породы '{breed}'")
        url = get_breed_image(breed)
        if url:
            filename = f"{breed}_{url.split('/')[-1]}"
            saved_name = upload_to_yandex_disk(token, url, YANDEX_FOLDER, filename)
            if saved_name:
                images_info.append({'file_name': saved_name})

    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(images_info, f, ensure_ascii=False, indent=4)

    logging.info(f"Готово! Загружено {len(images_info)} изображений.")
    print("Информация записана в result.json.")


if __name__ == '__main__':
    main()
