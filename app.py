"""Interface do Scanner de Quadro com IA.  Rodar com:  streamlit run app.py"""
import os

import numpy as np
import streamlit as st
from PIL import Image, ImageDraw

from streamlit_image_coordinates import streamlit_image_coordinates

from scanner.captura import carregar
from scanner.geometria import ordenar_cantos
from scanner.pipeline import gerar_pdf, processar_foto

# cantos do quadro na amostra sintética (gerada por gerar_amostra.py)
CANTOS_AMOSTRA = [(232, 173), (1416, 256), (1346, 1061), (177, 959)]

# carrega a chave da IA do arquivo .env (no computador) ou dos Secrets (no Streamlit Cloud)
if os.path.exists(".env"):
    for linha in open(".env", encoding="utf-8"):
        if "=" in linha and not linha.strip().startswith("#"):
            k, v = linha.strip().split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))
try:
    for k in ("ANTHROPIC_API_KEY", "MODELO_IA"):
        if k in st.secrets:
            os.environ.setdefault(k, str(st.secrets[k]))
except Exception:  # sem arquivo de secrets: tudo bem
    pass

st.set_page_config(page_title="Scanner de Quadro com IA", page_icon="📝", layout="wide")
st.title("📝 Scanner de Quadro com IA")
st.caption("Projeto A3 — Estruturas Matemáticas e Computação Gráfica · UNIFACS 2026.2")

with st.sidebar:
    st.header("Foto do quadro")
    modo = st.radio("Origem", ["Enviar arquivo", "Câmera", "Amostra de teste"])
    arquivo = None
    if modo == "Enviar arquivo":
        arquivo = st.file_uploader("Foto (JPG ou PNG)", type=["jpg", "jpeg", "png"])
    elif modo == "Câmera":
        arquivo = st.camera_input("Tire a foto do quadro")
    else:
        caminho = os.path.join("amostras", "quadro_sintetico.jpg")
        if os.path.exists(caminho):
            arquivo = open(caminho, "rb")
        else:
            st.warning("Rode `python gerar_amostra.py` para criar a amostra.")
    usar_ia = st.toggle("Gerar resumo com IA", value=True)
    st.divider()
    st.markdown("**Pipeline**\n\n1. Tons de cinza\n2. Gaussiano 3×3\n3. Sobel\n4. Cantos (clique)\n"
                "5. Homografia\n6. Iluminação + binarização\n7. Flood fill\n8. IA")

if arquivo is None:
    st.info("Envie a foto de um quadro pela barra lateral (ou use a amostra de teste).")
    st.stop()

dados = arquivo.read()
rgb = carregar(dados)
alt, larg = rgb.shape[:2]

# ------------------------------------------------------------- etapa 4: cantos marcados pelo usuário
# Os cliques ficam guardados na sessão; trocar de foto zera a lista.
chave_foto = hash(dados)
if st.session_state.get("foto") != chave_foto:
    st.session_state.foto = chave_foto
    st.session_state.ultimo_clique = None
    st.session_state.pontos = list(CANTOS_AMOSTRA) if modo == "Amostra de teste" else []
pontos = st.session_state.pontos

st.subheader("1. Marque os 4 cantos do quadro")
st.caption("Clique nos 4 cantos, em qualquer ordem. Eles definem a homografia que endireita o quadro.")
LARG_TELA = 800
escala = LARG_TELA / larg
previa = Image.fromarray(rgb).resize((LARG_TELA, round(alt * escala)))
d = ImageDraw.Draw(previa)
pts = [(x * escala, y * escala) for x, y in pontos]
if len(pts) == 4:
    pts = [tuple(p) for p in ordenar_cantos(pts)]
    d.line(pts + [pts[0]], fill=(255, 40, 40), width=3)
for x, y in pts:
    d.ellipse((x - 7, y - 7, x + 7, y + 7), outline=(255, 40, 40), width=3)

clique = streamlit_image_coordinates(previa, key="cantos")
if clique and clique != st.session_state.ultimo_clique:
    st.session_state.ultimo_clique = clique
    if len(pontos) < 4:
        f = larg / clique["width"]  # da imagem na tela para a foto original
        pontos.append((clique["x"] * f, clique["y"] * f))
        st.rerun()

c1, c2, c3 = st.columns(3)
if c1.button("↩️ Desfazer último ponto", width="stretch", disabled=not pontos):
    pontos.pop()
    st.rerun()
if c2.button("🗑️ Limpar pontos", width="stretch", disabled=not pontos):
    pontos.clear()
    st.rerun()
if c3.button("Usar a foto inteira", width="stretch"):
    pontos[:] = [(0, 0), (larg - 1, 0), (larg - 1, alt - 1), (0, alt - 1)]
    st.rerun()

if len(pontos) < 4:
    st.info(f"Faltam {4 - len(pontos)} canto(s).")
    st.stop()


@st.cache_data(show_spinner=False)
def rodar(dados, cantos, usar_ia):
    return processar_foto(carregar(dados), cantos=np.array(cantos), usar_ia=usar_ia)


with st.spinner("Processando…"):
    r = rodar(dados, tuple(pontos), usar_ia)

st.divider()
st.subheader("2. Resultado")
for aviso in r["avisos"]:
    st.warning(aviso)

# ------------------------------------------------------------- antes e depois
c1, c2 = st.columns(2)
original = Image.fromarray(r["original"])
d = ImageDraw.Draw(original)
cantos = [tuple(map(float, p)) for p in r["cantos"]]
d.line(cantos + [cantos[0]], fill=(255, 40, 40), width=6)
c1.subheader("Foto original")
c1.image(original, caption="Em vermelho: cantos marcados", width="stretch")
c2.subheader("Quadro tratado")
c2.image(r["scan"], caption=f"{r['manchas_removidas']} manchas removidas · "
         f"{len(r['blocos'])} blocos de conteúdo", width="stretch")

b1, b2 = st.columns(2)
b1.download_button("⬇️ Baixar PDF (escaneado)", gerar_pdf(r["scan"]), "quadro.pdf",
                   "application/pdf", width="stretch")
b2.download_button("⬇️ Baixar PDF (tons de cinza)", gerar_pdf(r["claro"]), "quadro_cinza.pdf",
                   "application/pdf", width="stretch")

# ------------------------------------------------------------- resumo da IA
if r["ia"]:
    st.divider()
    st.header(f"🎓 {r['ia'].get('tema', 'Resumo da aula')}")
    st.subheader("Resumo")
    for item in r["ia"].get("resumo", []):
        st.markdown(f"- {item}")
    st.subheader("Explicação")
    st.write(r["ia"].get("explicacao", ""))
    with st.expander("Transcrição do quadro"):
        st.text(r["ia"].get("transcricao", ""))

# ------------------------------------------------------------- etapas (demonstração)
st.divider()
st.header("Etapas do pipeline")
t = st.tabs(["1–3. Cinza e bordas", "4–5. Homografia", "6. Iluminação", "6. Binarização",
             "7. Flood fill e blocos", "Matriz H e tempos"])
with t[0]:
    a, b = st.columns(2)
    a.image(r["cinza"].astype(np.uint8), caption="Tons de cinza: f = 0,299R + 0,587G + 0,114B",
            width="stretch")
    b.image(r["bordas"] * 255, caption="Bordas: Sobel após Gaussiano 3×3", width="stretch")
with t[1]:
    st.image(r["quadro_cor"], caption="Quadro retificado por warp inverso com H⁻¹ e interpolação bilinear",
             width="stretch")
with t[2]:
    st.image(r["claro"], caption="f̂ = 255 · min(1, f / b), com b = média 41×41 (fundo estimado)",
             width="stretch")
with t[3]:
    st.image(255 * (1 - r["binaria"]), caption="Limiar adaptativo: média local 25×25 − C",
             width="stretch")
with t[4]:
    blocos_img = Image.fromarray(r["scan"]).convert("RGB")
    d = ImageDraw.Draw(blocos_img)
    for (topo, esq, base, dir_), _ in r["blocos"]:
        d.rectangle((esq, topo, dir_, base), outline=(220, 0, 0), width=4)
    st.image(blocos_img, caption=f"{r['componentes']} componentes rotuladas por flood fill · "
             f"{r['manchas_removidas']} removidas · blocos em vermelho", width="stretch")
with t[5]:
    st.markdown("**Homografia H** (resolvida pelo sistema 8×8 com eliminação de Gauss)")
    st.code(np.array2string(r["H"], precision=5, suppress_small=True))
    st.markdown("**Tempo de cada etapa**")
    st.table({"etapa": list(r["tempos"]), "segundos": [f"{v:.2f}" for v in r["tempos"].values()]})
