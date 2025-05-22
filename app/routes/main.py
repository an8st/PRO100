import json

from flask import Blueprint, render_template, request, jsonify
import speech_recognition as sr
import re


from app.model.Table import Table

main_bp = Blueprint('main', __name__)
_tables = {}
def new_table(name: str, rows: int, columns: int):
    if name in _tables:
        raise ValueError(f"Table '{name}' already exists")
    col_names = [f"col_{i+1}" for i in range(columns)]
    table = Table(name, col_names)
    for _ in range(rows):
        table.add_row(["" for _ in range(columns)])
    _tables[name] = table

def drop_table(name: str):
    if name not in _tables:
        raise ValueError(f"Table '{name}' does not exist")
    del _tables[name]

def update_table(name: str, row: int, column: int, data: str):
    if name not in _tables:
        raise ValueError(f"Table '{name}' does not exist")
    _tables[name].update_cell(row, column, data)

def open_table(name: str) -> str:
    if name not in _tables:
        raise ValueError(f"Table '{name}' does not exist")
    table = _tables[name]
    return json.dumps(table.to_dict(), ensure_ascii=False, indent=2)


def new_table(name: str, rows: int, columns: int):
    return f"Создана таблица '{name}' с {rows} строками и {columns} колонками."

def drop_table(name: str):
    return f"Таблица '{name}' удалена."

def update_table(name: str, row: int, col: int, data: str):
    return f"Таблица '{name}', строка {row}, колонка {col} обновлены данными: {data}"

def open_table(name: str):
    return f"Таблица '{name}' открыта."

# Обработчик POST /new_command
@main_bp.route('/new_command', methods=['POST'])
def new_command():
    if 'command' not in request.files:
        return jsonify({"error": "Audio not found"}), 400
    
    audio_file = request.files['command']
    
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        command_text = recognizer.recognize_google(audio, language='ru-RU')
        print("Распознанная команда:", command_text)
    except sr.UnknownValueError:
        return jsonify({"error": "Failed to recognize speech"}), 400
    except sr.RequestError as e:
        return jsonify({"error": f"Recognition service error: {e}"}), 500
    
    def word_to_number(word):
        num_words = {
            'один': 1, 'одна': 1,
            'два': 2, 'две': 2,
            'три': 3,
            'четыре': 4,
            'пять': 5,
            'шесть': 6,
            'семь': 7,
            'восемь': 8,
            'девять': 9,
            'десять': 10
        }
        if word.isdigit():
            return int(word)
        return num_words.get(word.lower())

    patterns = [
        {
            'regex': r'создать(?:\s+е|ть)?\s+таблицу\s+(\w+)\s+с\s+(\w+)\s+(?:строками|строка)\s*и\s*(\w+)\s+(?:колонками|колонка)',
            'func': new_table,
            'args': ['name', 'rows', 'columns']
        },
        {
            'regex': r'удалить(?:\s+е|ть)?\s+таблицу\s+(\w+)',
            'func': drop_table,
            'args': ['name']
        },
        {
            'regex': r'обновить(?:\s+е|ть)?\s+таблицу\s+(\w+)\s+на\s+строке\s+(\w+)\s+и\s+колонке\s+(\w+)\s+данными\s+(.+)',
            'func': update_table,
            'args': ['name', 'row', 'col', 'data']
        },
        {
            'regex': r'открыть(?:\s+е|ть)?\s+таблицу\s+(\w+)',
            'func': open_table,
            'args': ['name']
        }
    ]

    for pattern in patterns:
        match = re.match(pattern['regex'], command_text, re.IGNORECASE)
        if match:
            params = match.groups()
            kwargs = {}
            for i, arg_name in enumerate(pattern['args']):
                value = params[i]
                if arg_name in ['rows', 'columns', 'row', 'col']:
                    value = word_to_number(value)
                kwargs[arg_name] = value
            result = pattern['func'](**kwargs)
            return jsonify({"result": result})

    return jsonify({"error": "The command is not recognized or supported"}), 400

@main_bp.route('/')
def index():
    return render_template('index.html')
