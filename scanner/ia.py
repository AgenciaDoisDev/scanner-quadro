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

PROMPT = (
    "As imagens acima são de um quadro de sala de aula, já endireitado e limpo, em ordem "
    "de leitura. Responda APENAS com um JSON válido, em português do Brasil, com as chaves:\n"
    '  "transcricao": o que está escrito, fielmente, incluindo fórmulas em notação simples '
    "(desenhos e esquemas descritos em uma linha entre colchetes);\n"
    '  "tema": o assunto da aula em uma frase curta;\n'
    '  "resumo": lista de 3 a 7 tópicos curtos com os pontos principais;\n'
    '  "explicacao": explicação didática em 2 a 4 parágrafos, como para um colega que '
    "faltou à aula, com um exemplo.\n"
    "Se algum trecho estiver ilegível, escreva [ilegível] em vez de inventar."
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
    """Uma chamada só: manda os blocos em ordem de leitura (ou o quadro inteiro, se forem
    muitos) e recebe um dict com transcricao, tema, resumo (lista) e explicacao."""
    import anthropic  # importado aqui para o resto do sistema funcionar sem o SDK

    modelo = modelo or os.environ.get("MODELO_IA", MODELO_PADRAO)
    cliente = anthropic.Anthropic()

    conteudo = []
    if 0 < len(blocos) <= config.MAX_BLOCOS_IA:
        for i, (_, recorte) in enumerate(blocos, 1):
            conteudo += [{"type": "text", "text": f"Bloco {i}:"}, _imagem(recorte)]
    else:
        conteudo.append(_imagem(imagem_quadro))
    conteudo.append({"type": "text", "text": PROMPT})
    return _extrair_json(_chamar(cliente, modelo, conteudo, max_tokens=3000))
