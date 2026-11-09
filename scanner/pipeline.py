"""Orquestrador — PROCESSAR_FOTO (Entrega 2, pseudocódigo 3.1)."""
import io
import time

import numpy as np
from PIL import Image

from . import config, ia
from .geometria import achar_cantos, retificar
from .preprocessamento import sobel, suavizar, tons_de_cinza
from .realce import binarizar_adaptativo, corrigir_iluminacao, e_quadro_negro
from .segmentacao import limpar_manchas, separar_blocos


def processar_foto(rgb, cantos=None, usar_ia=True):
    """Executa o pipeline completo. Devolve um dict com cada etapa, avisos e tempos."""
    r = {"avisos": [], "tempos": {}}
    t = time.perf_counter

    t0 = t()
    cinza = tons_de_cinza(rgb)
    suave = suavizar(cinza)
    mag = sobel(suave)
    bordas = (mag > config.LIMIAR_BORDA).astype(np.uint8)
    r.update(original=rgb, cinza=cinza, bordas=bordas)
    r["tempos"]["pré-processamento"] = t() - t0

    t0 = t()
    if cantos is None:
        cantos = achar_cantos(bordas)
    if cantos is None:
        r["avisos"].append("Não encontrei os 4 cantos do quadro; usei a foto inteira. "
                           "Tente uma foto com o quadro inteiro aparecendo.")
        alt, larg = cinza.shape
        cantos = np.array([[0, 0], [larg - 1, 0], [larg - 1, alt - 1], [0, alt - 1]], float)
    quadro_cor, H = retificar(rgb, cantos)
    quadro = tons_de_cinza(quadro_cor)
    r.update(cantos=cantos, H=H, quadro_cor=quadro_cor.astype(np.uint8))
    r["tempos"]["homografia"] = t() - t0

    t0 = t()
    r["quadro_negro"] = e_quadro_negro(quadro)
    claro = corrigir_iluminacao(quadro)
    B = binarizar_adaptativo(claro)
    r.update(claro=claro.astype(np.uint8), binaria=B)
    r["tempos"]["iluminação e binarização"] = t() - t0

    t0 = t()
    limpa, n_comp, n_manchas = limpar_manchas(B)
    blocos = separar_blocos(limpa, claro.astype(np.uint8))
    r.update(limpa=limpa, componentes=n_comp, manchas_removidas=n_manchas, blocos=blocos)
    r["scan"] = (255 * (1 - limpa)).astype(np.uint8)  # escrita preta em fundo branco
    r["tempos"]["flood fill e blocos"] = t() - t0
    if not blocos:
        r["avisos"].append("Nenhum bloco de escrita encontrado.")

    r["ia"] = None
    if usar_ia and blocos:
        if not ia.disponivel():
            r["avisos"].append("Resumo indisponível: configure ANTHROPIC_API_KEY no arquivo .env.")
        else:
            t0 = t()
            try:
                r["ia"] = ia.resumir_com_ia(r["claro"], blocos)
            except Exception as e:  # rede, chave inválida, resposta fora do formato
                r["avisos"].append(f"Resumo indisponível: {e}")
            r["tempos"]["IA"] = t() - t0
    return r


def gerar_pdf(imagem):
    """Exporta a imagem tratada em PDF (Pillow)."""
    buf = io.BytesIO()
    Image.fromarray(imagem).convert("RGB").save(buf, format="PDF", resolution=150)
    return buf.getvalue()
