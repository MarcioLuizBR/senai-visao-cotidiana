# Visão Cotidiana

API de detecção de objetos em imagens, desenvolvida como projeto
acadêmico do curso de Machine Learning e Visão Computacional do SENAI.

## Objetivo

Receber uma imagem por uma API FastAPI e retornar as detecções em
formato JSON, contendo nome da classe, confiança e coordenadas
da caixa delimitadora (bounding box).

## Escopo planejado

- Utilizar o modelo YOLO26n com pesos pré-treinados.
- Selecionar um dataset de avaliação com pelo menos 10 classes
  compatíveis com o modelo.
- Avaliar detecções, tempo de processamento e limitações.
- Implementar o endpoint POST /detect para upload de imagens.
- Documentar a instalação, a execução e os resultados.
- Organizar as tarefas em um quadro Kanban no Trello.
- Registrar o desenvolvimento com branches e commits por etapa.
- Apresentar o projeto em um vídeo de até 7 minutos.

O fine-tuning é uma extensão opcional, conforme esclarecimento
do professor na aula de orientação do projeto. A entrega principal
utilizará pesos pré-treinados, com foco na avaliação e integração.

## Tecnologias

- Python 3.11
- uv para gerenciamento do ambiente e das dependências
- Ultralytics YOLO26n — integração planejada
- FastAPI — integração planejada

## Ambiente de desenvolvimento

Após clonar o repositório, execute:

```powershell
uv sync
```

Para verificar o Python utilizado:

```powershell
uv run python --version
```

O ambiente virtual fica na pasta `.venv` e não deve ser versionado.

As dependências de detecção e da API serão adicionadas nas próximas etapas.

## Organização do desenvolvimento

- `main`: versão final integrada.
- `develop`: integração das etapas revisadas.
- `feature/*`: desenvolvimento de cada tarefa.

## Planejamento

As tarefas são organizadas no
[quadro Kanban do Trello](https://trello.com/b/Evdfm58f/senai-visao-cotidiana).

O histórico de decisões e pendências está em
[Registro de progresso](docs/progresso.md).

## Situação atual

Ambiente Python configurado com uv.
Seleção do dataset e implementação ainda não iniciadas.

## Autor

Márcio Luiz