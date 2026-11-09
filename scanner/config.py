"""Parâmetros do pipeline (Entrega 2, seção 2). Valores iniciais, a calibrar com fotos reais."""

LADO_MAX = 1600            # maior lado da foto após o redimensionamento (px)
LIMIAR_BORDA = 60          # limiar da magnitude do gradiente de Sobel
AREA_MIN_QUADRO = 0.20     # o quadro deve ocupar ao menos 20% da foto
TOLERANCIA_POLIGONO = 0.02 # tolerância da aproximação poligonal (fração do perímetro)

K_ILUMINACAO = 41          # máscara k×k para estimar o fundo (correção de iluminação)
M_BINARIZACAO = 25         # máscara m×m da média local (binarização adaptativa)
C_BINARIZACAO = 10         # constante subtraída da média local

A_MIN_MANCHA = 60          # componentes menores que isso (px) e isoladas são manchas
RAIO_VIZINHANCA = 16       # pontos, pingos e acentos a até 16 px de uma letra são mantidos
FATOR_BLOCOS = 4           # redução da imagem antes de agrupar blocos (acelera o flood fill)
DILATACAO_BLOCOS = 45      # tamanho da dilatação que une letras em blocos (px na imagem cheia)
AREA_MIN_BLOCO = 1500      # blocos menores que isso (px²) são descartados
MARGEM_BLOCO = 12          # margem extra ao recortar cada bloco (px)

MAX_BLOCOS_IA = 6          # acima disso, a IA recebe o quadro inteiro em vez dos recortes
