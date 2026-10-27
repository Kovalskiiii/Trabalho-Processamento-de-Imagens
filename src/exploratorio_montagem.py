#!/usr/bin/env python3
from pathlib import Path
import argparse, csv
import cv2
import numpy as np

def split_grid(image, cols, rows):
    h, w = image.shape[:2]
    tiles = []
    # Divide a imagem proporcionalmente; adequado a montagens regulares.
    for r in range(rows):
        for c in range(cols):
            x0, x1 = round(c*w/cols), round((c+1)*w/cols)
            y0, y1 = round(r*h/rows), round((r+1)*h/rows)
            tiles.append((f"sample_{r+1:02d}_{c+1:02d}", image[y0:y1, x0:x1]))
    return tiles

def process(image, out_dir, fixed_threshold, min_area):
    out_dir.mkdir(parents=True, exist_ok=True)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image.copy()
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    blur = cv2.GaussianBlur(clahe, (3, 3), 0)
    _, fixed = cv2.threshold(blur, fixed_threshold, 255, cv2.THRESH_BINARY_INV)
    otsu_t, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    fixed_m = cv2.morphologyEx(fixed, cv2.MORPH_OPEN, kernel, iterations=1)
    otsu_m = cv2.morphologyEx(otsu, cv2.MORPH_OPEN, kernel, iterations=1)
    cv2.imwrite(str(out_dir/'01_gray.png'), gray)
    cv2.imwrite(str(out_dir/'02_clahe.png'), clahe)
    cv2.imwrite(str(out_dir/'03_fixed_mask.png'), fixed)
    cv2.imwrite(str(out_dir/'04_fixed_opening.png'), fixed_m)
    cv2.imwrite(str(out_dir/'05_otsu_mask.png'), otsu)
    cv2.imwrite(str(out_dir/'06_otsu_opening.png'), otsu_m)
    rows = []
    for name, mask in [('fixed', fixed_m), ('otsu', otsu_m)]:
        count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, 8)
        valid = []
        overlay = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        for i in range(1, count):
            x,y,w,h,area = map(int, stats[i])
            if area >= min_area:
                valid.append((x,y,w,h,area))
                cv2.rectangle(overlay, (x,y), (x+w-1,y+h-1), (0,255,0), 1)
        cv2.imwrite(str(out_dir/f'07_components_{name}.png'), overlay)
        rows.append({
            'config': name,
            'threshold': fixed_threshold if name == 'fixed' else round(float(otsu_t), 2),
            'foreground_pixels': int(cv2.countNonZero(mask)),
            'foreground_ratio_pct': round(100*cv2.countNonZero(mask)/mask.size, 3),
            'components_area_ge_min': len(valid),
            'min_area_px': min_area
        })
    return rows

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', required=True, help='Imagem de entrada')
    ap.add_argument('--output', default='results/exploratorio_montagem', help='Diretório de resultados')
    ap.add_argument('--threshold', type=int, default=120, help='Limiar fixo (0-255)')
    ap.add_argument('--min-area', type=int, default=12, help='Área mínima de componente em pixels')
    ap.add_argument('--split-grid', nargs=2, type=int, metavar=('COLS','ROWS'),
                    help='Divide uma montagem regular em recortes antes de processar')
    args = ap.parse_args()
    image = cv2.imread(args.input)
    if image is None:
        raise SystemExit(f'Não foi possível abrir a imagem: {args.input}')
    out = Path(args.output)
    if args.split_grid:
        tiles = split_grid(image, args.split_grid[0], args.split_grid[1])
    else:
        tiles = [(Path(args.input).stem, image)]
    all_rows = []
    for sample_name, tile in tiles:
        sample_dir = out / sample_name
        rows = process(tile, sample_dir, args.threshold, args.min_area)
        for row in rows:
            row['sample'] = sample_name
            all_rows.append(row)
    out.mkdir(parents=True, exist_ok=True)
    fields = ['sample','config','threshold','foreground_pixels','foreground_ratio_pct',
              'components_area_ge_min','min_area_px']
    with (out/'comparison.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f'Amostras processadas: {len(tiles)}')
    print(f'Resultados: {out.resolve()}')
    print(f'Tabela: {(out/"comparison.csv").resolve()}')

if __name__ == '__main__':
    main()
