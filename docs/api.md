# API de detecção — Visão Cotidiana

## Objetivo

Disponibilizar o modelo pré-treinado YOLO26n por meio de uma API
FastAPI. A aplicação recebe uma imagem e retorna as detecções em JSON.

O modelo é carregado uma vez por processo durante a inicialização.
A inferência utiliza CPU, com confiança mínima de 0,25.
Um bloqueio serializa o acesso ao modelo compartilhado.

## Classes retornadas

person, chair, couch, potted plant, dining table, laptop, cup,
bottle, book e cell phone.

O modelo mantém suas classes originais, mas a API retorna apenas
as dez classes selecionadas para o projeto.

## Preparação

Execute os comandos na raiz do repositório.

Instale as dependências usando o ambiente gerenciado pelo uv:

```powershell
uv sync --locked
```

O arquivo de pesos `yolo26n.pt` deve estar na raiz do projeto.
Ele não é versionado no Git.

Caso ainda não esteja disponível, execute o script de primeira
detecção com uma imagem local válida. Na primeira execução,
o Ultralytics baixa os pesos, exigindo conexão com a internet:

```powershell
uv run python scripts/primeira_deteccao.py data/local/teste.jpg
```

## Iniciar o servidor

```powershell
uv run uvicorn main:app --reload
```

A opção `--reload` recarrega a aplicação quando o código é alterado
e destina-se ao desenvolvimento local.

- Swagger: http://127.0.0.1:8000/docs
- Disponibilidade: http://127.0.0.1:8000/health

Para encerrar, pressione `Ctrl+C` no terminal do servidor.

## GET /health

Retorna uma resposta simples de disponibilidade:

```json
{
  "status": "ok"
}
```

Esse endpoint não executa uma inferência.

## POST /detect

Recebe um arquivo no campo obrigatório `file`, usando
`multipart/form-data`.

### Limites

- Formatos aceitos: JPEG e PNG.
- Tamanho máximo do arquivo: 10 MiB, equivalentes a 10.485.760 bytes.
- Quantidade máxima de pixels: 20.000.000, calculada por largura × altura.

A aplicação verifica o conteúdo real do arquivo, sem confiar
apenas na extensão ou no tipo MIME informado.

O limite de bytes é verificado após o processamento do upload
pelo framework; não representa um bloqueio de rede antes do
recebimento do arquivo.

### Envio pelo Swagger

1. Acesse http://127.0.0.1:8000/docs.
2. Expanda `POST /detect`.
3. Clique em `Try it out`.
4. Selecione uma imagem JPEG ou PNG.
5. Clique em `Execute`.
6. Confira o código HTTP e o corpo da resposta.

### Envio pelo PowerShell

Com o servidor rodando, execute em outro terminal:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/detect" -F "file=@data/local/teste.jpg"
```

### Resposta de sucesso

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

As coordenadas são expressas em pixels na imagem após a correção
de orientação EXIF. A origem fica no canto superior esquerdo:
x cresce para a direita e y cresce para baixo.

A confiança é uma pontuação do modelo, não uma garantia de acerto.

Quando nenhuma detecção das classes selecionadas atinge o limiar,
a API também retorna HTTP 200:

```json
{
  "status": "success",
  "detections": []
}
```

## Respostas HTTP

| Código | Significado |
|---|---|
| 200 | Imagem processada, com ou sem detecções. |
| 400 | Arquivo vazio, conteúdo inválido ou imagem corrompida. |
| 413 | Limite de bytes ou de pixels excedido. |
| 415 | Formato de imagem diferente de JPEG ou PNG. |
| 422 | Requisição incompatível com o contrato, como ausência do campo file. |

Os erros tratados pela aplicação utilizam o campo `detail`:

```json
{
  "detail": "O arquivo está vazio."
}
```

A resposta 422 é gerada pelo FastAPI e pode apresentar uma lista
de detalhes de validação.

## Validação manual realizada

| Entrada | Resultado observado |
|---|---|
| JPEG de escritório | HTTP 200, com 12 detecções. |
| Arquivo de texto | HTTP 400. |
| Arquivo vazio | HTTP 400. |
| Imagem GIF | HTTP 415. |
| Arquivo com 10.485.761 bytes | HTTP 413. |
| PNG com 20.005.000 pixels | HTTP 413. |
| PNG branco de 640 × 480 | HTTP 200, com lista vazia. |

Esses testes verificam casos funcionais da API. Não substituem
a avaliação quantitativa do detector, descrita em `avaliacao.md`.

## Limitações

- O modelo pode omitir objetos ou produzir falsos positivos.
- A API processa imagens estáticas; não oferece processamento de vídeo.
- O acesso ao modelo é serializado, limitando a capacidade simultânea.
- A aplicação foi preparada para demonstração acadêmica local.
- As imagens recebidas e as previsões não são salvas pelo código da API.