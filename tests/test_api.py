"""Testes do contrato HTTP e das validações de entrada da API."""

from io import BytesIO

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