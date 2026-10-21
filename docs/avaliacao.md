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

Análise de erros ainda pendente, com atenção inicial às classes
book e chair. Nenhum parâmetro foi ajustado após esta avaliação.

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

### Interpretação

Os exemplos ilustram omissões e uma detecção visualmente coerente.
A oclusão é uma hipótese de dificuldade no exemplo das cadeiras.

A inspeção é qualitativa: não substitui o pareamento por IoU do
COCOeval nem estabelece as causas do desempenho de toda uma classe.
O painel de cada exemplo mostra apenas a classe-alvo.

Nenhum peso ou parâmetro da avaliação foi alterado.