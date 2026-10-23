"""Verifica a execução do YOLO26n pré-treinado em uma imagem local."""

import argparse
import json
from pathlib import Path

from ultralytics import YOLO


def main():
    # O argumento permite testar imagens diferentes sem alterar o código.
    parser = argparse.ArgumentParser(
        description="Executa uma primeira detecção de objetos em CPU."
    )
    parser.add_argument("imagem", type=Path, help="Caminho da imagem de teste.")
    args = parser.parse_args()

    # Verificamos o arquivo antes de carregar o modelo.
    if not args.imagem.is_file():
        parser.error(f"Imagem não encontrada: {args.imagem}")

    # Na primeira execução, o Ultralytics baixa os pesos pré-treinados.
    # Carregar esses pesos não realiza treinamento nem fine-tuning.
    modelo = YOLO("yolo26n.pt")

    # CPU é definida explicitamente para reproduzir a configuração escolhida.
    # O limiar de 0.25 é um ponto de partida, ainda sem ajuste experimental.
    resultados = modelo.predict(
        source=str(args.imagem),
        device="cpu",
        conf=0.25,
        imgsz=640,
        save=False,
        verbose=False,
    )

    resultado = resultados[0]

    # Salva uma imagem anotada para inspeção visual das previsões.
    # Este recurso pertence ao teste local; a futura API retornará JSON.
    pasta_saida = Path("runs/primeira_deteccao")
    pasta_saida.mkdir(parents=True, exist_ok=True)

    caminho_saida = pasta_saida / f"{args.imagem.stem}_deteccoes.jpg"
    resultado.save(filename=str(caminho_saida))

    deteccoes = []
    

    # Cada caixa contém a classe prevista, a confiança e as coordenadas
    # em pixels, relativas à imagem original.
    for caixa in resultado.boxes:
        classe_id = int(caixa.cls.item())
        x_min, y_min, x_max, y_max = caixa.xyxy[0].tolist()

        deteccoes.append(
            {
                "class_name": resultado.names[classe_id],
                "confidence": round(float(caixa.conf.item()), 4),
                "box": {
                    "x_min": round(x_min, 2),
                    "y_min": round(y_min, 2),
                    "x_max": round(x_max, 2),
                    "y_max": round(y_max, 2),
                },
            }
        )

    # Este formato antecipa a resposta da futura API.
    # Uma imagem sem objetos reconhecidos produz uma lista vazia.
    resposta = {"status": "success", "detections": deteccoes}
    print(json.dumps(resposta, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    # Evita executar a rotina automaticamente caso o arquivo seja importado.
    main()