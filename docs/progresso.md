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

## Documentação de utilização da API

- Criado docs/api.md com preparação, execução, endpoints,
  classes, limites, respostas HTTP e limitações.
- Exemplo de upload por curl.exe executado com sucesso:
  retorno JSON com as mesmas 12 detecções da imagem de escritório.

## Testes automatizados — validação de entrada

- Adicionadas as dependências de desenvolvimento pytest e httpx2.
- Criado tests/test_api.py com oito casos aprovados:
  disponibilidade, ausência do arquivo obrigatório, arquivo vazio,
  texto, JPEG falso, GIF e limites de bytes e pixels.
- Utilizado modelo simulado para evitar carregar pesos e executar
  inferência nestes testes.
- O modelo simulado gera uma falha caso uma entrada inválida
  chegue à inferência.
- Limites reduzidos temporariamente nos testes automatizados;
  os limites reais também foram verificados manualmente.
- Execução: uv run python -m pytest tests/test_api.py -v
- Resultado: 8 passed, sem avisos.

## Testes automatizados — respostas de sucesso

- Adicionados casos de JPEG e PNG válidos com lista vazia.
- Verificados formato do JSON, arredondamento e filtragem de classes.
- Resultado do conjunto completo: 11 passed, sem avisos.
- Instruções de execução registradas em docs/api.md.

## Consolidação da documentação e dependências

- README atualizado com instalação, API, dataset, métricas,
  testes e limitações.
- requirements.txt exportado do uv.lock, sem dependências
  de desenvolvimento e com hashes preservados.
- Índice adicional do PyTorch incluído para localizar
  as distribuições de CPU.
- Verificação com uv pip install --dry-run --require-hashes
  --index-strategy unsafe-best-match -r requirements.txt:
  requisitos satisfeitos, sem alterações no ambiente atual.
- Instalação do zero pelo requirements.txt ainda não verificada.
- uv sync --locked permanece como instalação principal.

## Instruções de reprodução

- Documentada a sequência de obtenção das anotações, seleção,
  download e validação do subconjunto COCO.
- Documentados os comandos de avaliação e comparação visual.
- Corrigida a indicação desatualizada de avaliação pendente.
- Caminhos e argumentos conferidos nos scripts.
- Nesta revisão documental, o processo completo não foi reexecutado.

## Conferência do escopo acadêmico

- Enunciado e transcrição da orientação conferidos.
- Confirmada a permissão para usar pesos pré-treinados,
  sem fine-tuning, e demonstrar a API localmente.
- Confirmado que um modelo é suficiente para o trabalho individual.
- Justificativa da escolha do YOLO26n incluída no README.
- Mantidos os requisitos de dez classes, demonstração dos testes,
  FastAPI, JSON, Kanban, GitHub e vídeo de até sete minutos.

## Conferência de acesso ao Trello

- Professor identificado como membro do quadro.
- Compartilhamento realizado em 19/10/2026, conforme registro do autor.
- Acesso público verificado em janela anônima, sem login.

## Preparação das comparações para o vídeo

- Criado docs/amostra_video.json com dez exemplos por classe,
  distribuídos em seis imagens únicas.
- Script comparar_previsoes.py ampliado com argumentos
  --amostra e --pasta-saida.
- Dez painéis gerados em comparacoes_video, utilizando
  previsões salvas e limiar visual de 0,25.
- Métricas e amostra original preservadas.
- Inspeção dos novos painéis e conferência dos créditos pendentes.

## Créditos das imagens da apresentação

- Registradas as fontes das seis fotografias selecionadas.
- Autoria identificada para três imagens.
- Três páginas de origem ficaram inacessíveis na consulta.
- Licenças registradas conforme os metadados COCO,
  sem reconfirmação nas páginas individuais.
- Conferência de créditos permanece parcial.

## 23/10/2026 — Preparação da entrega final

- Narração gravada com voz do autor.
- Vídeo editado no CapCut e exportado com aproximadamente 6min38s.
- Incluídas demonstração da API, validação do dataset,
  métricas, comparações visuais, testes, Trello e histórico Git.
- Créditos das imagens incluídos no encerramento.
- Vídeo enviado ao Google Drive e link registrado no README.
- Pendente integração final na main e submissão no ambiente do curso.