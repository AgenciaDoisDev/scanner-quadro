"""Testa o módulo de IA com um cliente falso (não usa internet nem chave)."""
import sys
import types

import numpy as np

from scanner import ia


class _Bloco:
    type = "text"

    def __init__(self, text):
        self.text = text


class _Mensagens:
    def __init__(self):
        self.chamadas = []

    def create(self, model, max_tokens, messages):
        self.chamadas.append(messages)
        return types.SimpleNamespace(content=[_Bloco(
            'Claro! {"transcricao": "x\' = x + tx", "tema": "Transformações no plano", '
            '"resumo": ["Translação"], "explicacao": "Somar tx desloca o ponto."}')])


def test_resumir_com_ia(monkeypatch):
    msgs = _Mensagens()
    falso = types.ModuleType("anthropic")
    falso.Anthropic = lambda: types.SimpleNamespace(messages=msgs)
    monkeypatch.setitem(sys.modules, "anthropic", falso)

    img = np.full((50, 80), 255, np.uint8)
    blocos = [((0, 0, 50, 40), img[:, :40]), ((0, 40, 50, 80), img[:, 40:])]
    r = ia.resumir_com_ia(img, blocos)

    assert r["tema"] == "Transformações no plano"
    assert r["resumo"] == ["Translação"]
    assert "x' = x + tx" in r["transcricao"]
    assert len(msgs.chamadas) == 1  # uma chamada só, com os 2 blocos em ordem
    conteudo = msgs.chamadas[0][0]["content"]
    assert [c["type"] for c in conteudo] == ["text", "image", "text", "image", "text"]
    assert "ilegível" in conteudo[-1]["text"]
