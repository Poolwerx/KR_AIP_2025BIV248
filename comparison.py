import os
import sys
import json
import time
from utils import read_input
from shelf_packer import shelf_pack, calculate_area_stats as shelf_stats
from greedy_packer import greedy_pack, calculate_area_stats as greedy_stats
from maximal_rectangles_packer import maximal_rectangles_packer, calculate_area_stats as maxrects_stats
from visualize import visualize
from copy import deepcopy


def compare_algorithms(input_file):
    # Чтение входных данных
    if not os.path.exists(input_file):
        print(f"Файл '{input_file}' не найден. Завершение.")
        sys.exit(1)

    sheet_w, sheet_h, padding, figures = read_input(input_file)
    total_count = len(figures)
    total_area = sheet_w * sheet_h

    # Словарь для хранения результатов
    results = {
        'Shelf': {'placed': None, 'not_placed': None, 'used_area': 0, 'percent': 0, 'time': 0},
        'Greedy': {'placed': None, 'not_placed': None, 'used_area': 0, 'percent': 0, 'time': 0},
        'MaxRects': {'placed': None, 'not_placed': None, 'used_area': 0, 'percent': 0, 'time': 0}
    }

    # Запуск Shelf Algorithm
    figures_copy = deepcopy(figures)
    start_time = time.perf_counter()
    placed, not_placed = shelf_pack(sheet_w, sheet_h, padding, figures_copy)
    results['Shelf']['time'] = time.perf_counter() - start_time
    results['Shelf']['placed'] = placed
    results['Shelf']['not_placed'] = not_placed
    visualize(sheet_w, sheet_h, placed, padding, output_file='layout_shelf.png')

    # Запуск Greedy Placement
    figures_copy = deepcopy(figures)
    start_time = time.perf_counter()
    placed, not_placed = greedy_pack(sheet_w, sheet_h, padding, figures_copy)
    results['Greedy']['time'] = time.perf_counter() - start_time
    results['Greedy']['placed'] = placed
    results['Greedy']['not_placed'] = not_placed
    visualize(sheet_w, sheet_h, placed, padding, output_file='layout_greedy.png')

    # Запуск Maximal Rectangles
    figures_copy = deepcopy(figures)
    start_time = time.perf_counter()
    placed, not_placed = maximal_rectangles_packer(sheet_w, sheet_h, padding, figures_copy)
    results['MaxRects']['time'] = time.perf_counter() - start_time
    results['MaxRects']['placed'] = placed
    results['MaxRects']['not_placed'] = not_placed
    visualize(sheet_w, sheet_h, placed, padding, output_file='layout_maxrects.png')

    # Сбор статистики
    for algo in results:
        placed = results[algo]['placed']
        not_placed = results[algo]['not_placed']
        used_area = 0
        for f in placed:
            pad = padding * 2
            if f.type == 'rectangle':
                used_area += (f.width + pad) * (f.height + pad)
            elif f.type == 'circle':
                used_area += 3.14159 * (f.radius + padding) ** 2
            elif f.type in ('triangle', 'polygon'):
                verts = f.vertices
                area = 0
                n = len(verts)
                for i in range(n):
                    x1, y1 = verts[i]
                    x2, y2 = verts[(i + 1) % n]
                    area += x1 * y2 - x2 * y1
                used_area += abs(area) / 2 + pad * max(f.width, f.height)
        results[algo]['used_area'] = used_area
        results[algo]['percent'] = (used_area / total_area * 100) if total_area > 0 else 0

    # Вывод сравнения в консоль
    print("\n📊 Сравнение алгоритмов упаковки:")
    print(f"{'Алгоритм':<12} | {'Размещено':<10} | {'% Заполнения':<12} | {'Время (с)':<10} | {'Неразмещённые ID'}")
    print("-" * 70)

    comparison_data = []
    for algo in results:
        placed_count = len(results[algo]['placed'])
        percent = results[algo]['percent']
        time_taken = results[algo]['time']
        not_placed_ids = [f.id for f in results[algo]['not_placed']]
        print(f"{algo:<12} | {placed_count:<10} | {percent:<12.2f} | {time_taken:<10.4f} | {not_placed_ids}")
        comparison_data.append({
            'Algorithm': algo,
            'Placed': placed_count,
            'Percent': percent,
            'Time': time_taken,
            'NotPlacedIDs': not_placed_ids
        })

    # Сохранение результатов в JSON
    with open('comparison_results.json', 'w', encoding='utf-8') as f:
        json.dump(comparison_data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Результаты сравнения сохранены в 'comparison_results.json'.")
    print("📈 Визуализации сохранены как 'layout_shelf.png', 'layout_greedy.png', 'layout_maxrects.png'.")


if __name__ == "__main__":
    input_file = input("Введите имя входного файла (например, input.txt): ").strip()
    compare_algorithms(input_file)