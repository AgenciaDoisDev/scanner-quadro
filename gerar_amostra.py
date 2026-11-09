"""Gera uma foto sintética de quadro branco (torta, com reflexo, sombra e manchas) para testes.

Uso: python gerar_amostra.py   ->   amostras/quadro_sintetico.jpg
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))


def fonte(tam):
    for nome in ("DejaVuSans.ttf", "Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/Library/Fonts/Arial.ttf", "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(nome, tam)
        except OSError:
            pass
    return ImageFont.load_default()


def quadro():
    W, H = 1400, 900
    img = Image.new("L", (W, H), 235)
    d = ImageDraw.Draw(img)
    d.text((60, 40), "Aula 7 - Transformacoes no plano", font=fonte(54), fill=30)
    linhas = [
        "1) Translacao:  x' = x + tx ,  y' = y + ty",
        "2) Escala:  x' = sx . x ,  y' = sy . y",
        "3) Rotacao:  x' = x cos(t) - y sin(t)",
        "                  y' = x sin(t) + y cos(t)",
    ]
    for i, l in enumerate(linhas):
        d.text((70, 160 + 70 * i), l, font=fonte(38), fill=35)
    d.text((70, 480), "Coordenadas homogeneas:", font=fonte(40), fill=25)
    d.text((110, 545), "[x' y' 1] = M . [x y 1]   (tudo vira produto de matrizes)", font=fonte(34), fill=40)
    d.text((70, 650), "Composicao: M = T . R . S", font=fonte(40), fill=30)
    d.rectangle((900, 640, 1300, 840), outline=40, width=4)
    d.line((920, 820, 1280, 660), fill=40, width=4)
    return np.asarray(img, dtype=float)


def foto():
    rng = np.random.default_rng(7)
    q = quadro()
    H, W = q.shape
    yy, xx = np.mgrid[0:H, 0:W]
    luz = 0.75 + 0.35 * (xx / W)                                     # sombra à esquerda
    reflexo = 60 * np.exp(-((xx - 950) ** 2 + (yy - 250) ** 2) / (2 * 160 ** 2))
    q = q * luz + reflexo
    for _ in range(250):                                             # resíduos de apagador
        y, x = rng.integers(0, H), rng.integers(0, W)
        cv2.circle(q, (int(x), int(y)), int(rng.integers(1, 3)), 120, -1)
    q = np.clip(q, 0, 255)
    rgb = np.stack([q * 0.98, q, q * 1.02], -1)

    # moldura e parede, depois perspectiva
    moldura = np.full((H + 40, W + 40, 3), 90.0)
    moldura[20:-20, 20:-20] = rgb
    ph, pw = 1200, 1600
    origem = np.float32([[0, 0], [W + 39, 0], [W + 39, H + 39], [0, H + 39]])
    destino = np.float32([[230, 170], [1420, 260], [1350, 1060], [180, 960]])
    M = cv2.getPerspectiveTransform(origem, destino)
    parede = np.zeros((ph, pw, 3)) + np.array([170, 160, 140])
    parede += rng.normal(0, 4, parede.shape)
    out = cv2.warpPerspective(moldura, M, (pw, ph), borderMode=cv2.BORDER_TRANSPARENT,
                              dst=parede.copy())
    out = cv2.GaussianBlur(out, (3, 3), 0) + rng.normal(0, 3, out.shape)
    return np.clip(out, 0, 255).astype(np.uint8)


if __name__ == "__main__":
    os.makedirs(os.path.join(AQUI, "amostras"), exist_ok=True)
    caminho = os.path.join(AQUI, "amostras", "quadro_sintetico.jpg")
    Image.fromarray(foto()).save(caminho, quality=90)
    print("salvo em", caminho)
