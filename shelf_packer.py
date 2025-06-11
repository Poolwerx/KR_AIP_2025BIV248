from utils import read_input
from visualize import visualize
import json
import os
import sys

def shelf_pack(sheet_w, sheet_h, padding, figures):
    figures.sort(key=lambda f: f.height, reverse=True)

    x_cursor = padding
    y_cursor = padding
    row_height = 0

    placed = []
    not_placed = []

    for f in figures:
        if x_cursor + f.width + padding > sheet_w:
            x_cursor = padding
            y_cursor += row_height + padding
            row_height = 0

        if y_cursor + f.height + padding > sheet_h:
            not_placed.append(f)
            continue

        f.x = x_cursor
        f.y = y_cursor
        x_cursor += f.width + padding
        row_height = max(row_height, f.height)
        placed.append(f)

    return placed, not_placed

def write_output(figures, path='output.json'):
    data = []
    for f in figures:
        data.append({'id': f.id, 'type': f.type, 'x': f.x, 'y': f.y})
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Output written to {path}.")

def polygon_area(vertices):
    n = len(vertices)
    area = 0
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2

def calculate_area_stats(sheet_w, sheet_h, placed, total_count, not_placed, padding):
    total_area = sheet_w * sheet_h
    used_area = 0

    for f in placed:
        if f.type == 'rectangle':
            # Добавляем паддинг к ширине и высоте
            used_area += (f.width + padding) * (f.height + padding)
        elif f.type == 'circle':
            used_area += 3.14159 * f.radius ** 2
        elif f.type == 'triangle':
            x1, y1 = f.vertices[0]
            x2, y2 = f.vertices[1]
            x3, y3 = f.vertices[2]
            used_area += abs((x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2)) / 2)
        elif f.type == 'polygon':
            used_area += polygon_area(f.vertices)

    percent = used_area / total_area * 100 if total_area > 0 else 0

    print(f"\n📊 Статистика упаковки:")
    print(f"🧾 Общая площадь листа: {total_area}")
    print(f"🟩 Занятая площадь фигурами (с паддингом): {used_area:.2f}")
    print(f"📈 Заполнено: {percent:.2f}%")
    print(f"✔️ Размещено фигур: {len(placed)} из {total_count}")
    print(f"❌ Не влезло: {len(not_placed)}")
    if not_placed:
        print(f"❗️ ID неразмещённых фигур: {[f.id for f in not_placed]}")
    print()

if __name__ == "__main__":
    input_file = input("Введите имя входного файла (например, input.txt): ").strip()
    if not input_file or not os.path.exists(input_file):
        print(f"Файл '{input_file}' не найден. Завершение.")
        sys.exit(1)

    sheet_w, sheet_h, padding, figures = read_input(input_file)
    placed, not_placed = shelf_pack(sheet_w, sheet_h, padding, figures)

    write_output(placed, path='output_shelf.json')
    calculate_area_stats(sheet_w, sheet_h, placed, len(figures), not_placed, padding)
    visualize(sheet_w, sheet_h, placed, padding, output_file='layout_shelf.png')


