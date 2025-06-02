# Перед запуском !!!ОБЯЗАТЕЛЬНО!!! нужно убедиться что Python 3.11 установлен в системе.

# Пять свечей для призыва фиксиков⛧:           
# 1- Создаёт venv, устанавливает зависимости.
# 2- Ищет исполняемый файл Python 3.11 и запускает выбранный скрипт в его окружении.
# 3- Показывает список .py файлов.
# 5- Позволяет выбрать скрипт для запуска.
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⠈⠈⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⢸⡟⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⢸⡇⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⡛⢶⣄⡀⠀⠀⠀⠀⠀⢀⣀⣤⣼⡇⠀⠀⠀⠀⠀
# ⠀⠀⠐⣿⠃⠀⠀⠀⠀⠀⢹⣇⠀⢈⣙⣷⣶⣶⠒⠛⢉⣥⡿⠋⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⣿⠀⠀⢀⣀⣠⡴⠼⣿⡟⠋⠁⠀⠈⠉⠳⣦⣾⡛⠀⠀⠀⠘⣿⠀⠀⠀
# ⠀⠀⠀⠿⠶⠿⠯⢭⣤⣤⣀⣹⣷⡀⣀⣀⠀⢀⣼⠟⠍⠛⠷⣤⣄⣿⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣾⡏⢉⣿⠿⠛⠛⠓⠒⠒⠲⠿⠷⠿⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣷⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀



import subprocess                     # Для запуска внешних команд
import sys                            # Для выхода из программы
import os                             # Для работы с путями и файлами
import platform                       # Для определения ОС
from pathlib import Path              # Удобный интерфейс для путей

# === Функция поиска Python 3.11 ===
def get_python311_path():
    candidates = ['python3.11', 'python3', 'python']
    for name in candidates:
        try:
            output = subprocess.check_output([name, '--version'], stderr=subprocess.STDOUT)
            if output.decode().startswith('Python 3.11'):
                return name
        except Exception:
            continue

    # Для Windows: стандартные пути установки
    if platform.system() == 'Windows':
        possible_paths = [
            os.path.expandvars(r'%LocalAppData%\Programs\Python\Python311\python.exe'),
            r'C:\Python311\python.exe',
            r'C:\Program Files\Python311\python.exe',
        ]
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    output = subprocess.check_output([path, '--version'], stderr=subprocess.STDOUT)
                    if output.decode().startswith('Python 3.11'):
                        return path
                except Exception:
                    pass
    return None

# === Функция создания виртуального окружения ===
def create_virtualenv(python_bin, venv_dir='venv'):
    if not Path(venv_dir).exists():
        print(f"[+] Создаём виртуальное окружение в {venv_dir}")
        subprocess.check_call([python_bin, '-m', 'venv', venv_dir])
    else:
        print(f"[=] Виртуальное окружение уже существует.")

# === Установка зависимостей ===
def install_requirements(pip_path):
    print("[+] Устанавливаем зависимости из requirements.txt")
    subprocess.check_call([pip_path, 'install', '-r', 'requirements.txt'])

# === Определение путей к Python и pip в виртуальном окружении ===
def get_venv_paths(venv_dir='venv'):
    if platform.system() == 'Windows':
        python_path = os.path.join(venv_dir, 'Scripts', 'python.exe')
        pip_path = os.path.join(venv_dir, 'Scripts', 'pip.exe')
    else:
        python_path = os.path.join(venv_dir, 'bin', 'python')
        pip_path = os.path.join(venv_dir, 'bin', 'pip')
    return python_path, pip_path

# === Выбор скрипта для запуска ===
def choose_script():
    print("\n⛧⛧ Найденные .py файлы в текущей директории:")
    scripts = [f for f in os.listdir() if f.endswith('.py') and f != Path(__file__).name]
    if not scripts:
        print("⛧ Нет .py файлов для запуска.")
        return None

    for i, script in enumerate(scripts, 1):
        print(f"{i}. {script}")

    while True:
        choice = input("Введите номер скрипта для запуска: ")
        if choice.isdigit() and 1 <= int(choice) <= len(scripts):
            return scripts[int(choice) - 1]
        print("Неверный ввод. Попробуйте ещё раз.")

# === Основной блок ===
def main():
    python311 = get_python311_path()
    if not python311:
        print("⛧ Python 3.11 не найден. Установите его и попробуйте снова.")
        sys.exit(1)

    create_virtualenv(python311)
    python_path, pip_path = get_venv_paths()

    install_requirements(pip_path)

    script = choose_script()
    if script:
        print(f"\n 🤘🏻 Запускаем {script} через виртуальное окружение...\n")

        if not os.path.exists(python_path):
            print(f"⛧ Не найден файл {python_path}. Проверь, создано ли виртуальное окружение.")
            sys.exit(1)

        subprocess.run([python_path, script])
    else:
        print("☣ Скрипт не выбран. Выход.")

# === Точка входа ===
if __name__ == '__main__':
    main()
