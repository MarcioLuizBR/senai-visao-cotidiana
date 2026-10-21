"""Verifica a consistência do subconjunto COCO antes da avaliação."""

import json
import math
from collections import Counter
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / "data/processed/coco_cotidiano"
MANIFESTO = RAIZ / "docs/dataset_manifesto.json"


def main():
    dados = json.loads((PASTA / "annotations.json").read_text(encoding="utf-8"))
    manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8"))

    erros = []
    avisos = []

    # IDs únicos são necessários para associar cada objeto à imagem correta.
    for chave in ("images", "annotations", "categories"):
        ids = [item["id"] for item in dados[chave]]
        if len(ids) != len(set(ids)):
            erros.append(f"IDs duplicados em {chave}.")

    imagens = {item["id"]: item for item in dados["images"]}
    categorias = {item["id"]: item["name"] for item in dados["categories"]}

    if set(imagens) != set(manifesto["selected_image_ids"]):
        erros.append("Imagens do dataset diferem do manifesto versionado.")

    if set(categorias.values()) != set(manifesto["classes"]):
        erros.append("Classes do dataset diferem do manifesto.")

    # Confere se os arquivos existentes correspondem aos metadados.
    for imagem in imagens.values():
        caminho = PASTA / "images" / imagem["file_name"]
        try:
            with Image.open(caminho) as arquivo:
                arquivo.load()
                esperado = (imagem["width"], imagem["height"])
                if arquivo.size != esperado:
                    erros.append(f"Dimensões divergentes: {caminho.name}.")
        except OSError as erro:
            erros.append(f"Imagem indisponível ou inválida: {caminho.name}: {erro}")

    objetos = Counter()
    imagens_por_classe = {categoria_id: set() for categoria_id in categorias}
    multidoes = 0
    caixas_fora = 0

    for anotacao in dados["annotations"]:
        identificador = anotacao["id"]
        imagem = imagens.get(anotacao["image_id"])
        categoria_id = anotacao["category_id"]

        if imagem is None or categoria_id not in categorias:
            erros.append(f"Anotação {identificador}: imagem ou categoria inexistente.")
            continue

        # No formato COCO, bbox = [x, y, largura, altura], em pixels.
        caixa = anotacao.get("bbox", [])
        if (
            len(caixa) != 4
            or not all(
                isinstance(valor, (int, float)) and math.isfinite(valor)
                for valor in caixa
            )
        ):
            erros.append(f"Anotação {identificador}: bbox inválida.")
            continue

        x, y, largura, altura = caixa
        if largura <= 0 or altura <= 0:
            erros.append(f"Anotação {identificador}: caixa sem área positiva.")
            continue

        # Usa tolerância para pequenas diferenças numéricas.
        # Caixas fora da imagem são relatadas, sem correção silenciosa.
        tolerancia = 0.01
        if (
            x < -tolerancia
            or y < -tolerancia
            or x + largura > imagem["width"] + tolerancia
            or y + altura > imagem["height"] + tolerancia
        ):
            caixas_fora += 1

        area = anotacao.get("area")
        if (
            not isinstance(area, (int, float))
            or not math.isfinite(area)
            or area <= 0
        ):
            erros.append(f"Anotação {identificador}: área inválida.")

        # A área COCO pode ser a área da segmentação; por isso não exigimos
        # igualdade entre 'area' e largura * altura da bounding box.
        iscrowd = anotacao.get("iscrowd", 0)
        if iscrowd not in (0, 1):
            erros.append(f"Anotação {identificador}: iscrowd inválido.")
        elif iscrowd:
            multidoes += 1
        else:
            objetos[categoria_id] += 1
            imagens_por_classe[categoria_id].add(imagem["id"])

    if caixas_fora:
        avisos.append(f"{caixas_fora} bounding boxes ultrapassam os limites da imagem.")

    resumo_classes = {}
    for categoria_id, nome in categorias.items():
        quantidade = len(imagens_por_classe[categoria_id])
        resumo_classes[nome] = {
            "images": quantidade,
            "individual_objects": objetos[categoria_id],
        }
        if quantidade < manifesto["images_per_class"]:
            erros.append(f"{nome}: quantidade de imagens abaixo da meta.")

    relatorio = {
        "images": len(imagens),
        "categories": len(categorias),
        "annotations": len(dados["annotations"]),
        "crowd_annotations": multidoes,
        "classes": resumo_classes,
        "errors": erros,
        "warnings": avisos,
    }

    (PASTA / "validation_report.json").write_text(
        json.dumps(relatorio, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Imagens: {len(imagens)}")
    print(f"Classes: {len(categorias)}")
    print(f"Anotações: {len(dados['annotations'])}")
    print(f"Multidões preservadas: {multidoes}")
    print(f"Erros: {len(erros)}")
    print(f"Avisos: {len(avisos)}")

    for mensagem in erros + avisos:
        print(f"- {mensagem}")

    if erros:
        raise SystemExit("Validação reprovada. Confira o relatório.")
    if avisos:
        print("Verificações concluídas com avisos para análise.")
    else:
        print("Validação concluída sem erros ou avisos.")


if __name__ == "__main__":
    main()
    