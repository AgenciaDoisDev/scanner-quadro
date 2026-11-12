# Scanner de Quadro com IA

Projeto A3 — Estruturas Matemáticas e Computação Gráfica (UNIFACS, 2026.2)
Artur Jansen Almeida de Souza · Davi Jansen Almeida de Souza · Luiz

O aluno tira uma foto do quadro (torta, com reflexo e manchas). O sistema endireita o quadro
por homografia, corrige a iluminação, binariza, remove manchas com flood fill, separa o conteúdo
em blocos e, no fim, uma IA gera o tema, o resumo e a explicação da aula.

## Instalação

Requer Python 3.10 ou mais novo.

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt   # app + testes (só o app: requirements.txt)
```

## Execução

```bash
python gerar_amostra.py      # cria amostras/quadro_sintetico.jpg (foto de teste)
streamlit run app.py         # abre o app no navegador
```

Para usar pelo celular na mesma rede Wi-Fi, abra o endereço "Network URL" que o Streamlit mostra.

### Resumo com IA (opcional)

Copie `.env.example` para `.env` e preencha `ANTHROPIC_API_KEY`. Sem a chave, o app funciona
normalmente; apenas o resumo fica desligado. No Streamlit Cloud, a chave vai em
*Settings → Secrets*, no formato `ANTHROPIC_API_KEY = "..."`.

## Testes

```bash
python -m pytest -q
```

Os testes comparam as funções feitas pelo grupo com as equivalentes do OpenCV
(convolução, média local, homografia, warp e rotulação) e conferem o Teorema 3 (custo 4n + 1 do flood fill).

## Documentação

- `docs/entrega1-relatorio.pdf`: situação-problema e modelagem matemática
- `docs/entrega2-documentacao-tecnica.pdf`: arquitetura, pipeline, pseudocódigo e bibliotecas
- `docs/diretrizes-A3.pdf`: diretrizes do professor
- `CLAUDE.md`: contexto do projeto e decisões tomadas
- `RESUMO-DA-CONVERSA.md`: histórico completo do planejamento

## Estrutura

| Arquivo | O que faz | Relatório |
| --- | --- | --- |
| `scanner/captura.py` | Leitura e redimensionamento da foto | Etapa 0 |
| `scanner/preprocessamento.py` | Tons de cinza, convolução, Gaussiano, Sobel separável, média por imagem integral | Seções 5.2 e 5.3 |
| `scanner/geometria.py` | Ordenação dos cantos, sistema 8×8 com eliminação de Gauss, homografia, warp inverso bilinear | Seção 5.4 |
| `scanner/realce.py` | Correção de iluminação e binarização adaptativa | Seções 5.5 e 5.6 |
| `scanner/segmentacao.py` | Flood fill iterativo, rotulação, limpeza de manchas, blocos | Seção 6 |
| `scanner/ia.py` | Transcrição, tema, resumo e explicação via API | Seção 7 |
| `scanner/pipeline.py` | Orquestrador (PROCESSAR_FOTO) e exportação em PDF | Entrega 2, 3.1 |
| `scanner/config.py` | Parâmetros do pipeline | Entrega 2, seção 2 |
| `app.py` | Interface Streamlit, com antes/depois e cada etapa | — |

O pacote `scanner/` não usa o OpenCV: ele aparece só nos testes, como referência. Os cantos do quadro (etapa 4) são marcados pelo usuário, clicando na foto.
Toda a matemática avaliada (convolução, homografia, warp, flood fill e rotulação) é implementação própria em NumPy.
