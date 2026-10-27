#!/usr/bin/env python3
from pathlib import Path
import argparse
import cv2
import numpy as np

METHODS = ('fixo', 'otsu', 'adaptativo')


def label(img, text):
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if img.ndim == 2 else img.copy()
    cv2.rectangle(img, (0, 0), (img.shape[1], 16), (0, 0, 0), -1)
    cv2.putText(img, text, (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    return img


def panel(results, sample_id, out_path):
    d = Path(results) / 'segmentacao' / sample_id
    plate = cv2.imread(str(d / '01_placa_retificada.png'))
    rows = []
    for m in METHODS:
        cells = [label(plate, 'retificada'), label(cv2.imread(str(d / f'03_mascara_{m}.png'), 0), f'mascara {m}'),
                 label(cv2.imread(str(d / f'04_abertura_{m}.png'), 0), 'abertura 2x2'),
                 label(cv2.imread(str(d / f'05_componentes_{m}.png')), 'componentes')]
        rows.append(np.hstack(cells))
    cv2.imwrite(str(out_path), np.vstack(rows))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--results', default='results'); ap.add_argument('--out', default='docs/figs')
    a = ap.parse_args(); Path(a.out).mkdir(parents=True, exist_ok=True)
    panel(a.results, 'img_000004', Path(a.out) / 'fig1_sucesso_carro_img_000004.png')
    panel(a.results, 'img_027509', Path(a.out) / 'fig2_falha_moto_img_027509.png')
    panel(a.results, 'img_017507', Path(a.out) / 'fig3_moto_adaptativo_vs_global_img_017507.png')
    d = Path(a.results) / 'deteccao'
    for sid in ('img_000004', 'img_017503'):
        a_ = cv2.resize(cv2.imread(str(d / f'{sid}_A.jpg')), (640, 360)); b_ = cv2.resize(cv2.imread(str(d / f'{sid}_B.jpg')), (640, 360))
        cv2.imwrite(str(Path(a.out) / f'fig4_deteccao_{sid}.png'), np.hstack([label(a_, 'A: proporcao 1.8-5.5'), label(b_, 'B: proporcao 1.0-5.5')]))
