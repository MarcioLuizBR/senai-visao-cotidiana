"""Baixa as imagens selecionadas e verifica sua leitura e dimensões."""

import json
import shutil
import time
from pathlib import Path
from urllib.request import urlopen

from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
PASTA_DATASET = RAIZ / "data/processed/coco_cotidiano"
ANOTACOES = PASTA_DATASET / "annotations.json"
PASTA_IMAGENS = PASTA_DATASET / "images"


def verificar_imagem(caminho, largura, altura):
    """Confere integridade, decodificação e dimensões da imagem."""
    with Image.open(caminho) as imagem:
        imagem.verify()

    # verify() não decodifica todos os pixels; reabrimos para testar load().
    with Image.open(caminho) as imagem:
        imagem.load()
        if imagem.size != (largura, altura):
            raise ValueError(
                f"Dimensões inesperadas: {imagem.size}; "
                f"esperado: {(largura, altura)}."
            )


def baixar_imagem(imagem):
    """Reutiliza arquivos válidos e tenta novamente em caso de falha."""
    nome = imagem["file_name"]

    # Aceita somente nomes simples, sem caminhos vindos dos metadados.
    if Path(nome).name != nome:
        raise ValueError(f"Nome de arquivo inválido: {nome}")

    destino = PASTA_IMAGENS / nome
    temporario = destino.with_suffix(".jpg.part")
    largura, altura = imagem["width"], imagem["height"]

    if destino.exists():
        try:
            verificar_imagem(destino, largura, altura)
            return "reutilizada"
        except (OSError, ValueError):
            # Um arquivo local inválido será substituído após novo download.
            pass

    # O nome vem das anotações oficiais; não baixamos o pacote completo.
    url = f"http://images.cocodataset.org/val2017/{nome}"

    for tentativa in range(1, 4):
        try:
            # O arquivo só recebe o nome definitivo depois de ser validado.
            with urlopen(url, timeout=60) as resposta:
                with temporario.open("wb") as arquivo:
                    shutil.copyfileobj(resposta, arquivo)

            verificar_imagem(temporario, largura, altura)
            temporario.replace(destino)
            return "baixada"

        except (OSError, ValueError) as erro:
            temporario.unlink(missing_ok=True)
            if tentativa == 3:
                raise RuntimeError(
                    f"Falha ao baixar ou validar {nome}: {erro}"
                ) from erro
            time.sleep(tentativa * 2)


def main():
    dados = json.loads(ANOTACOES.read_text(encoding="utf-8"))
    imagens = sorted(dados["images"], key=lambda item: item["id"])
    PASTA_IMAGENS.mkdir(parents=True, exist_ok=True)

    contagens = {"baixada": 0, "reutilizada": 0}
    falhas = []

    for numero, imagem in enumerate(imagens, start=1):
        try:
            situacao = baixar_imagem(imagem)
            contagens[situacao] += 1
            print(f"[{numero}/{len(imagens)}] {imagem['file_name']}: {situacao}")
        except (RuntimeError, ValueError) as erro:
            falhas.append({"image_id": imagem["id"], "error": str(erro)})
            print(f"[{numero}/{len(imagens)}] ERRO: {erro}")

    # O relatório diferencia download concluído de execução com falhas.
    relatorio = {
        "expected_images": len(imagens),
        "downloaded": contagens["baixada"],
        "reused": contagens["reutilizada"],
        "failures": falhas,
    }
    (PASTA_DATASET / "download_report.json").write_text(
        json.dumps(relatorio, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nEsperadas: {len(imagens)}")
    print(f"Baixadas: {contagens['baixada']}")
    print(f"Reutilizadas: {contagens['reutilizada']}")
    print(f"Falhas: {len(falhas)}")

    if falhas:
        raise SystemExit("Download incompleto. Execute novamente para retomar.")

    print("Todas as imagens foram verificadas com sucesso.")


if __name__ == "__main__":
    main()