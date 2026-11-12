"""Etapa 6 — correção de iluminação e binarização adaptativa (Entrega 1, seções 5.5 e 5.6)."""
import numpy as np

from . import config
from .preprocessamento import media_local


def e_quadro_negro(f):
    """Quadro negro/verde: a escrita (giz) é mais CLARA que o fundo.

    Usa a assimetria (skewness) dos tons, o 3º momento padronizado
        γ = E[(f − μ)³] / σ³.
    O fundo ocupa a maior parte do quadro e a escrita forma uma "cauda": no quadro
    branco a cauda é escura (γ < 0); no quadro negro, clara (γ > 0). Não depende do
    brilho geral, que muda com a luz da sala (um quadro verde iluminado pode ter
    média acima de 100 e ainda ser quadro negro).
    """
    f = np.asarray(f, dtype=float).ravel()
    sigma = f.std()
    if sigma < 1e-9:
        return False
    return float(((f - f.mean()) ** 3).mean() / sigma ** 3) > 0


def corrigir_iluminacao(f, k=config.K_ILUMINACAO):
    """f̂ = 255 · min(1, f / b), onde b estima o fundo (luz, sombra e reflexo).

    O fundo é estimado em duas passadas de média k×k:
        b₁ = média(f)            ← a tinta escura puxa b₁ para baixo perto das letras
        b  = média(max(f, b₁))   ← troca a tinta por b₁ e tira a escrita da estimativa
    Com isso letras grossas não "clareiam" o próprio fundo e saem mais escuras.
    """
    f = np.asarray(f, dtype=float)
    if e_quadro_negro(f):
        f = 255 - f  # escrita clara em fundo escuro vira escrita escura em fundo claro
    b1 = media_local(f, k)
    b = media_local(np.maximum(f, b1), k)
    return 255 * np.minimum(1.0, f / (b + 1e-6))


def binarizar_adaptativo(f, m=config.M_BINARIZACAO, C=config.C_BINARIZACAO):
    """B(x,y) = 1 se f̂(x,y) < média_local_m×m(x,y) − C  (1 = escrita, 0 = fundo)."""
    return (f < media_local(f, m) - C).astype(np.uint8)
