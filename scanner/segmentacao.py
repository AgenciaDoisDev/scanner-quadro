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


def limpar_manchas(B, a_min=config.A_MIN_MANCHA, a_pingo=config.A_MIN_PINGO,
                   raio=config.RAIO_VIZINHANCA):
    """Remove manchas usando os rótulos do flood fill.

    Cada componente Cᵢ é classificada pela área:
      • forte:  |Cᵢ| ≥ a_min                 → é escrita, fica;
      • pingo:  a_pingo ≤ |Cᵢ| < a_min       → fica só se estiver a até `raio` px
                                               de uma componente forte (pingo do "i",
                                               acento, ":", ponto de fórmula);
      • poeira: |Cᵢ| < a_pingo               → sai sempre.
    Por fim, apaga a faixa junto à borda (resto da moldura do quadro).
    Devolve (imagem limpa, nº de componentes, nº removidas, máscara das fortes).
    """
    R, L, areas = rotular(B)
    if L == 0:
        return B.copy(), 0, 0, np.zeros_like(B)
    forte = areas >= a_min
    pingo = (areas >= a_pingo) & ~forte
    forte[0] = pingo[0] = False

    perto = dilatar(forte[R], 2 * raio + 1) > 0           # região a até `raio` px da escrita forte
    tem_vizinho = np.bincount(R[perto], minlength=L + 1) > 0
    manter = forte | (pingo & tem_vizinho)
    manter[0] = False

    limpa = manter[R].astype(np.uint8)
    alt, larg = B.shape
    f = max(2, int(config.FAIXA_BORDA * min(alt, larg)))
    limpa[:f], limpa[-f:], limpa[:, :f], limpa[:, -f:] = 0, 0, 0, 0
    return limpa, L, int(L - manter.sum()), forte[R].astype(np.uint8)


def reduzir_max(B, fator):
    """Reduz a imagem binária: o pixel reduzido é 1 se algum pixel do bloco fator×fator é 1."""
    alt, larg = B.shape
    a2, l2 = alt // fator, larg // fator
    return B[:a2 * fator, :l2 * fator].reshape(a2, fator, l2, fator).max(axis=(1, 3))


def separar_blocos(B, imagem, forte=None, fator=config.FATOR_BLOCOS,
                   dil=config.DILATACAO_BLOCOS, area_min=config.AREA_MIN_BLOCO,
                   margem=config.MARGEM_BLOCO):
    """Junta as letras em blocos e recorta cada um. Devolve lista de (caixa, recorte).

    A dilatação é mais larga na horizontal (dil = (altura, largura)): letras da mesma
    linha se juntam antes de linhas diferentes. Um bloco só vale se tiver escrita
    forte suficiente (TINTA_MIN_BLOCO px); o que sobra é resto de mancha.
    """
    forte = B if forte is None else forte
    pequena = reduzir_max(B, fator)
    k = tuple(max(3, (d // fator) | 1) for d in dil)  # tamanhos ímpares
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
        tinta_forte = int(forte[topo:base, esq:dir_].sum())
        if (base - topo) * (dir_ - esq) >= area_min and tinta_forte >= config.TINTA_MIN_BLOCO:
            blocos.append(((topo, esq, base, dir_), imagem[topo:base, esq:dir_]))
    blocos.sort(key=lambda b: (b[0][0], b[0][1]))  # de cima para baixo, da esquerda para a direita
    return blocos
