"""Etapa 6 — correção de iluminação e binarização adaptativa (Entrega 1, seções 5.5 e 5.6)."""
import numpy as np

from . import config
from .preprocessamento import media_local


def e_quadro_negro(f):
    """Quadro negro/verde: a imagem é escura na média."""
    return float(np.mean(f)) < 100


def corrigir_iluminacao(f, k=config.K_ILUMINACAO):
    """f̂ = 255 · min(1, f / b), onde b = média k×k estima o fundo (luz, sombra e reflexo)."""
    f = np.asarray(f, dtype=float)
    if e_quadro_negro(f):
        f = 255 - f  # escrita clara em fundo escuro vira escrita escura em fundo claro
    b = media_local(f, k)
    return 255 * np.minimum(1.0, f / (b + 1e-6))


def binarizar_adaptativo(f, m=config.M_BINARIZACAO, C=config.C_BINARIZACAO):
    """B(x,y) = 1 se f̂(x,y) < média_local_m×m(x,y) − C  (1 = escrita, 0 = fundo)."""
    return (f < media_local(f, m) - C).astype(np.uint8)
