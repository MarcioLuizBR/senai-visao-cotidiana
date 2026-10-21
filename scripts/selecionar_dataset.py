"""Seleciona um subconjunto COCO sem consultar previsões do modelo."""

import json
import random
from pathlib import Path

# Resolve os caminhos a partir do projeto, independentemente do terminal.
RAIZ = Path(__file__).resolve().parents[1]
ORIGEM = RAIZ / "data/raw/annotations/instances_val2017.json"
DESTINO = RAIZ / "data/processed/coco_cotidiano"

CLASSES = [
    "person",
    "chair",
    "couch",
    "potted plant",
    "dining table",
    "laptop",
    "cup",
    "bottle",
    "book",
    "cell phone",
]
SEMENTE = 42
IMAGENS_POR_CLASSE = 20


def main():
    dados = json.loads(ORIGEM.read_text(encoding="utf-8"))
    categorias = {categoria["name"]: categoria for categoria in dados["categories"]}

    ausentes = set(CLASSES) - categorias.keys()
    if ausentes:
        raise ValueError(f"Classes ausentes no COCO: {sorted(ausentes)}")

    ids_classes = {categorias[nome]["id"] for nome in CLASSES}
    candidatas = {categoria_id: set() for categoria_id in ids_classes}

    # Uma imagem é candidata quando possui pelo menos uma anotação
    # individual da classe. Multidões não contam para a meta de 20 imagens.
    # As anotações iscrowd serão preservadas no JSON para avaliação COCO.
    for anotacao in dados["annotations"]:
        categoria_id = anotacao["category_id"]
        if categoria_id in candidatas and not anotacao.get("iscrowd", 0):
            candidatas[categoria_id].add(anotacao["image_id"])

    sorteador = random.Random(SEMENTE)
    selecionadas = set()
    amostras = {}

    for nome in CLASSES:
        categoria_id = categorias[nome]["id"]

        # Ordenar antes do sorteio evita depender da ordem de um conjunto.
        disponiveis = sorted(candidatas[categoria_id])
        if len(disponiveis) < IMAGENS_POR_CLASSE:
            raise ValueError(
                f"{nome}: apenas {len(disponiveis)} imagens elegíveis."
            )

        ids = sorted(sorteador.sample(disponiveis, IMAGENS_POR_CLASSE))
        amostras[nome] = ids
        selecionadas.update(ids)

    # A união elimina imagens sorteadas para mais de uma classe.
    imagens = sorted(
        [imagem for imagem in dados["images"] if imagem["id"] in selecionadas],
        key=lambda imagem: imagem["id"],
    )

    # Preserva todas as anotações das classes escolhidas nas imagens
    # selecionadas, incluindo objetos que não motivaram o sorteio.
    anotacoes = sorted(
        [
            anotacao
            for anotacao in dados["annotations"]
            if anotacao["image_id"] in selecionadas
            and anotacao["category_id"] in ids_classes
        ],
        key=lambda anotacao: anotacao["id"],
    )

    subconjunto = {
        "info": dados.get("info", {}),
        "licenses": dados.get("licenses", []),
        "images": imagens,
        "annotations": anotacoes,
        "categories": [categorias[nome] for nome in CLASSES],
    }

    manifesto = {
        "source": "COCO 2017 val2017",
        "seed": SEMENTE,
        "images_per_class": IMAGENS_POR_CLASSE,
        "classes": CLASSES,
        "sampled_image_ids_by_class": amostras,
        "selected_image_ids": sorted(selecionadas),
    }

    DESTINO.mkdir(parents=True, exist_ok=True)
    for nome, conteudo in [
        ("annotations.json", subconjunto),
        ("manifesto.json", manifesto),
    ]:
        (DESTINO / nome).write_text(
            json.dumps(conteudo, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    print(f"Imagens únicas selecionadas: {len(imagens)}")
    print(f"Anotações preservadas: {len(anotacoes)}")
    print("\nContagem por classe — sem multidões:")

    for nome in CLASSES:
        categoria_id = categorias[nome]["id"]
        objetos = [
            anotacao
            for anotacao in anotacoes
            if anotacao["category_id"] == categoria_id
            and not anotacao.get("iscrowd", 0)
        ]
        quantidade_imagens = len({objeto["image_id"] for objeto in objetos})
        print(f"{nome}: {quantidade_imagens} imagens, {len(objetos)} objetos")

    print("\nSeleção concluída. Nenhuma imagem foi baixada nesta etapa.")


if __name__ == "__main__":
    main()