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

Seleção, download e validação estrutural concluídos.

Verificação dos termos de uso e avaliação do modelo ainda pendentes.

## Resultado da seleção

Seleção executada com semente 42 e sorteio de 20 imagens por classe,
seguido da união dos IDs e remoção de duplicatas.

- Imagens únicas: 196.
- Anotações preservadas: 1.431.
- Objetos individuais: 1.415.
- Anotações de multidões (iscrowd): 16.

| Classe | Imagens com objetos individuais | Objetos individuais |
|---|---:|---:|
| person | 114 | 418 |
| chair | 77 | 260 |
| couch | 42 | 59 |
| potted plant | 43 | 78 |
| dining table | 61 | 90 |
| laptop | 37 | 46 |
| cup | 46 | 110 |
| bottle | 46 | 123 |
| book | 44 | 182 |
| cell phone | 38 | 49 |

Uma imagem pode conter várias classes, portanto as contagens
da coluna de imagens não devem ser somadas como arquivos distintos.

O manifesto está em [dataset_manifesto.json](dataset_manifesto.json).

### Estado após a seleção

Seleção, contagens e download concluídos. As 196 imagens passaram
pelas verificações de integridade, leitura e dimensões.
Nenhuma métrica do modelo foi calculada.

## Validação estrutural

O script scripts/validar_dataset.py verificou:

- Unicidade dos IDs.
- Correspondência das imagens e classes com o manifesto.
- Leitura e dimensões das imagens.
- Referências de imagem e categoria das anotações.
- Coordenadas finitas, dimensões positivas e limites das bounding boxes.
- Área positiva e valores válidos de iscrowd.
- Presença de pelo menos 20 imagens com objetos individuais por classe.

Resultado: 196 imagens, 10 classes e 1.431 anotações,
incluindo 16 de multidões. Nenhum erro ou aviso encontrado.

Essa verificação é estrutural e não substitui a inspeção visual
das anotações nem a avaliação das previsões do detector.

## Inspeção visual de uma amostra das anotações

Foram inspecionados cinco exemplos gerados a partir das anotações
de referência, sem executar o detector:

- book, imagem 89648: materiais semelhantes sem marcação;
  possível ambiguidade de categoria ou omissão.
- cell phone, imagem 537991: caixas coerentes com os dois aparelhos.
- chair, imagem 221708: caixas coerentes, com objetos parcialmente ocultos.
- couch, imagem 293625: extensão da caixa considerada duvidosa.
- potted plant, imagem 277197: caixa coerente com uma planta pequena ao fundo.

As anotações originais foram preservadas. A inspeção evidencia
que consistência estrutural não garante ausência de ambiguidades
ou imperfeições na referência.

Também foram inspecionados:

- bottle, imagem 133244: objeto muito pequeno; confirmação visual
  inconclusiva na resolução examinada.
- cup, imagem 31296: marcações plausíveis, com sobreposição de rótulos
  dificultando a inspeção dos objetos pequenos.
- dining table, imagem 85157: caixa compatível com a região visível
  da mesa, parcialmente encoberta por pessoas.
- laptop, imagem 111609: caixa correspondente ao equipamento
  parcialmente cortado pela borda da imagem.
- person, imagem 422998: caixa coerente com a pessoa parcialmente
  enquadrada, sem necessidade de o rosto estar visível.

A amostra de dez exemplos, um por classe, foi inspecionada.
As dúvidas foram registradas e as anotações originais preservadas.
Não foi realizada revisão visual completa das 1.431 anotações.