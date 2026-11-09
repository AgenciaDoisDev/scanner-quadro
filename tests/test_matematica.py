"""Confere as implementações próprias contra as funções equivalentes do OpenCV.

Rodar com:  python -m pytest -q
"""
import cv2
import numpy as np
import pytest

from scanner.geometria import homografia, ordenar_cantos, resolver_gauss, warp_inverso
from scanner.preprocessamento import GAUSS_3x3, SOBEL_X, convolucao, media_local, sobel
from scanner.segmentacao import rotular

RNG = np.random.default_rng(0)


def imagem_teste(alt=60, larg=80):
    return RNG.integers(0, 256, (alt, larg)).astype(float)


def test_convolucao_igual_opencv():
    f = imagem_teste()
    for w in (GAUSS_3x3, SOBEL_X):
        # filter2D faz correlação; a convolução equivale à correlação com a máscara girada 180°
        ref = cv2.filter2D(f, -1, np.flip(w), borderType=cv2.BORDER_REPLICATE)
        assert np.allclose(convolucao(f, w), ref, atol=1e-9)


def test_sobel_separavel_igual_ao_completo():
    f = imagem_teste()
    gx = convolucao(f, SOBEL_X)
    gy = convolucao(f, SOBEL_X.T)
    assert np.allclose(sobel(f), np.hypot(gx, gy), atol=1e-9)


@pytest.mark.parametrize("k", [3, 25, 41])
def test_media_local_igual_blur(k):
    f = imagem_teste(120, 150)
    ref = cv2.blur(f, (k, k), borderType=cv2.BORDER_REPLICATE)
    assert np.allclose(media_local(f, k), ref, atol=1e-6)


def test_gauss_resolve_sistema():
    A = RNG.normal(size=(8, 8))
    b = RNG.normal(size=8)
    assert np.allclose(resolver_gauss(A, b), np.linalg.solve(A, b), atol=1e-9)


def test_gauss_detecta_singular():
    with pytest.raises(ValueError):
        resolver_gauss(np.zeros((3, 3)), np.ones(3))


def test_homografia_igual_opencv():
    origem = np.array([[230, 170], [1420, 260], [1350, 1060], [180, 960]], float)
    destino = np.array([[0, 0], [1199, 0], [1199, 799], [0, 799]], float)
    ref = cv2.getPerspectiveTransform(origem.astype(np.float32), destino.astype(np.float32))
    assert np.allclose(homografia(origem, destino), ref, atol=1e-6)


def test_homografia_leva_cantos_nos_cantos():
    origem = np.array([[10, 20], [300, 15], [320, 210], [5, 190]], float)
    destino = np.array([[0, 0], [299, 0], [299, 199], [0, 199]], float)
    H = homografia(origem, destino)
    for (x, y), (xd, yd) in zip(origem, destino):
        xw, yw, w = H @ [x, y, 1]
        assert abs(xw / w - xd) < 1e-6 and abs(yw / w - yd) < 1e-6


def test_warp_proximo_do_opencv():
    f = cv2.GaussianBlur(imagem_teste(200, 300), (9, 9), 3)
    origem = np.array([[20, 15], [280, 30], [270, 190], [10, 180]], float)
    destino = np.array([[0, 0], [249, 0], [249, 159], [0, 159]], float)
    H = homografia(origem, destino)
    nosso = warp_inverso(f, H, 250, 160)
    ref = cv2.warpPerspective(f, H, (250, 160), flags=cv2.INTER_LINEAR)
    miolo = (slice(5, -5), slice(5, -5))
    assert np.abs(nosso[miolo] - ref[miolo]).mean() < 0.5


def test_ordenar_cantos():
    p = [[300, 10], [5, 190], [10, 20], [320, 210]]
    assert ordenar_cantos(p).tolist() == [[10, 20], [300, 10], [320, 210], [5, 190]]


def test_rotulacao_conta_igual_opencv():
    B = (RNG.random((90, 120)) > 0.6).astype(np.uint8)
    R, L, areas = rotular(B)
    n_ref, R_ref = cv2.connectedComponents(B, connectivity=4)
    assert L == n_ref - 1
    assert areas[1:].sum() == B.sum()       # todo pixel de escrita recebeu rótulo
    assert np.all((R > 0) == (B == 1))


def test_flood_fill_custo_4n_mais_1():
    """Teorema 3: n pixels marcados → 4n + 1 chamadas de FF."""
    from scanner import segmentacao
    B = np.zeros((20, 20), np.uint8)
    B[5:10, 3:12] = 1                        # n = 45
    chamadas = 0
    Bl = B.ravel().tolist()
    R = [0] * len(Bl)
    pilha = [5 * 20 + 3]
    while pilha:                             # mesmo laço de flood_fill, contando as chamadas
        p = pilha.pop()
        chamadas += 1
        if p < 0 or p >= len(Bl) or Bl[p] == 0 or R[p] != 0:
            continue
        R[p] = 1
        x = p % 20
        pilha += [p + 20, p - 20, p + 1 if x + 1 < 20 else -1, p - 1 if x > 0 else -1]
    assert chamadas == 4 * 45 + 1
    assert segmentacao.flood_fill(Bl, 5 * 20 + 3, 2, [0] * len(Bl), 20) == 45
