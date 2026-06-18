# PITCH: Voice Assistant

PITCH — минималистичный голосовой ассистент для Windows, работающий по горячей клавише. Переводит речь в отредактированный текст с помощью Groq API непосредственно в активное текстовое поле.

## Системные требования

- Windows OS
- Python 3.8+
- Микрофон
- Активное интернет-соединение и Groq API ключ

## Установка

1. Создайте и активируйте виртуальное окружение:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Установите зависимости:
   ```powershell
   pip install -r requirements.txt
   ```

## Запуск и использование

Запуск в режиме разработки:
```powershell
python main.py
```

Управление:
- Запись: удерживайте `Ctrl + Windows` во время речи. После отпускания клавиш текст автоматически вставится в активное поле ввода.
- Настройки: дважды кликните по иконке приложения в трее Windows, чтобы открыть панель управления. Вставьте API-ключ Groq на вкладке Settings.

## Сборка в исполняемый файл (.exe)

Сборка автономного исполняемого файла с помощью PyInstaller:
```powershell
pip install pyinstaller
pyinstaller --noconsole --onefile --name="PITCH" --icon=icon.ico --add-data "assets/p.jpeg;assets" main.py
```
Исполняемый файл `PITCH.exe` будет сохранен в папке `dist/`.
