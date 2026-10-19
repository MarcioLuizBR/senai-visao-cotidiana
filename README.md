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