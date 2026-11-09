# Resumo da conversa — Projeto A3 (Scanner de Quadro com IA)

Resumo completo da conversa em que o projeto foi planejado, documentado e prototipado
(04/11/2026 a 09/11/2026). Serve para continuar o trabalho no VS Code.
O `CLAUDE.md` traz a versão curta, que o Claude lê sozinho ao abrir a pasta.

---

## 1. Ponto de partida (04/11)

- Disciplina: **Estruturas Matemáticas e Computação Gráfica**, UNIFACS, 2026.2.
- Professores: Alberlan Lopes, Inácio Borges, Norberto Maciel.
- Grupo (máx. 3): **Artur Jansen Almeida de Souza**, **Davi Jansen Almeida de Souza**, **Luiz**.
- Situação em 04/11: grupo montado, sem tema. O prazo do tema (22/10) e o da Entrega 1 (29/10) já tinham passado.
- Diretrizes do professor: `docs/diretrizes-A3.pdf`.

### O que o professor exige
- Aplicação prática de visão computacional que resolva um problema real (do cotidiano ou do setor produtivo).
- **Pilar 1 — Álgebra Linear:** imagem como matriz e vetores; filtros de convolução (bordas e suavização);
  transformações com matrizes homogêneas (translação, escala, rotação); mapeamento de coordenadas.
- **Pilar 2 — Indução e Recorrência:** algoritmo (flood fill, segmentação recursiva etc.) com formulação
  por recorrência, caso base e passo indutivo.
- Bibliotecas como OpenCV e NumPy são permitidas, desde que a matemática seja documentada.

### Cronograma
| Entrega | O que é | Prazo |
| --- | --- | --- |
| 1 — Modelagem e definição teórica | Relatório PDF: problema, justificativa, técnicas e demonstração matemática formal | 29/10 (atrasada) |
| 2 — Engenharia e documentação técnica | PDF: diagrama de arquitetura, pipeline, pseudocódigo e bibliotecas | 12/11 |
| 3 — Protótipo funcional | Aplicação executável, repositório organizado e README; demonstração processando imagens | 29/11 |
| 4 — Apresentação final | Código final comentado, relatório unificado, slides e vídeo de 10–15 min | ver diretrizes |

---

## 2. Escolha do tema

1. Primeiro escolhemos o **corretor automático de gabaritos por foto**, e a Entrega 1 foi escrita para ele.
2. Esse tema foi **descartado**: na faculdade as provas são de marcar letra ou discursivas, e a folha de bolhas é coisa do ENEM.
3. Outras opções consideradas: medidor de objetos por foto (com folha A4 como régua), detector de vagas
   de estacionamento e contador de peças/comprimidos.
4. **Tema final: Scanner de Quadro com IA.** O aluno fotografa o quadro da aula e o sistema:
   - endireita o quadro (homografia);
   - corrige a iluminação (sombra e reflexo);
   - binariza e remove manchas de apagador (flood fill);
   - separa o conteúdo em blocos;
   - manda os blocos para uma IA, que devolve tema, resumo e explicação da aula.

   A IA fica só no fim, como módulo complementar. **A nota vem do pipeline visual e da matemática.**

---

## 3. Entregas produzidas

Todas estão em `docs/` (PDF + markdown) e também como documentos editáveis no claude.ai:

| Documento | Arquivo | Editável no claude.ai |
| --- | --- | --- |
| Entrega 1 — Scanner de Quadro com IA | `docs/entrega1-relatorio.pdf` | https://claude.ai/artifact/Qat2K5j6J6gPivUnSNNBrL |
| Entrega 2 — Documentação técnica | `docs/entrega2-documentacao-tecnica.pdf` | https://claude.ai/artifact/3xRVqrFiwGMdvACMuq76tY |
| (descartado) Entrega 1 do gabarito | — | https://claude.ai/artifact/HMg1nk3AHogQNTwYtd5Mu6 |

### Entrega 1 — conteúdo
1. Situação-problema: fotos tortas e ruins do quadro.
2. Justificativa: legibilidade, estudo, acessibilidade, robustez e aderência à disciplina.
3. Objetivos geral e específicos.
4. Tabela das 8 etapas do pipeline com o fundamento matemático de cada uma.
5. **Álgebra Linear:** imagem como tensor M×N×3; tons de cinza como produto escalar (0,299R + 0,587G + 0,114B);
   convolução discreta; Gaussiano 3×3; Sobel (Gx, Gy, magnitude, separabilidade como produto externo);
   homografia 3×3 em coordenadas homogêneas; T, S e R como casos particulares; sistema 8×8 A h = b;
   condição det A ≠ 0; mapeamento inverso com H⁻¹ e interpolação bilinear; correção de iluminação
   f̂ = 255·min(1, f/b) com b = média k×k; binarização adaptativa (média local − C).
6. **Recorrência e Indução:** vizinhança-4; componente conexa; recorrência FF(p, V);
   Teorema 1 (terminação); Teorema 2 (correção, partes (i) e (ii) por indução);
   Teorema 3 (custo T(n) = 4n + 1, com prova da forma fechada); rotulação Lₖ com prova por indução;
   remoção de manchas por área; agrupamento em blocos por dilatação.
7. Módulo de IA, ferramentas, próximos passos e referências.

### Entrega 2 — conteúdo
1. Diagrama de arquitetura (`docs/arquitetura.png`) e tabela de módulos.
2. Pipeline com entrada, operação, saída e parâmetros iniciais de cada etapa.
3. Pseudocódigo de 9 algoritmos: pipeline, convolução, cantos, homografia, warp inverso,
   iluminação/binarização, flood fill iterativo, rotulação/limpeza, blocos e IA.
4. Bibliotecas: NumPy, OpenCV, Streamlit, Pillow, anthropic e pytest, com versão mínima e o que é implementação própria.
5. Estrutura do repositório, tratamento de erros e divisão de tarefas.

> Observação: a Entrega 2 lista `A_MIN_MANCHA = 15`; no protótipo o valor calibrado ficou **60**,
> com a regra de "isolamento" (seção 5). Vale atualizar o documento.

---

## 4. Protótipo (Entrega 3, versão inicial)

Este repositório. Para rodar:
```bash
pip install -r requirements.txt
python gerar_amostra.py        # gera amostras/quadro_sintetico.jpg
streamlit run app.py
python -m pytest -q            # 14 testes
```

| Arquivo | Função |
| --- | --- |
| `scanner/captura.py` | Lê a foto, corrige a rotação do celular, redimensiona para 1600 px |
| `scanner/preprocessamento.py` | Cinza, convolução, Gaussiano, Sobel separável, média local (imagem integral), dilatação |
| `scanner/geometria.py` | Cantos (contornos do OpenCV), eliminação de Gauss própria, homografia, warp inverso bilinear |
| `scanner/realce.py` | Detecção de quadro negro, correção de iluminação, binarização adaptativa |
| `scanner/segmentacao.py` | Flood fill iterativo, rotulação, limpeza de manchas, blocos |
| `scanner/ia.py` | Transcrição por bloco (até 6; acima disso manda o quadro inteiro), resumo em JSON |
| `scanner/pipeline.py` | Orquestrador `processar_foto` + `gerar_pdf` |
| `scanner/config.py` | Todos os parâmetros |
| `app.py` | Streamlit: arquivo/câmera/amostra, antes e depois, PDFs, resumo e abas por etapa |
| `tests/` | Comparações com o OpenCV, Teorema 3 e IA com cliente falso |

### Resultado com a foto sintética
- Cantos detectados corretamente; pipeline completo em cerca de 0,6 s.
- Moldura removida; 144 manchas removidas; pontos, ":" e pingos de "i" preservados.
- 3 blocos: título, fórmulas e coordenadas homogêneas/composição.

### Ajustes feitos durante os testes
- **Moldura:** componentes que tocam a faixa de 1,5% da borda são removidas.
- **Manchas:** uma regra só por área apagava pontos e ":". A regra final remove a componente se
  área < 60 px **e** não houver letra a até 16 px. Pontos perto de letras ficam, manchas isoladas saem.
- **Blocos:** imagem reduzida 4× e dilatação de ~45 px. Com 21 px saíam 56 blocos (palavras separadas).

---

## 5. Pendências e próximos passos

1. **Testar com fotos reais** dos quadros da faculdade (branco e negro, vários ângulos e luzes) e
   calibrar `scanner/config.py`. Até agora só foi testado com a foto sintética.
2. **Rodar a IA de verdade:** criar `.env` com `ANTHROPIC_API_KEY` e ajustar os prompts em `scanner/ia.py`.
   O nome do modelo vem de `MODELO_IA` (padrão `claude-sonnet-5-5`).
3. **Modo manual de cantos** quando a detecção falhar (hoje usa a foto inteira e mostra um aviso).
4. **Perguntar aos professores:** se aceitam a Entrega 1 com atraso e se pode usar API externa de IA.
5. Atualizar a Entrega 2 com os parâmetros calibrados.
6. **Entrega 4:** relatório unificado (Entregas 1 + 2 + resultados com fotos reais), slides e vídeo.
   As abas do app que mostram cada etapa servem para a demonstração ao vivo.

### Divisão sugerida
- **Artur:** `preprocessamento.py` e `geometria.py`.
- **Davi:** `realce.py` e `segmentacao.py`.
- **Luiz:** `ia.py`, `app.py`, testes e README.

---

## 6. Mensagem enviada ao grupo (modelo)

> Fechei o tema da A3: **Scanner de Quadro com IA**. A gente tira foto do quadro na aula (torta, com reflexo,
> do jeito que sempre sai) e o sistema endireita a imagem, limpa sombra e mancha de apagador, separa o
> conteúdo em blocos e uma IA resume e explica o assunto da aula.
> Cobre os dois pilares que valem 8 pontos: Álgebra Linear (convolução e homografia 3×3) e
> Recorrência/Indução (flood fill com prova por indução).
> Prazos: Entrega 2 em 12/11 e protótipo em 29/11.

---

## 7. Como continuar no VS Code

1. Crie o repositório vazio no GitHub e, dentro desta pasta:
   ```bash
   git remote add origin https://github.com/SEU_USUARIO/scanner-quadro.git
   git push -u origin main
   ```
2. Abra a pasta no VS Code. O Claude lê o `CLAUDE.md` automaticamente.
3. Para retomar, um bom primeiro pedido é:
   > "Leia o CLAUDE.md e o RESUMO-DA-CONVERSA.md. Quero testar o pipeline com fotos reais que coloquei em amostras/ e calibrar os parâmetros."
