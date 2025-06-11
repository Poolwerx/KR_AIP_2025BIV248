import matplotlib.pyplot as plt
import matplotlib.patches as patches

def visualize(sheet_w, sheet_h, figures, padding, output_file='layout.png'):
    fig, ax = plt.subplots(figsize=(sheet_w / 100, sheet_h / 100))
    ax.set_xlim(0, sheet_w)
    ax.set_ylim(0, sheet_h)
    ax.set_aspect('equal')
    ax.set_title('Figure Layout')

    for f in figures:
        if f.x is not None:
            if f.type == 'rectangle':
                shape = patches.Rectangle((f.x, f.y), f.width, f.height, edgecolor='black', facecolor='skyblue')
                ax.add_patch(shape)
                ax.text(f.x + f.width / 2, f.y + f.height / 2, str(f.id), ha='center', va='center', fontsize=8)

            elif f.type == 'circle':
                shape = patches.Circle((f.x + f.radius, f.y + f.radius), f.radius, edgecolor='black', facecolor='lightgreen')
                ax.add_patch(shape)
                ax.text(f.x + f.radius, f.y + f.radius, str(f.id), ha='center', va='center', fontsize=8)

            elif f.type == 'triangle' or f.type == 'polygon':
                translated = [(f.x + vx, f.y + vy) for vx, vy in f.vertices]
                shape = patches.Polygon(translated, edgecolor='black', facecolor='orange' if f.type == 'polygon' else 'lightcoral')
                ax.add_patch(shape)

                # Центр тяжести (приблизительный, без учёта площади)
                cx = sum(x for x, _ in translated) / len(translated)
                cy = sum(y for _, y in translated) / len(translated)
                ax.text(cx, cy, str(f.id), ha='center', va='center', fontsize=8)

    # Граница листа
    border = patches.Rectangle((0, 0), sheet_w, sheet_h, linewidth=2, edgecolor='red', facecolor='none')
    ax.add_patch(border)

    plt.gca().invert_yaxis()
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    plt.show()

