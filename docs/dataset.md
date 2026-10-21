# Dataset de avaliação

## Objetivo

Avaliar o YOLO26n pré-treinado na detecção de 10 classes de objetos
do cotidiano, utilizando imagens com anotações de referência.

Esta etapa não inclui treinamento ou fine-tuning.

## Fonte planejada

- Dataset: COCO 2017.
- Partição: validação (val2017).
- Site oficial: https://cocodataset.org/
- Anotações: bounding boxes e categorias no formato COCO JSON.

Serão baixadas apenas as imagens selecionadas e os arquivos
necessários para preparar a avaliação.

## Classes selecionadas

| Nome no modelo | Nome em português |
|---|---|
| person | Pessoa |
| chair | Cadeira |
| couch | Sofá |
| potted plant | Planta em vaso |
| dining table | Mesa de jantar |
| laptop | Notebook |
| cup | Copo ou caneca |
| bottle | Garrafa |
| book | Livro |
| cell phone | Celular |

Os identificadores das categorias no COCO serão associados aos
identificadores do modelo pelo nome da classe. Não será presumido
que os números sejam iguais nos dois formatos.

## Método de seleção planejado

- Utilizar uma semente fixa: 42.
- Selecionar aleatoriamente 20 imagens por classe, sem reposição
  dentro de cada classe.
- Unir as seleções e remover imagens duplicadas.
- Não utilizar as previsões do detector para escolher as imagens.
- Preservar todas as anotações das 10 classes nas imagens escolhidas.

Uma imagem pode conter várias classes. Assim, a união poderá ter
menos de 200 imagens e mais de 20 imagens contendo determinada classe.

Se alguma classe não tiver imagens elegíveis suficientes, o script
deverá informar o problema, sem reduzir a meta silenciosamente.

## Preparação e verificação

- Conferir a existência e a leitura das imagens.
- Verificar dimensões, categorias e bounding boxes.
- Registrar o tratamento das anotações de multidões (iscrowd).
- Contar imagens e objetos por classe.
- Registrar os IDs das imagens selecionadas em um manifesto.
- Preservar os metadados de origem e licença disponíveis.

As regras de tratamento serão documentadas antes do cálculo
das métricas.

## Avaliação planejada

- Inspeção visual de acertos e erros.
- Métricas de detecção utilizando as anotações de referência.
- Tempo de inferência em CPU, com procedimento documentado.
- Análise dos resultados por classe.

Os parâmetros serão registrados antes da avaliação. Se forem
ajustados após observar os resultados, essa exploração será
identificada na documentação.

## Limitações

- A amostra é pequena e selecionada por classe.
- Os resultados não representam o desempenho no COCO completo.
- COCO é um benchmark utilizado no desenvolvimento e na avaliação
  dessa família de modelos.
- A avaliação não comprova generalização para um domínio novo.
- Fotos próprias poderão complementar a análise qualitativa,
  sem serem misturadas às métricas do conjunto anotado.

## Termos de uso e armazenamento

Referência: https://cocodataset.org/#termsofuse

A licença das anotações e as licenças das imagens serão verificadas
separadamente antes de qualquer redistribuição.

As imagens e os arquivos volumosos permanecerão locais.
O repositório conterá o código de preparação, a documentação
e o manifesto necessário para reproduzir a seleção.

## Situação atual

Planejamento definido. Download, verificação de licenças,
seleção e contagens reais ainda pendentes.