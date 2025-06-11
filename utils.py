# utils.py
from typing import List, Tuple, Optional

class Figure:
    """
    Класс Figure представляет замкнутую плоскую фигуру для упаковки:
    - Поддерживает типы: rectangle, circle, triangle, polygon.
    - Рассчитывает габариты (width, height).
    - Нормализует координаты для многоугольников.
    """
    def __init__(
        self,
        fig_id: int,
        fig_type: str,
        param1: Optional[int] = None,
        param2: Optional[int] = None,
        vertices: Optional[List[Tuple[int, int]]] = None
    ):
        self.id = fig_id
        self.type = fig_type.lower()

        if self.type == 'rectangle':
            self.original_width = param1
            self.original_height = param2
            self.width = param1
            self.height = param2
            self.rotated = False

        elif self.type == 'circle':
            self.radius = param1
            self.width = self.height = 2 * self.radius

        elif self.type in ('triangle', 'polygon'):
            if not vertices:
                raise ValueError(f"Vertices must be provided for type {self.type}")
            self.vertices = vertices

            # Определение габаритов фигуры по вершинам
            xs = [v[0] for v in vertices]
            ys = [v[1] for v in vertices]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            self.width = max_x - min_x
            self.height = max_y - min_y

            # Нормализация координат в локальную систему (0, 0)
            self.vertices = [(x - min_x, y - min_y) for x, y in vertices]

        else:
            raise ValueError(f"Unknown figure type: {self.type}")

        # Позиция после упаковки (заполняется алгоритмом)
        self.x = None
        self.y = None
        self.rotated = False


def read_input(file_path: str) -> Tuple[int, int, int, List[Figure]]:
    """
    Считывает данные из входного файла.
    Возвращает: ширину листа, высоту листа, отступ, список фигур.
    """
    figures = []
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Чтение параметров листа
    sheet_w = int(lines[0].split(":")[1])
    sheet_h = int(lines[1].split(":")[1])
    padding = int(lines[2].split(":")[1])

    # Пропускаем 4-ю строку с заголовком
    for line in lines[4:]:
        parts = line.split()
        fig_id = int(parts[0])
        fig_type = parts[1].lower()

        if fig_type == 'rectangle':
            w = int(parts[2])
            h = int(parts[3])
            figures.append(Figure(fig_id, fig_type, w, h))

        elif fig_type == 'circle':
            r = int(parts[2])
            figures.append(Figure(fig_id, fig_type, r))

        elif fig_type in ('triangle', 'polygon'):
            coords = list(map(int, parts[2:]))
            if len(coords) < 6 or len(coords) % 2 != 0:
                raise ValueError(f"Invalid number of coordinates for {fig_type} ID {fig_id}")
            vertices = [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)]
            figures.append(Figure(fig_id, fig_type, vertices=vertices))

        else:
            raise ValueError(f"Unsupported figure type: {fig_type}")

    return sheet_w, sheet_h, padding, figures



