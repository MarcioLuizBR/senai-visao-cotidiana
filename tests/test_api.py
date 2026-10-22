"""Testes do contrato HTTP e das validações de entrada da API."""

from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from PIL import Image

import main


@pytest.fixture
def cliente(monkeypatch, tmp_path):
    """Inicializa a API sem carregar pesos reais do YOLO."""

    class ModeloSimulado:
        # Disponibiliza as classes esperadas pela inicialização da API.
        names = dict(enumerate(sorted(main.CLASSES)))

        def predict(self, **kwargs):
            # Os casos deste primeiro grupo não devem executar inferência.
            raise AssertionError("Entrada inválida chegou à inferência.")

    # Um arquivo temporário satisfaz a verificação de existência dos pesos.
    pesos = tmp_path / "modelo.pt"
    pesos.touch()
    monkeypatch.setattr(main, "PESOS", pesos)

    # Substitui o construtor apenas durante este teste.
    # O monkeypatch restaura os valores originais automaticamente.
    monkeypatch.setattr(main, "YOLO", lambda caminho: ModeloSimulado())

    # O contexto executa a inicialização e o encerramento da aplicação.
    with TestClient(main.app) as client:
        yield client


def criar_imagem(formato, tamanho=(32, 32)):
    """Produz uma imagem em memória, sem arquivos de teste no repositório."""
    with BytesIO() as buffer:
        with Image.new("RGB", tamanho, "white") as imagem:
            imagem.save(buffer, format=formato)
        return buffer.getvalue()


def test_health(cliente):
    resposta = cliente.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_arquivo_obrigatorio(cliente):
    resposta = cliente.post("/detect")

    assert resposta.status_code == 422
    # Confirma que a validação aponta para o campo obrigatório file.
    assert any(
        erro["loc"] == ["body", "file"]
        for erro in resposta.json()["detail"]
    )


@pytest.mark.parametrize(
    "nome,conteudo,mime,status,mensagem",
    [
        (
            "vazio.jpg",
            b"",
            "image/jpeg",
            400,
            "O arquivo está vazio.",
        ),
        (
            "texto.txt",
            b"Isto nao e uma imagem.",
            "text/plain",
            400,
            "Arquivo inválido ou imagem corrompida.",
        ),
        (
            # Declarar JPEG não transforma texto em imagem.
            "falso.jpg",
            b"Isto tambem nao e uma imagem.",
            "image/jpeg",
            400,
            "Arquivo inválido ou imagem corrompida.",
        ),
        (
            "imagem.gif",
            criar_imagem("GIF"),
            "image/gif",
            415,
            "Envie uma imagem JPEG ou PNG.",
        ),
    ],
    ids=["vazio", "texto", "jpeg-falso", "gif"],
)
def test_rejeitar_entrada_invalida(
    cliente, nome, conteudo, mime, status, mensagem
):
    resposta = cliente.post(
        "/detect",
        files={"file": (nome, conteudo, mime)},
    )

    assert resposta.status_code == status
    assert resposta.json() == {"detail": mensagem}


def test_limite_de_bytes(cliente, monkeypatch):
    # Reduz o limite neste teste para exercitar a rejeição sem criar
    # um arquivo de mais de 10 MiB a cada execução.
    monkeypatch.setattr(main, "MAX_BYTES", 100)

    resposta = cliente.post(
        "/detect",
        files={"file": ("grande.jpg", b"0" * 101, "image/jpeg")},
    )

    assert resposta.status_code == 413
    assert resposta.json() == {
        "detail": "O arquivo excede o limite de 10 MiB."
    }


def test_limite_de_pixels(cliente, monkeypatch):
    # Uma imagem pequena ultrapassa o limite temporário deste teste.
    # O limite real já foi verificado manualmente pelo Swagger.
    monkeypatch.setattr(main, "MAX_PIXELS", 100)

    resposta = cliente.post(
        "/detect",
        files={
            "file": (
                "muitos_pixels.png",
                criar_imagem("PNG", tamanho=(11, 10)),
                "image/png",
            )
        },
    )

    assert resposta.status_code == 413
    assert resposta.json() == {
        "detail": "A imagem excede o limite de 20 milhões de pixels."
    }



@pytest.fixture
def cliente_inferencia(monkeypatch, tmp_path):
    """Disponibiliza uma inferência controlada para testar o JSON da API."""
    modelo = Mock()
    modelo.names = dict(enumerate(sorted(main.CLASSES)))

    # Por padrão, simula uma imagem processada sem objetos detectados.
    modelo.predict.return_value = [
        SimpleNamespace(boxes=[], names=modelo.names)
    ]

    pesos = tmp_path / "modelo.pt"
    pesos.touch()
    monkeypatch.setattr(main, "PESOS", pesos)
    monkeypatch.setattr(main, "YOLO", lambda caminho: modelo)

    with TestClient(main.app) as client:
        yield client, modelo


def criar_caixa(classe, confianca, coordenadas):
    """Simula apenas os métodos de uma caixa utilizados pela API."""
    return SimpleNamespace(
        cls=SimpleNamespace(item=lambda: classe),
        conf=SimpleNamespace(item=lambda: confianca),
        xyxy=[SimpleNamespace(tolist=lambda: coordenadas)],
    )


@pytest.mark.parametrize(
    "formato,mime",
    [("JPEG", "image/jpeg"), ("PNG", "image/png")],
)
def test_imagem_valida_sem_deteccoes(cliente_inferencia, formato, mime):
    cliente, modelo = cliente_inferencia

    resposta = cliente.post(
        "/detect",
        files={
            "file": (
                f"imagem.{formato.lower()}",
                criar_imagem(formato),
                mime,
            )
        },
    )

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "success", "detections": []}
    modelo.predict.assert_called_once()


def test_serializar_deteccao_e_filtrar_classes(cliente_inferencia):
    cliente, modelo = cliente_inferencia

    # A inferência simulada inclui uma classe do projeto e outra fora dele.
    # Assim verificamos se a API filtra o resultado antes de responder.
    modelo.predict.return_value = [
        SimpleNamespace(
            names={0: "chair", 1: "car"},
            boxes=[
                criar_caixa(0, 0.912345, [1.234, 2.346, 20.567, 30.789]),
                criar_caixa(1, 0.99, [0.0, 0.0, 10.0, 10.0]),
            ],
        )
    ]

    resposta = cliente.post(
        "/detect",
        files={"file": ("imagem.png", criar_imagem("PNG"), "image/png")},
    )

    assert resposta.status_code == 200
    assert resposta.json() == {
        "status": "success",
        "detections": [
            {
                "class_name": "chair",
                "confidence": 0.9123,
                "box": {
                    "x_min": 1.23,
                    "y_min": 2.35,
                    "x_max": 20.57,
                    "y_max": 30.79,
                },
            }
        ],
    }
    modelo.predict.assert_called_once()