from utils import read_input
from visualize import visualize
import json
import math
import sys
import os

def rectangles_intersect(r1, r2, padding):
    return not (r1['x'] + r1['width'] + padding <= r2['x'] or
                r2['x'] + r2['width'] + padding <= r1['x'] or
                r1['y'] + r1['height'] + padding <= r2['y'] or
                r2['y'] + r2['height'] + padding <= r1['y'])

def can_place(f, x, y, placed, sheet_w, sheet_h, padding):
    if x < padding or y < padding:
        return False
    if x + f.width + padding > sheet_w or y + f.height + padding > sheet_h:
        return False

    new_rect = {'x': x, 'y': y, 'width': f.width, 'height': f.height}
    for pf in placed:
        placed_rect = {'x': pf.x, 'y': pf.y, 'width': pf.width, 'height': pf.height}
        if rectangles_intersect(new_rect, placed_rect, padding):
            return False
    return True

def try_place_with_rotation(f, placed, sheet_w, sheet_h, padding):
    """
    Пытаемся разместить прямоугольник с поворотом и без.
    Возвращает True если размещён, иначе False.
    """
    options = [(f.width, f.height, False), (f.height, f.width, True)]
    for w, h, rotated in options:
        f.width, f.height = w, h
        for y in range(sheet_h - h - padding, padding - 1, -1):
            for x in range(padding, sheet_w - w - padding + 1):
                if can_place(f, x, y, placed, sheet_w, sheet_h, padding):
                    f.x = x
                    f.y = y
                    f.rotated = rotated
                    return True
    return False

def greedy_pack(sheet_w, sheet_h, padding, figures):
    placed = []
    not_placed = []

    figures = sorted(figures, key=lambda f: max(f.width, f.height), reverse=True)

    for f in figures:
        f.rotated = False  # флаг поворота (для прямоугольников)
        if f.type == 'rectangle':
            if try_place_with_rotation(f, placed, sheet_w, sheet_h, padding):
                placed.append(f)
            else:
                not_placed.append(f)
        else:
            placed_flag = False
            for y in range(sheet_h - f.height - padding, padding - 1, -1):
                for x in range(padding, sheet_w - f.width - padding + 1):
                    if can_place(f, x, y, placed, sheet_w, sheet_h, padding):
                        f.x = x
                        f.y = y
                        placed.append(f)
                        placed_flag = True
                        break
                if placed_flag:
                    break
            if not placed_flag:
                not_placed.append(f)

    return placed, not_placed

def write_output(figures, path='output.json'):
    data = []
    for f in figures:
        entry = {'id': f.id, 'x': f.x, 'y': f.y}
        if hasattr(f, 'rotated'):
            entry['rotated'] = f.rotated
        data.append(entry)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Output written to {path}.")

def calculate_area_stats(sheet_w, sheet_h, placed, total_count, not_placed, padding):
    total_area = sheet_w * sheet_h
    used_area = 0

    for f in placed:
        # Учитываем padding по ширине и высоте
        pad = padding * 2

        if f.type == 'rectangle':
            used_area += (f.width + pad) * (f.height + pad)
        elif f.type == 'circle':
            used_area += math.pi * (f.radius + padding) ** 2
        elif f.type == 'triangle':
            x1, y1 = f.vertices[0]
            x2, y2 = f.vertices[1]
            x3, y3 = f.vertices[2]
            base_area = abs((x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2)) / 2)
            # Увеличим площадь с запасом padding
            # Примерная оценка — прибавим padding к габаритам треугольника (упрощённо)
            used_area += base_area + pad * max(f.width, f.height)
        elif f.type == 'polygon':
            verts = f.vertices
            area = 0
            n = len(verts)
            for i in range(n):
                x1, y1 = verts[i]
                x2, y2 = verts[(i + 1) % n]
                area += x1 * y2 - x2 * y1
            base_area = abs(area) / 2
            # Аналогично треугольнику — прибавим запас
            used_area += base_area + pad * max(f.width, f.height)

    percent = used_area / total_area * 100

    print(f"\n📊 Статистика упаковки:")
    print(f"🧾 Общая площадь листа: {total_area}")
    print(f"🟩 Занятая площадь (с padding): {used_area:.2f}")
    print(f"📈 Заполнено: {percent:.2f}%")
    print(f"✔️ Размещено фигур: {len(placed)} из {total_count}")
    print(f"❌ Не влезло: {total_count - len(placed)}")
    if not_placed:
        print(f"- ❗️ ID неразмещённых фигур: {[f.id for f in not_placed]}")
    print()

if __name__ == "__main__":
    input_file = input("Введите имя входного файла (например, input.txt): ").strip()
    if not input_file or not os.path.exists(input_file):
        print(f"Файл '{input_file}' не найден. Завершение.")
        sys.exit(1)

    sheet_w, sheet_h, padding, figures = read_input(input_file)
    placed, not_placed = greedy_pack(sheet_w, sheet_h, padding, figures)
    write_output(placed, path='output_greedy.json')
    calculate_area_stats(sheet_w, sheet_h, placed, len(figures), not_placed, padding)
    visualize(sheet_w, sheet_h, placed, padding, output_file='layout_greedy.png')


