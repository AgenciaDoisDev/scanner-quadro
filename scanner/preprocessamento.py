"""Etapas 1 a 3 — tons de cinza, suavização e bordas (Entrega 1, seções 5.2 e 5.3).

Tudo implementado com NumPy, seguindo as fórmulas do relatório.
"""
import numpy as np

# Máscara Gaussiana 3×3 (soma dos pesos = 1)
GAUSS_3x3 = np.array([[1, 2, 1],
                      [2, 4, 2],
                      [1, 2, 1]], dtype=float) / 16

# Sobel na direção x; a da direção y é a transposta
SOBEL_X = np.array([[-1, 0, 1],
                    [-2, 0, 2],
                    [-1, 0, 1]], dtype=float)
SOBEL_Y = SOBEL_X.T


def tons_de_cinza(rgb):
    """f(x,y) = 0,299 R + 0,587 G + 0,114 B  (produto escalar w·p)."""
    pesos = np.array([0.299, 0.587, 0.114])
    return rgb.astype(float) @ pesos


def convolucao(f, w):
    """Convolução discreta g = w * f, com bordas replicadas.

    g(x,y) = Σ_s Σ_t w(s,t) · f(x−s, y−t)

    Os dois laços correm só sobre a máscara; cada termo da soma é uma fatia
    deslocada da imagem inteira (vetorização NumPy). A fórmula é a mesma do
    pseudocódigo 3.2 da Entrega 2.
    """
    f = np.asarray(f, dtype=float)
    kh, kw = w.shape
    a, b = kh // 2, kw // 2
    fp = np.pad(f, ((a, a), (b, b)), mode="edge")
    M, N = f.shape
    g = np.zeros_like(f)
    for s in range(-a, a + 1):
        for t in range(-b, b + 1):
            coef = w[s + a, t + b]
            if coef != 0:
                # f(x−s, y−t) corresponde a fp[x−s+a, y−t+b]
                g += coef * fp[a - s:a - s + M, b - t:b - t + N]
    return g


def suavizar(f):
    return convolucao(f, GAUSS_3x3)


def sobel(f):
    """Magnitude do gradiente ‖∇f‖ ≈ √((Gx*f)² + (Gy*f)²).

    Usa a forma separável: Gx = [1,2,1]ᵀ · [−1,0,1]  (6 multiplicações por pixel em vez de 9).
    """
    col = np.array([[1.0], [2.0], [1.0]])
    lin = np.array([[-1.0, 0.0, 1.0]])
    gx = convolucao(convolucao(f, col), lin)
    gy = convolucao(convolucao(f, lin.T), col.T)
    return np.hypot(gx, gy)


def media_local(f, k):
    """Média em janela k×k (ou kh×kw, se k for um par), igual à convolução com a
    máscara 1/(kh·kw) de 1s.

    Calculada com imagem integral (soma acumulada), custo constante por pixel.
    """
    f = np.asarray(f, dtype=float)
    kh, kw = (k, k) if np.isscalar(k) else k
    rh, rw = kh // 2, kw // 2
    fp = np.pad(f, ((rh + 1, rh), (rw + 1, rw)), mode="edge")
    S = fp.cumsum(0).cumsum(1)
    M, N = f.shape
    total = S[kh:kh + M, kw:kw + N] - S[0:M, kw:kw + N] - S[kh:kh + M, 0:N] + S[0:M, 0:N]
    return total / (kh * kw)


def dilatar(B, k):
    """Dilatação binária: convolução com uma máscara de 1s (k×k ou kh×kw) seguida de limiar (> 0)."""
    return (media_local(B.astype(float), k) > 1e-9).astype(np.uint8)
