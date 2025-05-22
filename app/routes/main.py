from flask import Blueprint, render_template

from app import socketio
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

def open_table(name: str) -> Table:
    if name not in _tables:
        raise ValueError(f"Table '{name}' does not exist")
    return _tables[name]

@main_bp.route('/')
def index():
    return render_template('index.html')

@socketio.on('update_table')
def handle_update_table(data):
    print(data)
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

new_table("a", 2 ,2)