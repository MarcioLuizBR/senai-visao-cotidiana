# Protocolo de avaliação

## Objetivo

Avaliar o YOLO26n pré-treinado no subconjunto COCO documentado
em dataset.md, sem treinamento ou ajuste dos pesos.

## Dados

- 196 imagens de val2017.
- 10 classes selecionadas.
- 1.431 anotações, incluindo 16 de multidões.
- Seleção reproduzível registrada em dataset_manifesto.json.
- Anotações originais preservadas.

## Configuração planejada da inferência

- Pesos: yolo26n.pt.
- Dispositivo: CPU.
- Tamanho de entrada: imgsz=640.
- Precisão: FP32, com half=False.
- Processamento de uma imagem por chamada.
- Confiança mínima para coleta das previsões: conf=0.001.
- IoU de NMS: iou=0.70, quando aplicável ao modo do modelo.
- Limite de detecções na inferência: max_det=300.
- Sem aumento de dados na inferência: augment=False.

A confiança baixa preserva previsões para construir a curva
precisão-revocação. Ela não representa o limiar escolhido para
a futura API.

A versão das bibliotecas, o hash dos pesos e os parâmetros
efetivamente utilizados serão registrados junto aos resultados.

## Associação das classes

Os IDs do modelo serão associados aos IDs COCO pelo nome da classe.
Não será presumida igualdade entre os identificadores numéricos.

A inferência será executada com as classes do modelo, e as previsões
serão filtradas para as 10 categorias antes do cálculo das métricas.

## Métricas

Será utilizado COCOeval com iouType="bbox", restrito aos IDs
das 196 imagens e das 10 categorias.

- AP médio em IoU de 0.50 a 0.95, com passo de 0.05.
- AP em IoU 0.50.
- AP em IoU 0.75.
- AP por classe.
- Average Recall com até 100 detecções por imagem e categoria.

Serão preservados os limites padrão de COCOeval: 1, 10 e 100
detecções por imagem e categoria.

As anotações iscrowd serão tratadas pelo avaliador oficial.
Não serão simplesmente removidas nem contadas como objetos
individuais comuns.

## Medição de tempo

- Carregar o modelo uma única vez.
- Realizar três chamadas de aquecimento antes da medição.
- Processar as imagens em ordem crescente de ID.
- Medir cada chamada predict com perf_counter.
- Informar média, mediana e percentil 95 dos tempos.

O tempo da chamada inclui leitura da imagem, pré-processamento,
inferência e pós-processamento. Exclui carregamento inicial do
modelo, escrita dos resultados e cálculo das métricas.

Essa medida não será apresentada como latência da API nem como
tempo exclusivo da rede neural.

## Limitações

- Subconjunto pequeno, com distribuição desigual entre classes.
- Resultados não equivalem ao desempenho no COCO completo.
- Benchmark conhecido no desenvolvimento dessa família de modelos.
- Ambiguidades nas referências registradas durante a inspeção.
- Resultados de tempo dependem do computador e de sua carga de trabalho.

Mudanças posteriores neste protocolo serão documentadas,
sem substituir silenciosamente os resultados anteriores.

## Situação atual

Primeira avaliação executada nas 196 imagens.

- mAP@0.50:0.95: 0.382974.
- mAP@0.50: 0.541002.
- AP@0.75: 0.408763.
- AR@100: 0.563370.
- Tempo médio da chamada predict: 128.32 ms.
- Mediana: 113.11 ms.
- Percentil 95: 196.60 ms.
- Previsões coletadas com conf=0.001: 20.465.

Métricas, configuração e mapeamento de classes estão registrados
em resultados/avaliacao_inicial/.

Os resultados se referem somente ao subconjunto selecionado.
AP não representa uma porcentagem simples de acertos.
O tempo medido não representa a latência da API.

Análise qualitativa concluída em seis exemplos, com registros
de detecções coerentes, omissões e ambiguidades das referências.
Nenhum parâmetro foi ajustado após a avaliação.

## Análise qualitativa das previsões

As previsões salvas foram comparadas às referências COCO,
utilizando confiança mínima de 0.25 apenas para visualização.
As métricas originais foram preservadas.

### Exemplos examinados

- book, imagem 89648: seis referências e nenhuma previsão da classe
  exibida acima do limiar visual. Possíveis candidatos abaixo desse
  limiar não aparecem no painel. A aparência dos materiais apresenta
  ambiguidades já registradas na inspeção das referências.
- chair, imagem 221708: quatro referências e três previsões
  visualmente próximas das cadeiras em primeiro plano. A cadeira
  mais encoberta ao fundo não teve previsão exibida.
- person, imagem 422998: previsão com confiança aproximada de 0.87,
  visualmente próxima da referência, com diferença na borda inferior.
- laptop, imagem 111609: previsão com confiança aproximada de 0.48
  e caixa visualmente próxima da referência, apesar do objeto
  parcialmente cortado pela borda.
- couch, imagem 293625: nenhuma previsão da classe exibida acima
  de 0.25. Há forte oclusão e dúvida previamente registrada sobre
  a extensão da caixa de referência.
- bottle, imagem 133244: nenhuma previsão da classe exibida acima
  de 0.25. O objeto anotado ocupa uma região muito pequena da imagem.

Foram examinadas seis comparações qualitativas. Os exemplos
ilustram acertos e omissões, mas não constituem uma classificação
completa dos erros das 196 imagens.

### Interpretação

Os exemplos ilustram omissões e uma detecção visualmente coerente.
A oclusão é uma hipótese de dificuldade no exemplo das cadeiras.

A inspeção é qualitativa: não substitui o pareamento por IoU do
COCOeval nem estabelece as causas do desempenho de toda uma classe.
O painel de cada exemplo mostra apenas a classe-alvo.

Nenhum peso ou parâmetro da avaliação foi alterado.

## Como reproduzir a avaliação

Execute os comandos na raiz do projeto.

### Pré-requisitos

- Dependências instaladas com `uv sync --locked`.
- Pesos `yolo26n.pt` na raiz do projeto.
- Subconjunto preparado e validado conforme `dataset.md`.
- Anotações em `data/processed/coco_cotidiano/annotations.json`.
- Imagens em `data/processed/coco_cotidiano/images/`.

### Executar

```powershell
uv run python scripts/avaliar_modelo.py
```

O script utiliza os parâmetros definidos em PARAMETROS e cria
uma nova pasta em runs/avaliacao a cada execução.

São registrados:

- configuracao.json: parâmetros, versões, hashes e IDs avaliados.
- mapeamento_classes.json: associação entre classes YOLO e COCO.
- previsoes.json: previsões utilizadas nas métricas.
- tempos.json: duração de cada chamada predict.
- metricas.json: métricas gerais, por classe e resumo dos tempos.

Os resultados locais não substituem automaticamente os registros
versionados em docs/resultados/avaliacao_inicial.

O tempo de processamento pode variar conforme o computador
e sua carga de trabalho. A reprodução deve considerar as versões,
os pesos, as anotações e os parâmetros registrados na execução.

### Comparar previsões e referências

Para visualizar a execução inicial, quando sua pasta local
estiver disponível:

```powershell
uv run python scripts/comparar_previsoes.py runs/avaliacao/20261021_175407_503006
```

Para outra execução, substitua o caminho pelo diretório informado
ao final da avaliação.

O script utiliza docs/amostra_inspecao.json e salva os painéis
na subpasta comparacoes da execução escolhida.

As referências aparecem à esquerda, em verde, e as previsões
à direita, em ciano. Cada painel apresenta somente a classe-alvo.

O limiar de 0,25 é aplicado apenas à visualização.
O script não executa novamente o detector nem recalcula as métricas.

### Compatibilidade do parâmetro de precisão

O script da avaliação inicial mantém half=False, conforme
o protocolo e a configuração registrados naquela execução.

A versão instalada emitiu um aviso de depreciação desse parâmetro.
Na API, ele foi substituído por quantize=None e a inferência
foi novamente verificada. O script e os registros da avaliação
inicial foram preservados.