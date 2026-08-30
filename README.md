# Detecção e Reconhecimento de Placas Veiculares (ALPR)

> Projeto aplicado longitudinal — Disciplina de Processamento de Imagens — UNIVALI
> Etapa atual: **M1**

## Integrantes

- [José Vitor da Rosa] — [j0se-R]
- [Kauã Kovalski de Campos] — [Kovalskiiii]
- [Emanuel Muller Bueno] — [Emanuel-Muller]

## Problema investigado

O projeto tem como objetivo detectar automaticamente a região correspondente à placa
de um veículo em uma imagem e reconhecer os caracteres nela contidos, produzindo como
saída o texto da placa em formato legível (ex: `ABC1D23`).

O problema envolve processamento e análise de imagens porque exige, entre outras
etapas: realce de bordas, segmentação da região de interesse, correção de perspectiva
e segmentação de caracteres individuais antes de qualquer etapa de reconhecimento.

## Contexto de aplicação

Sistemas de reconhecimento automático de placas (ALPR — *Automatic License Plate
Recognition*) são amplamente utilizados em contextos como controle de acesso a
estacionamentos, fiscalização de trânsito (radares, pedágios) e sistemas de
monitoramento urbano. O projeto pretende produzir
uma versão simplificada e didática de um sistema para avaliar a eficácia das técnicas
de PDI aplicadas ao problema.

## Objetivo geral

Desenvolver um pipeline de processamento de imagens capaz de localizar a placa de um
veículo em uma foto e extrair o texto correspondente, avaliando a taxa de acerto em
um conjunto de imagens de teste.

### Objetivos específicos

- Implementar a etapa de pré-processamento (conversão para escala de cinza, realce de
  contraste, redução de ruído).
- Implementar e comparar métodos de detecção da região da placa (contornos +
  filtragem geométrica vs. Haar Cascade).
- Implementar a correção de perspectiva da região detectada.
- Implementar a segmentação dos caracteres individuais da placa.
- Avaliar ao menos uma abordagem de reconhecimento de caracteres (OCR).

## Visão resumida da solução proposta

Pipeline clássico de PDI: pré-processamento → detecção da região da placa →
correção de perspectiva → segmentação de caracteres → reconhecimento (OCR).
Ver detalhes em [`docs/proposta.md`](docs/proposta.md).

## Conjunto de imagens

- Dataset público [rodosol-alpr-dataset][https://github.com/raysonlaroca/rodosol-alpr-dataset/tree/main] (Github), com imagens anotadas em PNG.
- Fotos próprias, complementando o dataset público com placas no padrão Mercosul.

Detalhes de origem, licença e forma de obtenção em [`docs/proposta.md`](docs/proposta.md).

## Estágio atual do projeto (M1)

- [x] Definição do problema e escopo
- [x] Conjunto inicial de imagens selecionado
- [x] Pipeline preliminar definido
- [ ] Primeiros experimentos exploratórios (leitura/visualização das imagens)
- [ ] Vídeo da M1 gravado

## Organização do repositório

```text
projeto-placas/
├── README.md
├── docs/
│   └── proposta.md
├── images/
│   ├── input/
│   └── results/
├── src/
├── notebooks/
├── tests/
├── LICENSE
└── .gitignore
```

## Tecnologias

- C++
- OpenCV
- (a definir) biblioteca de OCR — ex: Tesseract

## Como reproduzir

> A ser preenchido conforme experimentos forem adicionados ao repositório.

## Vídeo da M1

Link:

## Uso de Inteligência Artificial generativa

Declaro que não utilizei ferramentas de Inteligência Artificial generativa na elaboração do código, dos testes, das imagens, do relatório ou de outros artefatos deste laboratório.

## Referências


- R. Laroca, E. V. Cardoso, D. R. Lucio, V. Estevam, and D. Menotti, "On the Cross-dataset Generalization in License Plate Recognition," International Conference on Computer Vision Theory and Applications (VISAPP), 2022.
- Repositório do dataset RodoSol-ALPR: [https://github.com/raysonlaroca/rodosol-alpr-dataset](https://github.com/raysonlaroca/rodosol-alpr-dataset)