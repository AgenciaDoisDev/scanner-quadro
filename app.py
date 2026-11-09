"""Interface do Scanner de Quadro com IA.  Rodar com:  streamlit run app.py"""
import os

import numpy as np
import streamlit as st
from PIL import Image, ImageDraw

from scanner.captura import carregar
from scanner.pipeline import gerar_pdf, processar_foto

# carrega a chave da IA do arquivo .env, se existir
if os.path.exists(".env"):
    for linha in open(".env", encoding="utf-8"):
        if "=" in linha and not linha.strip().startswith("#"):
            k, v = linha.strip().split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))

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
    st.markdown("**Pipeline**\n\n1. Tons de cinza\n2. Gaussiano 3×3\n3. Sobel\n4. Cantos do quadro\n"
                "5. Homografia\n6. Iluminação + binarização\n7. Flood fill\n8. IA")

if arquivo is None:
    st.info("Envie a foto de um quadro pela barra lateral (ou use a amostra de teste).")
    st.stop()


@st.cache_data(show_spinner=False)
def rodar(dados, usar_ia):
    return processar_foto(carregar(dados), usar_ia=usar_ia)


with st.spinner("Processando…"):
    r = rodar(arquivo.read(), usar_ia)

for aviso in r["avisos"]:
    st.warning(aviso)

# ------------------------------------------------------------- antes e depois
c1, c2 = st.columns(2)
original = Image.fromarray(r["original"])
d = ImageDraw.Draw(original)
cantos = [tuple(map(float, p)) for p in r["cantos"]]
d.line(cantos + [cantos[0]], fill=(255, 40, 40), width=6)
c1.subheader("Foto original")
c1.image(original, caption="Em vermelho: cantos encontrados", use_container_width=True)
c2.subheader("Quadro tratado")
c2.image(r["scan"], caption=f"{r['manchas_removidas']} manchas removidas · "
         f"{len(r['blocos'])} blocos de conteúdo", use_container_width=True)

b1, b2 = st.columns(2)
b1.download_button("⬇️ Baixar PDF (escaneado)", gerar_pdf(r["scan"]), "quadro.pdf",
                   "application/pdf", use_container_width=True)
b2.download_button("⬇️ Baixar PDF (tons de cinza)", gerar_pdf(r["claro"]), "quadro_cinza.pdf",
                   "application/pdf", use_container_width=True)

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
            use_container_width=True)
    b.image(r["bordas"] * 255, caption="Bordas: Sobel após Gaussiano 3×3", use_container_width=True)
with t[1]:
    st.image(r["quadro_cor"], caption="Quadro retificado por warp inverso com H⁻¹ e interpolação bilinear",
             use_container_width=True)
with t[2]:
    st.image(r["claro"], caption="f̂ = 255 · min(1, f / b), com b = média 41×41 (fundo estimado)",
             use_container_width=True)
with t[3]:
    st.image(255 * (1 - r["binaria"]), caption="Limiar adaptativo: média local 25×25 − C",
             use_container_width=True)
with t[4]:
    blocos_img = Image.fromarray(r["scan"]).convert("RGB")
    d = ImageDraw.Draw(blocos_img)
    for (topo, esq, base, dir_), _ in r["blocos"]:
        d.rectangle((esq, topo, dir_, base), outline=(220, 0, 0), width=4)
    st.image(blocos_img, caption=f"{r['componentes']} componentes rotuladas por flood fill · "
             f"{r['manchas_removidas']} removidas · blocos em vermelho", use_container_width=True)
with t[5]:
    st.markdown("**Homografia H** (resolvida pelo sistema 8×8 com eliminação de Gauss)")
    st.code(np.array2string(r["H"], precision=5, suppress_small=True))
    st.markdown("**Tempo de cada etapa**")
    st.table({"etapa": list(r["tempos"]), "segundos": [f"{v:.2f}" for v in r["tempos"].values()]})
