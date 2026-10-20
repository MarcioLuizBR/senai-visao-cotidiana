# Registro de progresso

## 19/10/2026 — Configuração inicial

### Concluído

- Repositório criado e clonado no computador.
- Branch develop criada e publicada.
- Branch feature/project-setup criada e publicada.
- Projeto inicializado com uv.
- Python 3.11 fixado em .python-version.
- Ambiente .venv criado e execução verificada.
- Configuração registrada no commit 7933691.

### Decisões

- Trabalho individual.
- Desenvolvimento e execução no computador pessoal.
- Ambiente e dependências gerenciados pelo uv.
- Modelo inicial planejado: YOLO26n pré-treinado.
- Fine-tuning opcional após concluir a entrega principal.
- Código com comentários explicativos em português.
- Vídeo produzido em etapa própria, com edição no CapCut Desktop.

### Pendências


- Selecionar dataset e pelo menos 10 classes.
- Verificar origem, licença e anotações dos dados.
- Instalar e testar as dependências de inferência.

### Concluído

- Quadro Kanban criado no Trello e vinculado no README.
- Escopo inicial documentado.

### Próximo passo

Concluir a documentação inicial e revisar a etapa antes
da integração na develop.

## 20/10/2026 — Primeira inferência em CPU

### Concluído

- Dependências de inferência instaladas e importações verificadas.
- PyTorch 2.14.1+cpu, Torchvision 0.29.1+cpu e Ultralytics 8.4.183.
- Script scripts/primeira_deteccao.py criado com comentários explicativos.
- YOLO26n pré-treinado executado em CPU sobre uma imagem local.
- Retorno JSON com classe, confiança e bounding box verificado.
- Teste inicial produziu 12 detecções de 9 classes distintas.

### Limitações

- Teste funcional em uma única imagem.
- Detecções ainda não conferidas visualmente.
- Resultado não representa a avaliação do dataset nem comprova acurácia.

### Próximo passo

Conferir visualmente as detecções e selecionar o dataset de avaliação
com pelo menos 10 classes.

### Inspeção visual da primeira inferência

- Imagem com bounding boxes salva localmente em runs/primeira_deteccao.
- Identificações visualmente coerentes para cadeiras, pessoa, notebook,
  sofá, mesa, vasos, caneca e livros.
- Possível confusão entre um recipiente alto e a classe cup.
- Observadas detecções plausíveis com confiança inferior a 0.50.
- Limiar mantido em 0.25, sem ajuste baseado apenas nesta imagem.
- Inspeção qualitativa; não foram calculadas métricas de acurácia ou mAP.