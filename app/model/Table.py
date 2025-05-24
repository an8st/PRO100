class Table:
    def __init__(self, name: str, columns: list[str]):
        self.name = name
        self.columns = columns
        self.rows = []
        self.description = ""

    def add_row(self, row: list):
        if len(row) != len(self.columns):
            raise ValueError(f"Row length ({len(row)}) does not match number of columns ({len(self.columns)})")
        self.rows.append(row)

    def get_row(self, index: int) -> list:
        return self.rows[index]

    def get_column(self, column_name: str) -> list:
        if column_name not in self.columns:
            raise ValueError(f"Column '{column_name}' not found")
        idx = self.columns.index(column_name)
        return [row[idx] for row in self.rows]

    def update_cell(self, row_index: int, column_index: int, value):
        if not (0 <= row_index < len(self.rows)):
            raise IndexError("Row index out of range")
        if not (0 <= column_index < len(self.columns)):
            raise IndexError("Column index out of range")
        self.rows[row_index-1][column_index] = value

    def update_cell_by_name(self, row_index: int, column_name: str, value):
        if column_name not in self.columns:
            raise ValueError(f"Column '{column_name}' not found")
        column_index = self.columns.index(column_name)
        self.update_cell(row_index, column_index, value)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'columns': self.columns,
            'rows': self.rows,
            'description': self.description
        }

    def __repr__(self):
        return f"<Table '{self.name}' with {len(self.columns)} columns and {len(self.rows)} rows>"
