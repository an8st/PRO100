import json

from flask import Blueprint, render_template

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


@main_bp.route('/')
def index():
    return render_template('index.html')
