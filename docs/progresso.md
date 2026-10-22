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

## Preparação do dataset COCO

- Selecionadas 196 imagens únicas para avaliação de 10 classes.
- Preservadas 1.431 anotações, incluindo 16 de multidões.
- Manifesto da seleção registrado na documentação.
- Baixadas e verificadas as 196 imagens, sem falhas.
- Dados volumosos mantidos localmente e ignorados pelo Git.
- Próximo passo: validar as anotações e preparar a avaliação.

## 21/10/2026 — Validação estrutural do dataset

- Script de validação criado e executado.
- Conferidas 196 imagens, 10 classes e 1.431 anotações.
- Preservadas 16 anotações de multidões.
- Resultado: zero erros e zero avisos.
- Próximo passo: inspecionar visualmente uma amostra das anotações
  e concluir a documentação dos termos de uso.

### Conclusão da preparação dos dados

- Inspecionados dez exemplos de referência, um por classe.
- Ambiguidades registradas, sem alterar as anotações originais.
- Documentados os termos gerais das anotações e das imagens.
- Licenças individuais serão conferidas para exemplos publicados.
- Preparação pronta para revisão e integração na develop.

## 21/10/2026 — Avaliação inicial do modelo

- Avaliadas 196 imagens em CPU com YOLO26n pré-treinado.
- mAP@0.50:0.95 de 0.382974 e mAP@0.50 de 0.541002.
- Tempo médio por chamada predict: 128.32 ms.
- Configuração, métricas e mapeamento de classes preservados.
- Inspecionadas seis comparações entre previsões e referências.
- Resultados e limitações documentados.
- Próximo passo: revisar e integrar a avaliação na develop.

## Primeira execução da API FastAPI

- Modelo carregado na inicialização por lifespan.
- Endpoint POST /detect recebe imagem por UploadFile.
- Inferência executada em CPU, com confiança mínima de 0.25.
- Resposta limitada às 10 classes do projeto.
- Teste pelo Swagger retornou HTTP 200 e JSON com 12 detecções.
- Resultado da imagem local coincidiu com o teste inicial do script.
- Tratamentos de arquivos inválidos e limites ainda aguardam testes.
- Aviso de depreciação do parâmetro half registrado para revisão.

## Validação manual da API

Testes realizados pelo Swagger no endpoint POST /detect:

- JPEG de escritório: HTTP 200, com 12 detecções.
- Arquivo de texto: HTTP 400, conteúdo inválido.
- Arquivo vazio: HTTP 400, arquivo vazio.
- Imagem GIF: HTTP 415, formato não permitido.
- Arquivo com 10.485.761 bytes: HTTP 413, limite de 10 MiB excedido.
- PNG com 20.005.000 pixels: HTTP 413, limite de pixels excedido.
- PNG branco de 640 × 480: HTTP 200, com detections vazio.

Todos os casos acima apresentaram o comportamento esperado.
Os arquivos utilizados nos testes permanecem em data/local,
fora do versionamento.

Pendências: documentar as respostas de erro no Swagger,
revisar o aviso do parâmetro half e documentar a execução da API.

## Atualização da documentação e configuração da API

- Respostas HTTP 400, 413 e 415 documentadas no Swagger.
- Modelo RespostaErro adicionado para descrever o campo detail.
- Parâmetro obsoleto half=False substituído por quantize=None,
  conforme a configuração disponível na versão instalada.
- Nova requisição com teste.jpg retornou HTTP 200.
- Aviso de depreciação de half ausente na nova requisição.

Pendência desta etapa: documentar como executar e utilizar a API.