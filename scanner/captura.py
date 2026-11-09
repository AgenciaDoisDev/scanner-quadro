"""Etapa 0 — captura: leitura da foto e redimensionamento."""
import io

import numpy as np
from PIL import Image, ImageOps

from . import config


def carregar(origem, lado_max=config.LADO_MAX):
    """Lê uma imagem (caminho, bytes ou arquivo aberto) e devolve uma matriz RGB M×N×3 uint8."""
    if isinstance(origem, (bytes, bytearray)):
        origem = io.BytesIO(origem)
    img = Image.open(origem)
    img = ImageOps.exif_transpose(img).convert("RGB")  # respeita a rotação do celular
    escala = lado_max / max(img.size)
    if escala < 1:
        novo = (round(img.width * escala), round(img.height * escala))
        img = img.resize(novo, Image.LANCZOS)
    return np.asarray(img, dtype=np.uint8)
