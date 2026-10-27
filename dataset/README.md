# Dataset (não versionado)

Amostra do **RodoSol-ALPR** (Laroca et al., VISAPP 2022), distribuído apenas para pesquisa acadêmica.
Obtenção: https://github.com/raysonlaroca/rodosol-alpr-dataset (acordo de licença enviado por e-mail institucional).
As imagens e anotações **não** são versionadas (ver `.gitignore`).

Estrutura esperada (mesma do dataset original):

```text
dataset/
├── cars-br/          img_000001.jpg + img_000001.txt ...   (carros, placa padrão brasileiro)
├── motocycles-br/    img_017501.jpg + img_017501.txt ...   (motos, padrão brasileiro)
└── motocycles-me/    img_027501.jpg + img_027501.txt ...   (motos, padrão Mercosul)
```

Cada `.txt` tem: `type`, `plate`, `layout` e `corners` (4 cantos "x,y": sup-esq, sup-dir, inf-dir, inf-esq).
Amostra usada na M2: 26 imagens (8 carros-br, 9 motos-br, 9 motos-me). A pasta `cars-me` está vazia na amostra.
