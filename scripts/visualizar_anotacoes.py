"""Desenha anotações COCO em uma amostra reproduzível por classe."""

import json
import random
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parents[1]
DATASET = RAIZ / "data/processed/coco_cotidiano"
SAIDA = RAIZ / "runs/inspecao_anotacoes"


def main():
    dados = json.loads(
        (DATASET / "annotations.json").read_text(encoding="utf-8")
    )
    imagens = {item["id"]: item for item in dados["images"]}
    categorias = {item["id"]: item["name"] for item in dados["categories"]}

    por_imagem = defaultdict(list)
    candidatas = defaultdict(set)

    for anotacao in dados["annotations"]:
        por_imagem[anotacao["image_id"]].append(anotacao)
        if not anotacao.get("iscrowd", 0):
            candidatas[anotacao["category_id"]].add(anotacao["image_id"])

    SAIDA.mkdir(parents=True, exist_ok=True)
    sorteador = random.Random(42)
    registro = []

    # Sorteia uma imagem por classe. Uma mesma imagem pode representar
    # mais de uma classe, mas cada arquivo destaca apenas a classe-alvo.
    for categoria_id, nome in sorted(categorias.items()):
        imagem_id = sorteador.choice(sorted(candidatas[categoria_id]))
        metadados = imagens[imagem_id]
        origem = DATASET / "images" / metadados["file_name"]

        with Image.open(origem) as arquivo:
            imagem = arquivo.convert("RGB")

        desenho = ImageDraw.Draw(imagem)
        quantidade = 0

        for anotacao in por_imagem[imagem_id]:
            if anotacao["category_id"] != categoria_id:
                continue

            # Converte COCO [x, y, largura, altura] para os dois cantos.
            x, y, largura, altura = anotacao["bbox"]
            multidao = bool(anotacao.get("iscrowd", 0))
            cor = "orange" if multidao else "lime"
            rotulo = nome + (" [iscrowd]" if multidao else "")

            desenho.rectangle(
                [x, y, x + largura, y + altura],
                outline=cor,
                width=3,
            )

            # Fundo escuro melhora a leitura do nome da classe.
            posicao = (max(0, x), max(0, y))
            limites = desenho.textbbox(posicao, rotulo)
            desenho.rectangle(limites, fill="black")
            desenho.text(posicao, rotulo, fill=cor)
            quantidade += 1

        nome_saida = f"{nome.replace(' ', '_')}_{imagem_id}.jpg"
        imagem.save(SAIDA / nome_saida, quality=95)

        registro.append(
            {
                "class_name": nome,
                "image_id": imagem_id,
                "annotation_count": quantidade,
                "output_file": nome_saida,
            }
        )
        print(f"{nome}: {nome_saida} — {quantidade} anotações")

    # Registra os exemplos usados, sem afirmar que já foram revisados.
    (SAIDA / "amostra.json").write_text(
        json.dumps(registro, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print("\nAmostra gerada em runs/inspecao_anotacoes.")
    print("Verde: objeto individual. Laranja: multidão.")


if __name__ == "__main__":
    main()