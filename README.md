Esse branch contém o pipeline inicial que foi usado como base para o trabalho finalizado no branch main.
# ALPR didático — Projeto Aplicado Longitudinal (PDI, M2)

**Problema:** localizar a região de uma placa veicular e, futuramente, reconhecer seu texto (ALPR).  
**Etapa:** M2 — implementação parcial de segmentação em recortes de placas.  
**Integrantes:** José Vitor da Rosa (`j0se-R`), Kauã Kovalski de Campos (`Kovalskiiii`) e Emanuel Muller Bueno (`Emanuel-Muller`).

## Estado real da implementação

A M2 acrescenta um pipeline executável para explorar a segmentação preliminar de caracteres em imagens de placas recortadas. O código processa uma imagem ou divide uma montagem regular em amostras, gera imagens intermediárias e compara duas configurações de limiarização:

1. **Limiar fixo** (padrão 120).
2. **Limiarização de Otsu**, que escolhe automaticamente um limiar global a partir do histograma.

Ambas passam por escala de cinza, CLAHE, filtro Gaussiano, limiarização inversa, abertura morfológica e análise de componentes conexos. A saída inclui máscaras, visualizações dos componentes e `results/comparison.csv`.

**Limitação importante:** o arquivo versionado `imagens/input/samples-cropped.png` é uma montagem de 20 recortes de placas, não um conjunto de fotos completas de veículos. Portanto, esta implementação não demonstra ainda a localização da placa em uma cena inteira nem o reconhecimento OCR. A divisão da montagem em grade é uma conveniência experimental, não uma etapa geral de detecção. A comparação atual é exploratória: não há máscaras de referência nem contagem manual validada dos caracteres, então contagem de componentes e proporção de pixels de primeiro plano são indicadores diagnósticos, não acurácia de segmentação.

## Problema e objetivos atuais

O objetivo final permanece detectar a placa em uma imagem de veículo, retificar sua perspectiva, segmentar caracteres e reconhecer o texto. Para M2, o escopo executável foi reduzido deliberadamente à exploração de limiarização, morfologia e componentes sobre recortes disponíveis. A localização em cenas completas, retificação, OCR e avaliação com ground truth continuam pendentes para M3.

## Dados

- `imagens/input/samples-cropped.png`: montagem de 20 recortes de placas, resolução 1757 × 487 px.
- O arquivo não fornece anotações de bounding boxes, máscaras de caracteres ou texto esperado por amostra.
- Os recortes variam em iluminação, contraste, inclinação, desfoque e padrão de placa; são exemplos exploratórios e não devem ser tratados como amostra representativa de desempenho real.
- O dataset RodoSol-ALPR é descrito em `docs/proposta.md`, mas não está incluído no ZIP. Antes de usá-lo, siga as condições de acesso/licença do repositório oficial; não publique imagens restritas nem placas pessoais sem autorização.

## Tecnologias e instalação

- Python 3.10 ou superior
- OpenCV (`opencv-python`)
- NumPy

Crie e ative um ambiente virtual se desejar e instale as dependências:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Execução reproduzível

Na raiz do repositório:

```bash
python src/pipeline.py --input imagens/input/samples-cropped.png --output results --split-grid 5 4
```

O comando divide a montagem em 5 colunas × 4 linhas e processa 20 recortes. Para processar uma única imagem sem divisão:

```bash
python src/pipeline.py --input caminho/para/placa.png --output results/unica
```

Para alterar o limiar fixo e a área mínima dos componentes:

```bash
python src/pipeline.py --input imagens/input/samples-cropped.png --output results_teste --split-grid 5 4 --threshold 100 --min-area 15
```

Cada amostra gera `01_gray.png`, `02_clahe.png`, máscaras e imagens de componentes. `comparison.csv` reúne o limiar usado, pixels de primeiro plano, percentual de primeiro plano e número de componentes com área igual ou superior à mínima.

## Resultados M2

O experimento inicial é documentado em [`docs/relatorio_m2.md`](docs/relatorio_m2.md), incluindo a comparação fixa × Otsu, interpretação e limitações. Resultados gerados localmente são artefatos reproduzíveis e podem ser regenerados pelo comando acima.

## Estrutura

```text
.
├── README.md
├── requirements.txt
├── docs/
│   ├── proposta.md
│   └── relatorio_m2.md
├── imagens/input/
│   └── samples-cropped.png
├── src/
│   └── pipeline.py
└── results/                 # saídas do experimento de referência
    ├── comparison.csv
    └── sample_*/            # imagens intermediárias por recorte
```

## Evolução desde a M1 e feedback

A proposta da M1 permanece como objetivo final, mas a M2 adiciona código executável e saídas verificáveis. Como o arquivo de entrada disponível contém apenas recortes, o experimento foi limitado à segmentação preliminar em vez de afirmar que a detecção de placas em cenas completas já está implementada. A proposta de comparar contornos com Haar Cascade continua pertinente, mas ainda não foi executada porque o repositório não contém imagens de veículos completos nem resultados anotados para avaliar detecção.

## Plano para M3

1. **Dados e referência:** reunir um conjunto autorizado e documentar IDs, condições de aquisição, texto esperado e bounding boxes/máscaras manuais.
2. **Detecção:** implementar e comparar contornos com filtragem geométrica e uma cascata apropriada, avaliando IoU ou taxa de localização correta.
3. **Retificação:** usar cantos anotados ou estimados para gerar placas alinhadas.
4. **Segmentação:** comparar parâmetros de limiarização e morfologia contra máscaras ou caixas de caracteres de referência.
5. **OCR:** integrar Tesseract ou alternativa e avaliar correspondência exata da placa e taxa de erro por caractere.
6. **Reprodutibilidade:** fixar versões, separar dados de ajuste e avaliação, registrar falhas e atualizar vídeo/relatório.


## Uso de IA generativa

Este artefato foi preparado com assistência do ChatGPT (OpenAI) para estruturar/implementar o pipeline experimental e redigir documentação inicial.

## Referências

- Laroca, R. et al. “On the Cross-dataset Generalization in License Plate Recognition.” VISAPP, 2022.
- RodoSol-ALPR: https://github.com/raysonlaroca/rodosol-alpr-dataset
- OpenCV: https://docs.opencv.org/
- Tesseract OCR: https://github.com/tesseract-ocr/tesseract
