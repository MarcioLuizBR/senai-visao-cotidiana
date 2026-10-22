# Visão Cotidiana

API de detecção de objetos em imagens, desenvolvida como projeto
acadêmico individual do curso de Machine Learning e Visão
Computacional do SENAI.

Utiliza YOLO26n pré-treinado, FastAPI e execução em CPU.
O ambiente e as dependências são gerenciados pelo uv.

## Objetivo

Receber uma imagem e retornar as detecções em JSON, contendo:

- Nome da classe.
- Pontuação de confiança.
- Coordenadas da caixa delimitadora em pixels.

O projeto utiliza pesos pré-treinados, sem fine-tuning.
O foco está na avaliação do detector, integração com a API,
validação das entradas e documentação dos resultados.

## Classes do projeto

| Classe do modelo | Tradução |
|---|---|
| person | Pessoa |
| chair | Cadeira |
| couch | Sofá |
| potted plant | Planta em vaso |
| dining table | Mesa de jantar |
| laptop | Notebook |
| cup | Xícara ou copo |
| bottle | Garrafa |
| book | Livro |
| cell phone | Celular |

Os nomes retornados pela API permanecem em inglês.
A API filtra as previsões para essas dez classes.

## Escolha do modelo e escopo acadêmico

Foi escolhido o YOLO26n pré-treinado, variante compacta,
para viabilizar a execução local em CPU no computador disponível.
Suas classes incluem os dez objetos selecionados para o projeto.

A escolha priorizou a viabilidade de execução, a integração
com FastAPI e a avaliação documentada. Não foi realizado
benchmark entre arquiteturas; portanto, não se afirma que
esse seja o melhor modelo para todos os cenários.

Conforme esclarecimento do professor na aula de orientação
(8:28–8:44 e 50:16–50:24), o uso de pesos pré-treinados é permitido
e o fine-tuning é opcional.

Na mesma orientação, a hospedagem online foi dispensada
(23:12–24:24). Como o trabalho é individual, utiliza-se um modelo,
conforme explicado em 25:48–26:04.


## Tecnologias

- Python 3.11.
- uv e ambiente virtual .venv.
- Ultralytics YOLO26n.
- PyTorch e Torchvision com distribuições de CPU.
- FastAPI, Uvicorn e python-multipart.
- pycocotools para avaliação no formato COCO.
- pytest e httpx2 para testes automatizados.

As versões resolvidas das dependências estão registradas no uv.lock.

## Instalação

Pré-requisitos: Git e uv instalados, acesso à internet para obter
as dependências e os pesos do modelo.

No PowerShell:

```powershell
git clone https://github.com/MarcioLuizBR/senai-visao-cotidiana.git
cd senai-visao-cotidiana
uv sync --locked
```

O uv utiliza a versão de Python indicada em .python-version
e cria o ambiente virtual .venv.

A ativação manual é opcional quando os comandos usam uv run.
Para ativar no PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Obter os pesos e executar a primeira detecção

Coloque uma imagem JPEG válida em data/local/teste.jpg.
Crie a pasta data/local caso ainda não exista.

Execute:

```powershell
uv run python scripts/primeira_deteccao.py data/local/teste.jpg
```

Na primeira execução, o Ultralytics baixa yolo26n.pt.
O arquivo deve permanecer na raiz do projeto para iniciar a API.

Pesos, imagens locais e saídas de execução não são versionados.

## Executar a API

Na raiz do projeto:

```powershell
uv run uvicorn main:app --reload
```

Acesse:

- Swagger: http://127.0.0.1:8000/docs
- Disponibilidade: http://127.0.0.1:8000/health

No Swagger, abra POST /detect, clique em Try it out,
selecione uma imagem e clique em Execute.

Alternativamente, em outro terminal:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/detect" -F "file=@data/local/teste.jpg"
```

Para encerrar o servidor, pressione Ctrl+C.

A opção --reload é destinada ao desenvolvimento local.

## Exemplo de resposta

Exemplo ilustrativo com uma detecção:

```json
{
  "status": "success",
  "detections": [
    {
      "class_name": "chair",
      "confidence": 0.9376,
      "box": {
        "x_min": 852.18,
        "y_min": 323.75,
        "x_max": 1206.51,
        "y_max": 767.46
      }
    }
  ]
}
```

As coordenadas correspondem à imagem após a correção de orientação
EXIF. A origem fica no canto superior esquerdo.

Uma imagem processada sem detecções retorna HTTP 200 com
"detections": [].

## Validações da API

- Formatos permitidos: JPEG e PNG.
- Tamanho máximo do arquivo: 10 MiB, ou 10.485.760 bytes.
- Quantidade máxima de pixels: 20.000.000.
- Verificação do conteúdo real do arquivo.
- Confiança mínima de detecção: 0,25.
- Inferência em CPU, com acesso serializado ao modelo compartilhado.

| HTTP | Significado |
|---|---|
| 200 | Imagem processada, com ou sem detecções. |
| 400 | Arquivo vazio, inválido ou imagem corrompida. |
| 413 | Limite de bytes ou pixels excedido. |
| 415 | Formato de imagem não permitido. |
| 422 | Requisição incompatível com o contrato da API. |

Detalhes e exemplos estão na [documentação da API](docs/api.md).

## Dataset de avaliação

Foi selecionado um subconjunto do COCO val2017:

- 196 imagens únicas.
- 10 classes.
- 1.431 anotações preservadas.
- 1.415 anotações de objetos sem multidões.
- 16 anotações de multidões, preservadas para a avaliação COCO.

A seleção utiliza semente 42 e combina amostras por classe.
Como uma imagem pode conter várias classes, as contagens
de imagens por classe se sobrepõem.

As imagens não são distribuídas no repositório.
O procedimento de preparação, as fontes e as condições de uso
estão em [Dataset de avaliação](docs/dataset.md).

## Resultados da avaliação inicial

Modelo YOLO26n pré-treinado, executado em CPU, com entrada
configurada em imgsz=640 e confiança mínima de 0,001 para
a avaliação quantitativa.

Esse limiar é diferente do utilizado na API, pois a avaliação
considera previsões com baixa confiança para calcular as métricas.

| Métrica | Resultado |
|---|---|
| AP@[0,50:0,95] | 0,3830 |
| AP@0,50 | 0,5410 |
| AP@0,75 | 0,4088 |
| AR@100 | 0,5634 |
| Tempo médio por imagem | 128,32 ms |
| Tempo mediano por imagem | 113,11 ms |
| Percentil 95 do tempo | 196,60 ms |

Os tempos correspondem à chamada de predição no protocolo
documentado, não à latência HTTP da API.

AP não representa uma porcentagem simples de acertos.
Os resultados descrevem somente o subconjunto selecionado
e não equivalem à avaliação completa do COCO.

O protocolo, os resultados por classe e a análise qualitativa
estão em [Avaliação do modelo](docs/avaliacao.md).

Os registros da execução estão em
[Resultados da avaliação inicial](docs/resultados/avaliacao_inicial).

## Testes

Execute na raiz do projeto:

```powershell
uv run python -m pytest tests/test_api.py -v
```

Resultado verificado: 11 testes aprovados, sem avisos.

Os testes utilizam inferência simulada para verificar o contrato
HTTP, validações, serialização, arredondamento e filtragem
das classes. Não exigem os pesos do YOLO nem um servidor Uvicorn.

Também foram realizados testes manuais com o modelo real
pelo Swagger e pelo curl.exe.

## Estrutura principal

- main.py: aplicação FastAPI e validação das imagens.
- scripts/: preparação dos dados, inferência e avaliação.
- tests/test_api.py: testes automatizados da API.
- docs/dataset.md: preparação, fontes e condições de uso dos dados.
- docs/avaliacao.md: protocolo e resultados da avaliação.
- docs/api.md: execução e utilização da API.
- docs/progresso.md: histórico de decisões e desenvolvimento.
- docs/resultados/: registros versionados da avaliação inicial.
- pyproject.toml e uv.lock: configuração e dependências.

## Limitações

- Objetos pequenos, parcialmente visíveis ou ocluídos podem ser omitidos.
- O detector pode produzir falsos positivos.
- A confiança retornada não garante que a classe esteja correta.
- O subconjunto de avaliação não comprova desempenho em novos cenários.
- O uso de um benchmark associado ao treinamento dos pesos limita
  conclusões sobre generalização.
- A API processa imagens estáticas e foi preparada para demonstração local.
- Não foram realizados testes de carga ou implantação em produção.

## Organização do desenvolvimento

- main: versão final integrada para entrega.
- develop: integração das etapas revisadas.
- feature/*: implementação e testes.
- docs/*: consolidação da documentação.

As etapas são registradas com commits e pull requests.

O planejamento está no
[quadro Kanban do Trello](https://trello.com/b/Evdfm58f/senai-visao-cotidiana).

O histórico está no [Registro de progresso](docs/progresso.md).


## Arquivo requirements.txt

O requirements.txt contém as dependências de execução exportadas
do uv.lock, com versões fixadas e hashes. Não inclui o grupo
de desenvolvimento utilizado nos testes.

O índice adicional do PyTorch foi acrescentado para disponibilizar
as distribuições de CPU. As condições de plataforma selecionam
as versões aplicáveis ao sistema operacional.

A instalação principal do projeto continua sendo:

```powershell
uv sync --locked
```

O requirements.txt é fornecido como formato complementar.
Ele não preserva a associação exclusiva entre pacotes e índices
definida no pyproject.toml.

## Autor

Márcio Luiz