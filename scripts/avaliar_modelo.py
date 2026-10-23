"""Avalia o YOLO26n no subconjunto COCO e registra métricas e tempos."""

import hashlib
import json
import platform
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

import numpy as np
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval
from ultralytics import YOLO

RAIZ = Path(__file__).resolve().parents[1]
DATASET = RAIZ / "data/processed/coco_cotidiano"
SAIDA = RAIZ / "runs/avaliacao"
PESOS = RAIZ / "yolo26n.pt"

PARAMETROS = {
    "device": "cpu",
    "imgsz": 640,
    "half": False,
    "conf": 0.001,
    "iou": 0.70,
    "max_det": 300,
    "augment": False,
    "save": False,
    "verbose": False,
}


def salvar_json(caminho, conteudo):
    """Grava resultados legíveis, sem aceitar números JSON inválidos."""
    caminho.write_text(
        json.dumps(conteudo, indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )


def media_valida(valores):
    """COCOeval usa -1 quando determinada métrica não está disponível."""
    validos = valores[valores >= 0]
    return float(validos.mean()) if validos.size else None


def main():
    # Uma pasta diferente por execução evita substituir resultados anteriores.
    from datetime import datetime

    pasta_execucao = SAIDA / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    pasta_execucao.mkdir(parents=True, exist_ok=False)

    referencia = COCO(str(DATASET / "annotations.json"))
    ids_imagens = sorted(referencia.getImgIds())
    ids_categorias = sorted(referencia.getCatIds())

    if not ids_imagens:
        raise ValueError("O conjunto de avaliação está vazio.")

    modelo = YOLO(str(PESOS))

    # Faz a associação pelo nome, pois IDs COCO e IDs YOLO são diferentes.
    categorias_por_nome = {
        categoria["name"]: categoria["id"]
        for categoria in referencia.loadCats(ids_categorias)
    }
    modelo_para_coco = {
        int(classe_id): categorias_por_nome[nome]
        for classe_id, nome in modelo.names.items()
        if nome in categorias_por_nome
    }

    if set(modelo_para_coco.values()) != set(ids_categorias):
        raise ValueError("Nem todas as classes COCO foram encontradas no modelo.")

    salvar_json(
        pasta_execucao / "mapeamento_classes.json",
        [
            {
                "model_class_id": classe_id,
                "coco_category_id": categoria_id,
                "class_name": modelo.names[classe_id],
            }
            for classe_id, categoria_id in sorted(modelo_para_coco.items())
        ],
    )

    # Registra configuração, versões e pesos antes de executar a avaliação.
    configuracao = {
        "model": PESOS.name,
        "weights_sha256": hashlib.sha256(PESOS.read_bytes()).hexdigest(),
        "annotations_sha256": hashlib.sha256(
            (DATASET / "annotations.json").read_bytes()
        ).hexdigest(),
        "parameters": PARAMETROS,
        "image_ids": ids_imagens,
        "category_ids": ids_categorias,
        "warmup_calls": 3,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "versions": {
            pacote: version(pacote)
            for pacote in (
                "ultralytics", "torch", "torchvision", "pycocotools", "numpy"
            )
        },
    }
    salvar_json(pasta_execucao / "configuracao.json", configuracao)

    primeira = referencia.loadImgs([ids_imagens[0]])[0]
    caminho_aquecimento = DATASET / "images" / primeira["file_name"]

    print("\nExecutando três chamadas de aquecimento...")
    for _ in range(3):
        modelo.predict(source=str(caminho_aquecimento), **PARAMETROS)

    previsoes = []
    tempos = []

    for numero, imagem_id in enumerate(ids_imagens, start=1):
        imagem = referencia.loadImgs([imagem_id])[0]
        caminho = DATASET / "images" / imagem["file_name"]

        # A medição engloba a chamada predict, incluindo a leitura da imagem.
        inicio = perf_counter()
        resultado = modelo.predict(source=str(caminho), **PARAMETROS)[0]
        duracao_ms = (perf_counter() - inicio) * 1000

        tempos.append({"image_id": imagem_id, "predict_ms": duracao_ms})

        for caixa in resultado.boxes:
            classe_id = int(caixa.cls.item())
            if classe_id not in modelo_para_coco:
                continue

            x_min, y_min, x_max, y_max = caixa.xyxy[0].tolist()

            # COCO espera [x, y, largura, altura], em pixels.
            # Não arredondamos as previsões antes de calcular as métricas.
            previsoes.append(
                {
                    "image_id": imagem_id,
                    "category_id": modelo_para_coco[classe_id],
                    "bbox": [
                        x_min,
                        y_min,
                        x_max - x_min,
                        y_max - y_min,
                    ],
                    "score": float(caixa.conf.item()),
                }
            )

        print(f"[{numero}/{len(ids_imagens)}] imagem {imagem_id}")

    salvar_json(pasta_execucao / "previsoes.json", previsoes)
    salvar_json(pasta_execucao / "tempos.json", tempos)

    # loadRes não aceita lista vazia em algumas versões; tratamos esse caso.
    if previsoes:
        deteccoes = referencia.loadRes(previsoes)
    else:
        deteccoes = COCO()
        deteccoes.dataset = {
            "images": referencia.dataset["images"],
            "categories": referencia.dataset["categories"],
            "annotations": [],
        }
        deteccoes.createIndex()

    avaliador = COCOeval(referencia, deteccoes, iouType="bbox")
    avaliador.params.imgIds = ids_imagens
    avaliador.params.catIds = ids_categorias
    avaliador.params.maxDets = [1, 10, 100]

    # O avaliador oficial aplica o tratamento COCO às anotações iscrowd.
    avaliador.evaluate()
    avaliador.accumulate()
    avaliador.summarize()

    # precision tem dimensões: IoU, recall, categoria, área e maxDets.
    precisao = avaliador.eval["precision"]
    indice_area = avaliador.params.areaRngLbl.index("all")
    indice_limite = list(avaliador.params.maxDets).index(100)
    indice_iou50 = int(
        np.flatnonzero(np.isclose(avaliador.params.iouThrs, 0.50))[0]
    )

    por_classe = []
    for indice, categoria_id in enumerate(avaliador.params.catIds):
        nome = referencia.loadCats([categoria_id])[0]["name"]
        ap = media_valida(
            precisao[:, :, indice, indice_area, indice_limite]
        )
        ap50 = media_valida(
            precisao[indice_iou50, :, indice, indice_area, indice_limite]
        )
        por_classe.append(
            {"class_name": nome, "AP_50_95": ap, "AP_50": ap50}
        )

    duracoes = np.array([item["predict_ms"] for item in tempos])
    metricas = {
        "images": len(ids_imagens),
        "detections": len(previsoes),
        "AP_50_95": float(avaliador.stats[0]),
        "AP_50": float(avaliador.stats[1]),
        "AP_75": float(avaliador.stats[2]),
        "AR_100": float(avaliador.stats[8]),
        "per_class": por_classe,
        "timing_ms": {
            "mean": float(duracoes.mean()),
            "median": float(np.median(duracoes)),
            "p95": float(np.percentile(duracoes, 95)),
        },
    }
    salvar_json(pasta_execucao / "metricas.json", metricas)

    print("\nRESUMO")
    print(json.dumps(metricas, indent=2, ensure_ascii=False))
    print(f"\nResultados salvos em: {pasta_execucao}")


if __name__ == "__main__":
    main()