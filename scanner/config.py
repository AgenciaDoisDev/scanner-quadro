"""Parâmetros do pipeline (Entrega 2, seção 2). Calibrados com as fotos de amostras/."""

LADO_MAX = 1600            # maior lado da foto após o redimensionamento (px)
LIMIAR_BORDA = 60          # limiar da magnitude do gradiente de Sobel (mapa de bordas)

K_ILUMINACAO = 41          # máscara k×k para estimar o fundo (correção de iluminação)
M_BINARIZACAO = 25         # máscara m×m da média local (binarização adaptativa)
C_BINARIZACAO = 10         # constante subtraída da média local

A_MIN_MANCHA = 25          # componente com área ≥ 25 px é escrita "forte"
A_MIN_PINGO = 4            # menor que 4 px é poeira e sai sempre
RAIO_VIZINHANCA = 12       # entre 4 e 24 px, fica só se houver escrita forte a até 12 px
FAIXA_BORDA = 0.03         # faixa junto à borda (3% do lado) apagada: resto da moldura

FATOR_BLOCOS = 4           # redução da imagem antes de agrupar blocos (acelera o flood fill)
DILATACAO_BLOCOS = (25, 51)  # dilatação (altura, largura) em px que une letras em blocos
AREA_MIN_BLOCO = 1500      # blocos menores que isso (px²) são descartados
TINTA_MIN_BLOCO = 75       # blocos com menos escrita forte que isso (px) são resto de mancha
MARGEM_BLOCO = 12          # margem extra ao recortar cada bloco (px)

MAX_BLOCOS_IA = 8          # acima disso, a IA recebe o quadro inteiro em vez dos recortes
