"""API acadêmica de detecção de objetos com YOLO26n e FastAPI."""

from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path
from threading import Lock
from typing import Annotated, Literal

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from pydantic import BaseModel, Field
from ultralytics import YOLO

RAIZ = Path(__file__).resolve().parent
PESOS = RAIZ / "yolo26n.pt"

# Limites da aplicação: 10 MiB por arquivo e 20 milhões de pixels.
MAX_BYTES = 10 * 1024 * 1024
MAX_PIXELS = 20_000_000
CONFIANCA = 0.25

CLASSES = {
    "person", "chair", "couch", "potted plant", "dining table",
    "laptop", "cup", "bottle", "book", "cell phone",
}


# Os modelos Pydantic documentam e validam o contrato de resposta.
class BoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float


class Deteccao(BaseModel):
    class_name: str
    confidence: float = Field(ge=0, le=1)
    box: BoundingBox


class RespostaDeteccao(BaseModel):
    status: Literal["success"] = "success"
    detections: list[Deteccao]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Carrega uma vez por processo do servidor, antes das requisições.
    # Exige os pesos locais já utilizados na avaliação.
    if not PESOS.is_file():
        raise RuntimeError(f"Pesos não encontrados: {PESOS}")

    modelo = YOLO(str(PESOS))
    nomes_disponiveis = set(modelo.names.values())
    if not CLASSES.issubset(nomes_disponiveis):
        raise RuntimeError("O modelo não contém todas as 10 classes esperadas.")

    app.state.modelo = modelo

    # Serializa o acesso ao modelo compartilhado entre requisições.
    app.state.inferencia_lock = Lock()
    try:
        yield
    finally:
        del app.state.modelo


app = FastAPI(
    title="Visão Cotidiana",
    description="Detecção de 10 classes de objetos em imagens JPEG ou PNG.",
    version="0.1.0",
    lifespan=lifespan,
)


def carregar_imagem(conteudo: bytes) -> Image.Image:
    """Valida o conteúdo real e prepara uma imagem RGB em memória."""
    try:
        with Image.open(BytesIO(conteudo)) as original:
            if original.format not in {"JPEG", "PNG"}:
                raise HTTPException(
                    status_code=415, detail="Envie uma imagem JPEG ou PNG."
                )

            if original.width * original.height > MAX_PIXELS:
                raise HTTPException(
                    status_code=413,
                    detail="A imagem excede o limite de 20 milhões de pixels.",
                )

            original.verify()

        # Reabre após verify(), decodifica os pixels e corrige a orientação.
        with Image.open(BytesIO(conteudo)) as original:
            original.load()
            return ImageOps.exif_transpose(original).convert("RGB")

    except Image.DecompressionBombError as erro:
        raise HTTPException(
            status_code=413, detail="Dimensões da imagem excedem o limite."
        ) from erro
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as erro:
        raise HTTPException(
            status_code=400, detail="Arquivo inválido ou imagem corrompida."
        ) from erro


@app.get("/health", summary="Verificar disponibilidade")
def health():
    return {"status": "ok"}


@app.post(
    "/detect",
    response_model=RespostaDeteccao,
    summary="Detectar objetos em uma imagem",
)
def detectar(
    request: Request,
    file: Annotated[UploadFile, File(description="Imagem JPEG ou PNG")],
):
    # Endpoint síncrono: o FastAPI executa a rotina em uma thread.
    # Lê até o limite + 1 para identificar arquivos grandes sem carregar
    # todo o conteúdo do upload na memória da aplicação.
    try:
        conteudo = file.file.read(MAX_BYTES + 1)
    finally:
        file.file.close()

    if not conteudo:
        raise HTTPException(status_code=400, detail="O arquivo está vazio.")
    if len(conteudo) > MAX_BYTES:
        raise HTTPException(
            status_code=413, detail="O arquivo excede o limite de 10 MiB."
        )

    # A validação usa o conteúdo, sem confiar apenas na extensão ou MIME.
    imagem = carregar_imagem(conteudo)

    try:
        with request.app.state.inferencia_lock:
            resultado = request.app.state.modelo.predict(
                source=imagem,
                device="cpu",
                imgsz=640,
                conf=CONFIANCA,
                half=False,
                max_det=300,
                augment=False,
                save=False,
                verbose=False,
            )[0]

            deteccoes = []
            for caixa in resultado.boxes:
                nome = resultado.names[int(caixa.cls.item())]
                if nome not in CLASSES:
                    continue

                x_min, y_min, x_max, y_max = caixa.xyxy[0].tolist()
                deteccoes.append(
                    Deteccao(
                        class_name=nome,
                        confidence=round(float(caixa.conf.item()), 4),
                        box=BoundingBox(
                            x_min=round(x_min, 2),
                            y_min=round(y_min, 2),
                            x_max=round(x_max, 2),
                            y_max=round(y_max, 2),
                        ),
                    )
                )
    finally:
        imagem.close()

    # Nenhum objeto reconhecido é uma resposta válida, com lista vazia.
    return RespostaDeteccao(detections=deteccoes)