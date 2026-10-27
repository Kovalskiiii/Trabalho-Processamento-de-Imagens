# ALPR didático — Projeto Aplicado Longitudinal (PDI, M2)

**Problema:** localizar a placa de um veículo em uma imagem e segmentar/reconhecer seus caracteres (ALPR).  
**Etapa:** M2 — implementação parcial com avaliação quantitativa contra a anotação do dataset.  
**Integrantes:** José Vitor da Rosa (`j0se-R`), Kauã Kovalski de Campos (`Kovalskiiii`), Emanuel Muller Bueno (`Emanuel-Muller`).  
**Tecnologias:** Python 3.10+ e OpenCV. *Mudança em relação à M1:* a proposta previa C++; o grupo passou para Python por maior facilidade de desenvolvimento e experimentação do grupo (OpenCV tem a mesma API em ambas).

## Estágio atual

| Etapa | Estado |
|---|---|
| Entrada: leitura de imagens + anotação (texto, layout, 4 cantos) | Implementado |
| Detecção da placa (contornos + filtro geométrico), 2 configurações, IoU | Implementado, **resultado fraco** (ver relatório) |
| Retificação por perspectiva | Implementado, **usando os cantos anotados** (entrada "oráculo"); estimar os cantos automaticamente é M3 |
| Segmentação de caracteres (limiar fixo × Otsu × adaptativo → abertura → componentes) | Implementado e avaliado (erro de contagem vs. 7 caracteres) |
| Descritores por componente (área, perímetro, caixa, aspecto, centroide) | Implementado (`results/descritores_componentes.csv`) |
| Haar Cascade, OCR | Pendentes (M3) |

Resultado principal (17 imagens de avaliação, erro absoluto médio na contagem de caracteres): fixo 1,53 · Otsu 1,47 · **adaptativo 0,41**. Detalhes, falhas e limitações em [`docs/relatorio_m2.md`](docs/relatorio_m2.md).

## Dados

Amostra de 26 imagens do RodoSol-ALPR (1280×720): 8 carros-br, 9 motos-br, 9 motos-me; 17 padrão brasileiro e 9 Mercosul. Origem, licença, seleção e divisão ajuste/avaliação estão em [`dataset/README.md`](dataset/README.md) e no relatório. **As imagens do dataset não são versionadas**; veja `dataset/README.md` para obtê-las e colocá-las em `dataset/`.

## Instalação

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1   |   Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Execução reproduzível

```bash
python src/pipeline.py --dataset dataset --output results   # experimentos 1 e 2 (~1 min)
python src/make_figures.py --results results --out docs/figs # figuras do relatório
```

Exemplo mínimo: com `dataset/cars-br/img_000004.jpg` (+ `.txt`) presente, `results/segmentacao/img_000004/` contém `01_placa_retificada.png`, `02_clahe.png`, `03_mascara_<método>.png`, `04_abertura_<método>.png` e `05_componentes_<método>.png`, e `results/metricas_segmentacao.csv` registra `n_detectado = 7` para os três métodos.

Saídas: `results/metricas_deteccao.csv`, `resumo_deteccao.csv`, `metricas_segmentacao.csv`, `resumo_segmentacao_por_conjunto.csv`, `resumo_segmentacao_por_tipo.csv`, `descritores_componentes.csv`, `split.csv`, e imagens em `results/deteccao/` e `results/segmentacao/`.

O experimento exploratório anterior (montagem de 20 recortes, sem referência) foi preservado em `src/exploratorio_montagem.py` e `results/exploratorio_montagem/` (roda com `imagens/input/samples-cropped.png`); não entra nas conclusões da M2.

## Estrutura

```text
.
├── README.md  requirements.txt  .gitignore
├── dataset/              # README + amostra local (imagens não versionadas)
├── docs/                 # proposta.md, relatorio_m2.md, figs/
├── imagens/input/        # montagem do experimento exploratório
├── src/                  # pipeline.py, make_figures.py, exploratorio_montagem.py
└── results/              # CSVs, deteccao/, segmentacao/, exploratorio_montagem/
```

## Evolução desde a M1 e feedback

Ver seção 2 do relatório. **Pendente (grupo):** colar o feedback real recebido na M1 e a ação tomada para cada item.

## Plano para M3

Detecção automática dos cantos (para retificar sem oráculo), comparação com Haar Cascade, tratamento de placas pequenas/2 linhas, OCR (Tesseract) com avaliação por placa exata e erro por caractere, anotação de caixas de caracteres para IoU/Dice, ampliação do conjunto. Tarefas e responsáveis na seção 8 do relatório.

## Contribuições

A preencher pelo grupo, com evidências (tabela na seção 9 do relatório).

## Vídeo M2

Link do YouTube não listado: **a inserir após a gravação**.

## Uso de IA generativa

Para a etapa M2, foi utilizado o Claude (Anthropic), na criação da estrutura de pastas do projeto e para redigir o documento "README.md".

## Referências

- Laroca, R. et al. “On the Cross-dataset Generalization in License Plate Recognition.” VISAPP, 2022.
- RodoSol-ALPR: https://github.com/raysonlaroca/rodosol-alpr-dataset
- OpenCV: https://docs.opencv.org/ · Tesseract OCR: https://github.com/tesseract-ocr/tesseract
