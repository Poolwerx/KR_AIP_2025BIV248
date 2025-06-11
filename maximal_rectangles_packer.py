from utils import read_input
from visualize import visualize
import json
import math
import sys
import os

class Rect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def fits(self, w, h):
        return self.width >= w and self.height >= h

    def intersects(self, other):
        return not (self.x + self.width <= other.x or
                    other.x + other.width <= self.x or
                    self.y + self.height <= other.y or
                    other.y + other.height <= self.y)

    def split(self, used):
        result = []
        if not self.intersects(used):
            return [self]

        if used.x > self.x:
            result.append(Rect(self.x, self.y, used.x - self.x, self.height))
        if used.x + used.width < self.x + self.width:
            result.append(Rect(used.x + used.width, self.y,
                               self.x + self.width - (used.x + used.width), self.height))
        if used.y > self.y:
            top_width = min(self.width, used.width)
            result.append(Rect(self.x, self.y, top_width, used.y - self.y))
        if used.y + used.height < self.y + self.height:
            bottom_width = min(self.width, used.width)
            result.append(Rect(self.x, used.y + used.height, bottom_width,
                               self.y + self.height - (used.y + used.height)))
        return result

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

def maximal_rectangles_packer(sheet_w, sheet_h, padding, figures):
    free_rects = [Rect(0, 0, sheet_w, sheet_h)]
    placed = []
    not_placed = []

    figures = sorted(figures, key=lambda f: max(f.width, f.height), reverse=True)

    for f in figures:
        best = None
        # Сохраним исходные размеры, чтобы не ломать объект
        orig_w, orig_h = f.width, f.height
        for rect in free_rects:
            for rotate in [False, True]:
                if rotate:
                    w, h = orig_h, orig_w
                else:
                    w, h = orig_w, orig_h

                if rect.fits(w + 2 * padding, h + 2 * padding):
                    x = rect.x + padding
                    y = rect.y + padding
                    # временно меняем размеры фигуры для проверки
                    f.width, f.height = w, h
                    if can_place(f, x, y, placed, sheet_w, sheet_h, padding):
                        best = (rect, x, y, w, h, rotate)
                        break
            if best:
                break

        if best:
            rect, x, y, w, h, rotated = best
            f.x, f.y = x, y
            f.width, f.height = w, h
            f.rotated = rotated
            placed.append(f)
            used_rect = Rect(x - padding, y - padding, w + 2 * padding, h + 2 * padding)

            new_free = []
            for fr in free_rects:
                new_free.extend(fr.split(used_rect))

            free_rects = filter_rectangles(new_free)
        else:
            not_placed.append(f)

    return placed, not_placed

def filter_rectangles(rects):
    filtered = []
    for r in rects:
        is_inside = False
        for o in rects:
            if o == r:
                continue
            if o.x <= r.x and o.y <= r.y and o.x + o.width >= r.x + r.width and o.y + o.height >= r.y + r.height:
                is_inside = True
                break
        if not is_inside:
            filtered.append(r)
    return filtered

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
        if f.type == 'rectangle':
            # Считаем с учётом паддинга по ширине и высоте
            used_area += (f.width + 2 * padding) * (f.height + 2 * padding)
        elif f.type == 'circle':
            used_area += math.pi * f.radius ** 2
        elif f.type == 'triangle':
            x1, y1 = f.vertices[0]
            x2, y2 = f.vertices[1]
            x3, y3 = f.vertices[2]
            used_area += abs((x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2)) / 2)
        elif f.type == 'polygon':
            verts = f.vertices
            area = 0
            n = len(verts)
            for i in range(n):
                x1, y1 = verts[i]
                x2, y2 = verts[(i + 1) % n]
                area += x1 * y2 - x2 * y1
            used_area += abs(area) / 2

    percent = used_area / total_area * 100 if total_area > 0 else 0

    print(f"\n📊 Статистика упаковки:")
    print(f"🧾 Общая площадь листа: {total_area}")
    print(f"🟩 Занятая площадь: {used_area:.2f}")
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
    placed, not_placed = maximal_rectangles_packer(sheet_w, sheet_h, padding, figures)
    write_output(placed, path='output_maxrects.json')
    calculate_area_stats(sheet_w, sheet_h, placed, len(figures), not_placed, padding)
    visualize(sheet_w, sheet_h, placed, padding, output_file='layout_maxrects.png')





