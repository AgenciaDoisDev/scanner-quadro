"""Etapas 4 e 5 — cantos do quadro, homografia e warp inverso (Entrega 1, seção 5.4).

A homografia, a eliminação de Gauss e o warp com interpolação bilinear são
implementação própria. O OpenCV é usado apenas para extrair contornos.
"""
import cv2
import numpy as np

from . import config
from .preprocessamento import dilatar


# ---------------------------------------------------------------- cantos

def ordenar_cantos(p):
    """Ordena 4 pontos em: superior-esquerdo, superior-direito, inferior-direito, inferior-esquerdo."""
    p = np.asarray(p, dtype=float).reshape(4, 2)
    soma = p[:, 0] + p[:, 1]
    dif = p[:, 1] - p[:, 0]
    return np.array([p[np.argmin(soma)], p[np.argmin(dif)],
                     p[np.argmax(soma)], p[np.argmax(dif)]])


def achar_cantos(bordas, area_min=config.AREA_MIN_QUADRO, tol=config.TOLERANCIA_POLIGONO):
    """Procura o maior contorno que vira um quadrilátero convexo. Devolve 4 cantos ou None."""
    fechado = dilatar(bordas, 5) * 255  # fecha pequenas falhas na moldura
    contornos, _ = cv2.findContours(fechado.astype(np.uint8), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
    area_foto = bordas.shape[0] * bordas.shape[1]
    for c in sorted(contornos, key=cv2.contourArea, reverse=True):
        if cv2.contourArea(c) < area_min * area_foto:
            break
        for candidato in (c, cv2.convexHull(c)):
            p = cv2.approxPolyDP(candidato, tol * cv2.arcLength(candidato, True), True)
            if len(p) == 4 and cv2.isContourConvex(p):
                return ordenar_cantos(p)
    return None


# ---------------------------------------------------------------- sistema linear

def resolver_gauss(A, b):
    """Resolve A x = b por eliminação de Gauss com pivoteamento parcial."""
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)
    for k in range(n):
        piv = k + np.argmax(np.abs(A[k:, k]))
        if abs(A[piv, k]) < 1e-12:
            raise ValueError("sistema singular (det A = 0): cantos colineares")
        A[[k, piv]] = A[[piv, k]]
        b[[k, piv]] = b[[piv, k]]
        for i in range(k + 1, n):
            m = A[i, k] / A[k, k]
            A[i, k:] -= m * A[k, k:]
            b[i] -= m * b[k]
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):  # substituição reversa
        x[i] = (b[i] - A[i, i + 1:] @ x[i + 1:]) / A[i, i]
    return x


# ---------------------------------------------------------------- homografia

def homografia(origem, destino):
    """Matriz H 3×3 que leva os 4 pontos de origem nos 4 de destino (sistema 8×8, A h = b)."""
    A = np.zeros((8, 8))
    b = np.zeros(8)
    for i in range(4):
        x, y = origem[i]
        xd, yd = destino[i]
        A[2 * i] = [x, y, 1, 0, 0, 0, -x * xd, -y * xd]
        b[2 * i] = xd
        A[2 * i + 1] = [0, 0, 0, x, y, 1, -x * yd, -y * yd]
        b[2 * i + 1] = yd
    h = resolver_gauss(A, b)
    return np.append(h, 1.0).reshape(3, 3)


def retangulo_destino(c):
    """Tamanho do quadro retificado (média dos lados opostos) e seus 4 cantos."""
    c = np.asarray(c, dtype=float)
    W = int(round((np.linalg.norm(c[1] - c[0]) + np.linalg.norm(c[2] - c[3])) / 2))
    Hd = int(round((np.linalg.norm(c[3] - c[0]) + np.linalg.norm(c[2] - c[1])) / 2))
    destino = np.array([[0, 0], [W - 1, 0], [W - 1, Hd - 1], [0, Hd - 1]], dtype=float)
    return W, Hd, destino


def warp_inverso(f, H, W, Hd, fundo=255.0):
    """Para cada pixel (u,v) do destino, busca a origem por H⁻¹ e interpola (bilinear)."""
    f = np.asarray(f, dtype=float)
    Hinv = np.linalg.inv(H)
    v, u = np.mgrid[0:Hd, 0:W]
    pts = np.stack([u.ravel(), v.ravel(), np.ones(u.size)])  # coordenadas homogêneas
    xw, yw, w = Hinv @ pts
    x = (xw / w).reshape(Hd, W)
    y = (yw / w).reshape(Hd, W)

    alt, larg = f.shape[:2]
    dentro = (x >= 0) & (x <= larg - 1) & (y >= 0) & (y <= alt - 1)
    x = np.clip(x, 0, larg - 1)
    y = np.clip(y, 0, alt - 1)
    x0 = np.minimum(np.floor(x).astype(int), larg - 2)
    y0 = np.minimum(np.floor(y).astype(int), alt - 2)
    dx = x - x0
    dy = y - y0
    if f.ndim == 3:  # imagem colorida: mesmos pesos para cada canal
        dx, dy, dentro = dx[..., None], dy[..., None], dentro[..., None]
    saida = ((1 - dx) * (1 - dy) * f[y0, x0] + dx * (1 - dy) * f[y0, x0 + 1]
             + (1 - dx) * dy * f[y0 + 1, x0] + dx * dy * f[y0 + 1, x0 + 1])
    return np.where(dentro, saida, fundo)


def retificar(imagem, cantos):
    """Aplica a correção de perspectiva completa. Devolve a imagem e a matriz H."""
    W, Hd, destino = retangulo_destino(cantos)
    H = homografia(cantos, destino)
    return warp_inverso(imagem, H, W, Hd), H
