#!/usr/bin/env python3
from pathlib import Path
import argparse, csv, re
import cv2
import numpy as np

EXPECTED_CHARS = 7
SEG = dict(fixed_t=120, adaptive_block=31, adaptive_c=10, open_k=2,
           h_min=0.22, h_max=0.95, w_max_ratio=1.0, w_min=0.02, margin=0.04)
PLATE_SIZE = {'car': (300, 100), 'motorcycle': (200, 170)}  # (largura, altura) após retificação


def load_annotation(txt_path):
    info = {}
    for line in Path(txt_path).read_text(encoding='utf-8').splitlines():
        k, _, v = line.partition(':')
        info[k.strip()] = v.strip()
    pts = [[int(a) for a in p.split(',')] for p in info['corners'].split()]
    info['corners'] = np.array(pts, np.float32)  # ordem: sup-esq, sup-dir, inf-dir, inf-esq
    return info


def list_samples(dataset_dir):
    files = sorted(Path(dataset_dir).glob('*/img_*.jpg'))
    return [(f.stem, f.parent.name, f) for f in files]


def split_ids(samples):
    return {sid: ('ajuste' if i % 3 == 0 else 'avaliacao') for i, (sid, _, _) in enumerate(samples)}


def iou(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    iw = max(0, min(ax + aw, bx + bw) - max(ax, bx)); ih = max(0, min(ay + ah, by + bh) - max(ay, by))
    inter = iw * ih
    return inter / (aw * ah + bw * bh - inter) if inter else 0.0


def detect_candidates(img, aspect_min, aspect_max, min_area=600, max_cands=5):
    gray = cv2.bilateralFilter(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 9, 75, 75)
    edges = cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize=3)            # bordas verticais (caracteres)
    _, b = cv2.threshold(edges, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    b = cv2.morphologyEx(b, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (25, 5)))
    b = cv2.morphologyEx(b, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3)))
    cnts, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cands = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        fill = cv2.contourArea(c) / (w * h)
        if h > 10 and aspect_min <= w / h <= aspect_max and w * h >= min_area and fill > 0.5:
            cands.append((w * h * fill, (x, y, w, h)))
    cands.sort(reverse=True)
    return [r for _, r in cands[:max_cands]]


def run_detection(samples, out_dir, split):
    configs = {'A_proporcao_1.8-5.5': (1.8, 5.5), 'B_proporcao_1.0-5.5': (1.0, 5.5)}
    rows = []
    (out_dir / 'deteccao').mkdir(parents=True, exist_ok=True)
    for sid, folder, path in samples:
        img = cv2.imread(str(path)); ann = load_annotation(path.with_suffix('.txt'))
        gt = cv2.boundingRect(ann['corners'].astype(np.int32))
        for name, (amin, amax) in configs.items():
            cands = detect_candidates(img, amin, amax)
            ious = [iou(c, gt) for c in cands]
            rows.append(dict(id=sid, pasta=folder, tipo=ann['type'], layout=ann['layout'], conjunto=split[sid],
                             config=name, n_candidatos=len(cands),
                             iou_top1=round(ious[0], 3) if ious else 0.0,
                             iou_melhor_de_5=round(max(ious), 3) if ious else 0.0))
            vis = img.copy()
            cv2.rectangle(vis, gt[:2], (gt[0] + gt[2], gt[1] + gt[3]), (0, 255, 0), 2)
            for i, (x, y, w, h) in enumerate(cands):
                cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 0, 255) if i == 0 else (0, 165, 255), 1)
            cv2.imwrite(str(out_dir / 'deteccao' / f'{sid}_{name[0]}.jpg'), vis)
    return rows


def rectify(img, ann):
    w, h = PLATE_SIZE[ann['type']]
    dst = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], np.float32)
    M = cv2.getPerspectiveTransform(ann['corners'], dst)
    return cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_CUBIC)


def binarize(blur, method, p):
    if method == 'fixo':
        return cv2.threshold(blur, p['fixed_t'], 255, cv2.THRESH_BINARY_INV)[1]
    if method == 'otsu':
        return cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    return cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                 p['adaptive_block'], p['adaptive_c'])


def segment(plate, method, p=SEG):
    gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4)).apply(gray)
    blur = cv2.GaussianBlur(clahe, (3, 3), 0)
    mask = binarize(blur, method, p)
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (p['open_k'], p['open_k']))
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
    H, W = opened.shape
    n, labels, stats, cents = cv2.connectedComponentsWithStats(opened, connectivity=8)
    chars = []
    for i in range(1, n):
        x, y, w, h, area = map(int, stats[i])
        touches = x <= p['margin'] * W * 0.25 or y <= 0 or x + w >= W - 1 or y + h >= H - 1
        if (p['h_min'] * H <= h <= p['h_max'] * H and w <= p['w_max_ratio'] * h
                and w >= p['w_min'] * W and not touches):
            comp = (labels == i).astype(np.uint8)
            cnt = max(cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0], key=cv2.contourArea)
            chars.append(dict(x=x, y=y, w=w, h=h, area_px=area, perimetro_px=round(cv2.arcLength(cnt, True), 1),
                              razao_aspecto=round(w / h, 3), cx=round(float(cents[i][0]), 1),
                              cy=round(float(cents[i][1]), 1)))
    return dict(gray=gray, clahe=clahe, mask=mask, opened=opened, chars=chars)


def run_segmentation(samples, out_dir, split, p=SEG):
    rows, desc = [], []
    for sid, folder, path in samples:
        img = cv2.imread(str(path)); ann = load_annotation(path.with_suffix('.txt'))
        plate = rectify(img, ann)
        sdir = out_dir / 'segmentacao' / sid; sdir.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(sdir / '01_placa_retificada.png'), plate)
        for method in ('fixo', 'otsu', 'adaptativo'):
            r = segment(plate, method, p)
            if method == 'fixo':
                cv2.imwrite(str(sdir / '02_clahe.png'), r['clahe'])
            cv2.imwrite(str(sdir / f'03_mascara_{method}.png'), r['mask'])
            cv2.imwrite(str(sdir / f'04_abertura_{method}.png'), r['opened'])
            vis = cv2.cvtColor(r['gray'], cv2.COLOR_GRAY2BGR)
            for c in r['chars']:
                cv2.rectangle(vis, (c['x'], c['y']), (c['x'] + c['w'] - 1, c['y'] + c['h'] - 1), (0, 200, 0), 1)
            cv2.imwrite(str(sdir / f'05_componentes_{method}.png'), vis)
            n = len(r['chars'])
            rows.append(dict(id=sid, tipo=ann['type'], layout=ann['layout'], conjunto=split[sid], config=method,
                             n_esperado=EXPECTED_CHARS, n_detectado=n,
                             erro_contagem=n - EXPECTED_CHARS, erro_abs=abs(n - EXPECTED_CHARS),
                             acerto_exato=int(n == EXPECTED_CHARS)))
            for j, c in enumerate(sorted(r['chars'], key=lambda c: (c['y'] > plate.shape[0] * 0.5 and ann['type'] == 'motorcycle', c['x']))):
                desc.append(dict(id=sid, config=method, ordem=j + 1, **c))
    return rows, desc


def write_csv(path, rows):
    if not rows:
        return
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


def summarize(rows, keys, value_fields):
    groups = {}
    for r in rows:
        groups.setdefault(tuple(r[k] for k in keys), []).append(r)
    out = []
    for g, rs in sorted(groups.items()):
        d = dict(zip(keys, g)); d['n_imagens'] = len(rs)
        for vf in value_fields:
            d[vf] = round(float(np.mean([r[vf] for r in rs])), 3)
        out.append(d)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dataset', default='dataset', help='Pasta com subpastas img_*.jpg + img_*.txt')
    ap.add_argument('--output', default='results', help='Diretório de resultados')
    args = ap.parse_args()
    samples = list_samples(args.dataset)
    if not samples:
        raise SystemExit(f'Nenhuma imagem em {args.dataset}/*/img_*.jpg')
    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
    split = split_ids(samples)
    write_csv(out / 'split.csv', [dict(id=s, conjunto=split[s]) for s, _, _ in samples])

    det = run_detection(samples, out, split)
    write_csv(out / 'metricas_deteccao.csv', det)
    for r in det:
        r['detectou_iou50_top1'] = int(r['iou_top1'] >= 0.5)
    write_csv(out / 'resumo_deteccao.csv',
              summarize(det, ['config', 'tipo'], ['iou_top1', 'iou_melhor_de_5', 'detectou_iou50_top1']))

    seg, desc = run_segmentation(samples, out, split)
    write_csv(out / 'metricas_segmentacao.csv', seg)
    write_csv(out / 'descritores_componentes.csv', desc)
    write_csv(out / 'resumo_segmentacao_por_conjunto.csv',
              summarize(seg, ['conjunto', 'config'], ['erro_abs', 'acerto_exato']))
    write_csv(out / 'resumo_segmentacao_por_tipo.csv',
              summarize(seg, ['tipo', 'config'], ['erro_abs', 'acerto_exato']))
    print(f'Imagens: {len(samples)} (ajuste={sum(v=="ajuste" for v in split.values())}, '
          f'avaliacao={sum(v=="avaliacao" for v in split.values())})')
    print(f'Resultados em: {out.resolve()}')


if __name__ == '__main__':
    main()
