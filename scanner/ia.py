"""Etapa 8 — módulo de IA: transcrição, tema, resumo e explicação.

Módulo complementar: recebe a imagem já tratada pelo pipeline visual.
Precisa da variável ANTHROPIC_API_KEY (arquivo .env). Sem ela, o sistema
continua funcionando e só o resumo fica indisponível.
"""
import base64
import io
import json
import os
import re

import numpy as np
from PIL import Image

from . import config

MODELO_PADRAO = "claude-sonnet-5-5"

PROMPT_TRANSCRICAO = (
    "Esta imagem é um trecho de um quadro de sala de aula, já recortado e limpo. "
    "Transcreva fielmente o que está escrito, incluindo fórmulas (use notação simples). "
    "Se houver desenho ou esquema, descreva-o em uma linha entre colchetes. "
    "Responda só com a transcrição."
)

PROMPT_RESUMO = (
    "Abaixo está a transcrição do quadro de uma aula. Responda APENAS com um JSON válido, "
    "em português do Brasil, com as chaves:\n"
    '  "tema": o assunto da aula em uma frase curta;\n'
    '  "resumo": lista de 3 a 7 tópicos curtos com os pontos principais;\n'
    '  "explicacao": explicação didática do conteúdo em 2 a 4 parágrafos, com um exemplo.\n\n'
    "Transcrição:\n"
)


def disponivel():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _png_base64(imagem):
    img = Image.fromarray(np.clip(imagem, 0, 255).astype(np.uint8))
    if max(img.size) > 1568:  # limite prático de resolução para a API
        img.thumbnail((1568, 1568))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.standard_b64encode(buf.getvalue()).decode()


def _chamar(cliente, modelo, conteudo, max_tokens=1500):
    resp = cliente.messages.create(model=modelo, max_tokens=max_tokens,
                                   messages=[{"role": "user", "content": conteudo}])
    return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()


def _imagem(imagem):
    return {"type": "image",
            "source": {"type": "base64", "media_type": "image/png", "data": _png_base64(imagem)}}


def _extrair_json(texto):
    m = re.search(r"\{.*\}", texto, re.S)
    if not m:
        raise ValueError("a IA não devolveu JSON")
    return json.loads(m.group(0))


def resumir_com_ia(imagem_quadro, blocos, modelo=None):
    """Devolve dict com transcricao, tema, resumo (lista) e explicacao."""
    import anthropic  # importado aqui para o resto do sistema funcionar sem o SDK

    modelo = modelo or os.environ.get("MODELO_IA", MODELO_PADRAO)
    cliente = anthropic.Anthropic()

    # Poucos blocos: transcreve um a um (mais legível). Muitos: manda o quadro inteiro.
    if 0 < len(blocos) <= config.MAX_BLOCOS_IA:
        partes = [_chamar(cliente, modelo, [_imagem(rec), {"type": "text", "text": PROMPT_TRANSCRICAO}])
                  for _, rec in blocos]
        transcricao = "\n\n".join(partes)
    else:
        transcricao = _chamar(cliente, modelo, [_imagem(imagem_quadro),
                                                {"type": "text", "text": PROMPT_TRANSCRICAO}])

    resposta = _chamar(cliente, modelo, [{"type": "text", "text": PROMPT_RESUMO + transcricao}])
    dados = _extrair_json(resposta)
    dados["transcricao"] = transcricao
    return dados
