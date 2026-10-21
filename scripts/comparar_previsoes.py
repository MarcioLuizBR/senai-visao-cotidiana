"""Compara referências COCO e previsões salvas, uma classe por exemplo."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parents[1]
DATASET = RAIZ / "data/processed/coco_cotidiano"
LIMIAR_VISUAL = 0.25


def desenhar(imagem, anotacoes, nome, cor, previsao=False):
    """Desenha caixas COCO [x, y, largura, altura] em uma cópia."""
    painel = imagem.copy()
    desenho = ImageDraw.Draw(painel)

    for item in anotacoes:
        x, y, largura, altura = item["bbox"]
        rotulo = nome

        if previsao:
            rotulo += f" {item['score']:.2f}"
        elif item.get("iscrowd", 0):
            rotulo += " [iscrowd]"

        desenho.rectangle(
            [x, y, x + largura, y + altura],
            outline=cor,
            width=3,
        )
        posicao = (max(0, x), max(0, y))
        desenho.rectangle(desenho.textbbox(posicao, rotulo), fill="black")
        desenho.text(posicao, rotulo, fill=cor)

    return painel


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "execucao",
        type=Path,
        help="Pasta da avaliação que contém previsoes.json.",
    )
    args = parser.parse_args()

    dados = json.loads(
        (DATASET / "annotations.json").read_text(encoding="utf-8")
    )
    previsoes = json.loads(
        (args.execucao / "previsoes.json").read_text(encoding="utf-8")
    )
    amostra = json.loads(
        (RAIZ / "docs/amostra_inspecao.json").read_text(encoding="utf-8")
    )

    imagens = {item["id"]: item for item in dados["images"]}
    categorias = {item["name"]: item["id"] for item in dados["categories"]}
    saida = args.execucao / "comparacoes"
    saida.mkdir(parents=True, exist_ok=True)

    for exemplo in amostra:
        imagem_id = exemplo["image_id"]
        nome = exemplo["class_name"]
        categoria_id = categorias[nome]

        referencias = [
            item for item in dados["annotations"]
            if item["image_id"] == imagem_id
            and item["category_id"] == categoria_id
        ]
        detectadas = [
            item for item in previsoes
            if item["image_id"] == imagem_id
            and item["category_id"] == categoria_id
            and item["score"] >= LIMIAR_VISUAL
        ]

        caminho = DATASET / "images" / imagens[imagem_id]["file_name"]
        with Image.open(caminho) as arquivo:
            imagem = arquivo.convert("RGB")

        esquerda = desenhar(imagem, referencias, nome, "lime")
        direita = desenhar(imagem, detectadas, nome, "cyan", previsao=True)

        # Mantém a resolução original em cada painel.
        largura, altura = imagem.size
        comparacao = Image.new("RGB", (largura * 2, altura + 30), "white")
        comparacao.paste(esquerda, (0, 30))
        comparacao.paste(direita, (largura, 30))

        desenho = ImageDraw.Draw(comparacao)
        desenho.text((5, 8), "REFERENCIAS COCO", fill="black")
        desenho.text(
            (largura + 5, 8),
            f"YOLO - confianca >= {LIMIAR_VISUAL}",
            fill="black",
        )

        destino = saida / f"{nome.replace(' ', '_')}_{imagem_id}.jpg"
        comparacao.save(destino, quality=95)
        print(
            f"{nome}: {len(referencias)} referencias; "
            f"{len(detectadas)} previsoes acima do limiar"
        )

    print(f"\nComparacoes salvas em: {saida}")


if __name__ == "__main__":
    main()