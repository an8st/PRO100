import json
import uuid

import ffmpeg
from flask import Blueprint, render_template, request, jsonify
from vosk import Model, KaldiRecognizer
import wave
import os
import re

from app import socketio
from app.model.Table import Table

main_bp = Blueprint('main', __name__)
_tables = {}
FFMPEG_BIN = r'C:\ProgramData\chocolatey\bin\ffmpeg.exe'

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


def recognize_speech_vosk(audio_file_path, model_path='path_to_your_vosk_model'):
    wf = wave.open(audio_file_path, "rb")
    
    model = Model(model_path)
    rec = KaldiRecognizer(model, wf.getframerate())
    
    full_text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            full_text += result.get("text", "") + " "
    
    final_result = json.loads(rec.FinalResult())
    full_text += final_result.get("text", "")
    print(full_text.strip())
    return full_text.strip()


# Обработчик POST /new_command
@main_bp.route('/new_command', methods=['POST'])
def new_command():
    if 'command' not in request.files:
        return jsonify({"error": "Audio not found"}), 400

    audio_file = request.files['command']

    temp_input = f"temp_{uuid.uuid4().hex}.webm"
    temp_output = f"temp_{uuid.uuid4().hex}.wav"

    audio_file.save(temp_input)

    try:
        ffmpeg.input(temp_input).output(temp_output).run(
            cmd=FFMPEG_BIN,
            quiet=True,
            overwrite_output=True
        )
        command_text = recognize_speech_vosk(temp_output, model_path='vosk-model-small-ru-0.22')
        print("Распознанная команда:", command_text)
    except Exception as e:
        return jsonify({"error": f"Recognition error: {e}"}), 500
    finally:
        if os.path.exists(temp_input): os.remove(temp_input)
        if os.path.exists(temp_output): os.remove(temp_output)

    
    def word_to_number(word):
        num_words = {
            'один': 1, 'одна': 1, 'одной': 1,
            'два': 2, 'две': 2, 'двумя': 2,
            'три': 3, 'тремя': 3,
            'четыре': 4, 'четырьмя': 4,
            'пять': 5, 'пятью': 5,
            'шесть': 6, 'шестью': 6,
            'семь': 7, 'семью': 7,
            'восемь': 8, 'восемью': 8,
            'девять': 9, 'девятью': 9,
            'десять': 10, 'десятью': 10
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

    return jsonify({"error": "The command is not recognized or is not supported."}), 400


@main_bp.route('/')
def index():
    return render_template('index.html')

@socketio.on('update_table')
def handle_update_table(data):
    try:
        name = data['name']
        row = int(data['row'])
        col = int(data['col'])
        value = data['value']
        update_table(name, row, col, value)
        table_json = open_table(name)
        socketio.emit('table_updated', table_json)
    except Exception as e:
        socketio.emit('table_updated', {"error": str(e)})

new_table("1", 2 ,2)