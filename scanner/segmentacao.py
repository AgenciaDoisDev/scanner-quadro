"""Etapa 7 — flood fill, rotulação, limpeza de manchas e blocos (Entrega 1, seção 6).

O flood fill é a versão iterativa (pilha explícita) da recorrência

    FF(p, V) = V                                     se p ∉ D, B(p) = 0 ou p ∈ V   (caso base)
    FF(p, V) = FF(p4, FF(p3, FF(p2, FF(p1, V ∪ {p}))))   caso contrário

Cada volta do laço é uma chamada FF(p, ·): mesmo teste de caso base, e empilhar
os 4 vizinhos equivale às 4 chamadas recursivas. Valem os Teoremas 1 a 3.
"""
import numpy as np

from . import config
from .preprocessamento import dilatar


def flood_fill(B, p0, rotulo, R, largura):
    """Rotula a componente conexa (vizinhança-4) que contém p0. Devolve a área.

    B e R são listas planas (índice = y·largura + x) por desempenho;
    a matemática é a mesma da versão em matriz.
    """
    n = len(B)
    pilha = [p0]
    area = 0
    while pilha:
        p = pilha.pop()
        # caso base: fora de D, fundo, ou já visitado
        if p < 0 or p >= n or B[p] == 0 or R[p] != 0:
            continue
        R[p] = rotulo
        area += 1
        x = p % largura
        pilha.append(p + largura)                 # (x, y+1)
        pilha.append(p - largura)                 # (x, y−1)
        pilha.append(p + 1 if x + 1 < largura else -1)  # (x+1, y) sem passar de linha
        pilha.append(p - 1 if x > 0 else -1)            # (x−1, y)
    return area


def rotular(B):
    """Rotula todas as componentes: L₀ = 0; Lₖ = Lₖ₋₁ + 1 quando pₖ é escrita ainda sem rótulo.

    Devolve (matriz de rótulos R, número de componentes L, vetor de áreas).
    """
    alt, larg = B.shape
    Bl = B.ravel().astype(np.uint8).tolist()
    R = [0] * len(Bl)
    areas = [0]
    L = 0
    for p in np.flatnonzero(B):  # percorre linha por linha, só os pixels de escrita
        p = int(p)
        if R[p] == 0:
            L += 1
            areas.append(flood_fill(Bl, p, L, R, larg))
    return np.array(R, dtype=np.int32).reshape(alt, larg), L, np.array(areas)


def limpar_manchas(B, a_min=config.A_MIN_MANCHA, raio=config.RAIO_VIZINHANCA):
    """Remove manchas usando os rótulos do flood fill.

    B'(q) = 0 quando q pertence a uma componente Cᵢ que:
      • toca a borda da imagem (resto da moldura do quadro), ou
      • tem área |Cᵢ| < a_min E está isolada (nenhuma escrita grande a menos de `raio` px).
    A segunda condição preserva pingos de "i" e acentos, que ficam colados às letras.
    """
    R, L, areas = rotular(B)
    if L == 0:
        return B.copy(), 0, 0
    # faixa junto à borda (1,5% do tamanho): o que encosta nela é resto da moldura
    alt, larg = B.shape
    f = max(2, int(0.015 * min(alt, larg)))
    borda = np.zeros(L + 1, bool)
    borda[np.concatenate([R[:f].ravel(), R[-f:].ravel(), R[:, :f].ravel(), R[:, -f:].ravel()])] = True
    borda[0] = False

    grande = (areas >= a_min) & ~borda
    grande[0] = False
    perto_de_escrita = dilatar(grande[R], 2 * raio + 1)
    tem_vizinho = np.zeros(L + 1, bool)
    np.logical_or.at(tem_vizinho, R[R > 0], perto_de_escrita[R > 0].astype(bool))

    remover = borda | ((areas < a_min) & ~tem_vizinho)
    remover[0] = False
    limpa = B.copy()
    limpa[remover[R]] = 0
    return limpa, L, int(remover.sum())


def reduzir_max(B, fator):
    """Reduz a imagem binária: o pixel reduzido é 1 se algum pixel do bloco fator×fator é 1."""
    alt, larg = B.shape
    a2, l2 = alt // fator, larg // fator
    return B[:a2 * fator, :l2 * fator].reshape(a2, fator, l2, fator).max(axis=(1, 3))


def separar_blocos(B, imagem, fator=config.FATOR_BLOCOS, dil=config.DILATACAO_BLOCOS,
                   area_min=config.AREA_MIN_BLOCO, margem=config.MARGEM_BLOCO):
    """Dilata, rotula e recorta cada bloco de conteúdo. Devolve lista de (caixa, recorte)."""
    pequena = reduzir_max(B, fator)
    k = max(3, (dil // fator) | 1)  # tamanho ímpar
    D = dilatar(pequena, k)
    R, L, _ = rotular(D)
    if L == 0:
        return []
    ys, xs = np.nonzero(R)
    rot = R[ys, xs]
    y0 = np.full(L + 1, 10**9); x0 = np.full(L + 1, 10**9)
    y1 = np.full(L + 1, -1); x1 = np.full(L + 1, -1)
    np.minimum.at(y0, rot, ys); np.minimum.at(x0, rot, xs)
    np.maximum.at(y1, rot, ys); np.maximum.at(x1, rot, xs)

    alt, larg = B.shape
    blocos = []
    for r in range(1, L + 1):
        topo = max(0, y0[r] * fator - margem)
        esq = max(0, x0[r] * fator - margem)
        base = min(alt, (y1[r] + 1) * fator + margem)
        dir_ = min(larg, (x1[r] + 1) * fator + margem)
        if (base - topo) * (dir_ - esq) >= area_min:
            blocos.append(((topo, esq, base, dir_), imagem[topo:base, esq:dir_]))
    blocos.sort(key=lambda b: (b[0][0], b[0][1]))  # de cima para baixo, da esquerda para a direita
    return blocos
