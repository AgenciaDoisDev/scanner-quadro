# Contexto do projeto (para o Claude no VS Code)

Este arquivo resume a conversa em que o projeto foi planejado e o protótipo foi criado.
Leia antes de mexer no código.

## O que é

Projeto A3 da disciplina **Estruturas Matemáticas e Computação Gráfica** (UNIFACS, 2026.2).
Professores: Alberlan Lopes, Inácio Borges, Norberto Maciel.
Grupo: Artur Jansen Almeida de Souza, Davi Jansen Almeida de Souza, Luiz.

**Tema: Scanner de Quadro com IA.** O aluno fotografa o quadro da aula (torta, com reflexo,
sombra e manchas). O sistema endireita o quadro (homografia), corrige a iluminação, binariza,
remove manchas e separa o conteúdo em blocos (flood fill) e, no fim, uma IA gera tema, resumo
e explicação da aula. A IA é módulo complementar: a nota vem do pipeline visual e da matemática.

O tema anterior (corretor de gabaritos) foi descartado porque a faculdade não usa folha de bolhas.

## Exigências do professor (docs/diretrizes-A3.pdf)

- Pilar 1, Álgebra Linear: imagem como matriz, filtros de convolução, transformações com
  matrizes homogêneas, mapeamento de coordenadas.
- Pilar 2, Indução e Recorrência: algoritmo (flood fill) formulado por recorrência, com caso
  base e passo indutivo.
- Bibliotecas como OpenCV e NumPy são permitidas, desde que a matemática seja documentada.

| Entrega | Conteúdo | Prazo | Situação |
| --- | --- | --- | --- |
| 1 | Situação-problema, justificativa, técnicas, demonstração matemática | 29/10 (atrasada) | Pronta: docs/entrega1-relatorio.pdf |
| 2 | Arquitetura, pipeline, pseudocódigo, bibliotecas | 12/11 | Pronta e revisada em 11/11 (versão simplificada: cantos por clique, limpeza por vizinhança, seção 6 com fotos reais): docs/entrega2-documentacao-tecnica.pdf |
| 3 | Protótipo executável, repositório organizado, README | 29/11 | Protótipo inicial pronto (este repositório) |
| 4 | Código final comentado, relatório unificado, slides, vídeo de 10–15 min | — | A fazer |

Pendência: confirmar com os professores se podem aceitar a Entrega 1 com atraso e se pode usar API externa de IA.
Os professores (Alberlan e Norberto) não gostam de IA usada para fazer o projeto. Por isso, em 11/11 o código
foi simplificado de propósito para o grupo entender e defender. Manter simples: não reintroduzir detecção
automática de cantos nem regras elaboradas sem o grupo pedir.

## Decisões técnicas

- Python + NumPy para toda a matemática avaliada (implementação própria): convolução,
  Sobel separável, média local por imagem integral (janela k×k ou kh×kw), sistema 8×8 com
  eliminação de Gauss, homografia, warp inverso bilinear, correção de iluminação, binarização
  adaptativa, flood fill iterativo (pilha explícita), rotulação, assimetria dos tons.
- OpenCV só como referência nos testes (o pacote `scanner/` não usa).
- Cantos: o usuário clica nos 4 cantos no app (`streamlit-image-coordinates`);
  `geometria.ordenar_cantos` aceita qualquer ordem. Botão "usar a foto inteira" para closes.
  A detecção automática por Hough foi removida em 11/11 para simplificar.
- Quadro negro (realce.e_quadro_negro): assimetria γ > 0. Não voltar para "média < 100":
  quadro verde iluminado passa de 100.
- Iluminação: fundo em duas passadas, b₁ = média(f), b = média(max(f, b₁)) (ideia do Luiz).
- Streamlit para a interface (abre no navegador, inclusive no celular).
- IA via SDK `anthropic` (ANTHROPIC_API_KEY no .env; modelo em MODELO_IA). Uma chamada só,
  com os blocos em ordem de leitura (ou o quadro inteiro se > 8 blocos), devolvendo JSON;
  o prompt pede "[ilegível]" em vez de inventar (ideia do Luiz). Sem chave, só o resumo desliga.
- O flood fill iterativo corresponde 1:1 à recorrência FF(p, V) do relatório (seção 6.2),
  com vizinhança-4, então valem os Teoremas 1–3 (terminação, correção, custo 4n + 1). Não trocar
  por vizinhança-8 nem por cv2.floodFill/connectedComponents: a implementação própria é o que é avaliado.

## Regras de limpeza (segmentacao.limpar_manchas)

- Componente com área ≥ A_MIN_MANCHA (25 px) é escrita forte e fica.
- De A_MIN_PINGO (4 px) a 24 px fica só se houver escrita forte a até RAIO_VIZINHANCA (12 px):
  preserva pontos, ":" e pingos do "i". Menos de 4 px sai sempre.
  Com corte de 40 ou 60 px o texto miúdo (branco_06) some.
- Apaga a faixa de 3% junto à borda (resto da moldura). Com 1,5% a moldura da amostra
  sintética sobrava e virava um bloco do tamanho do quadro.
- Blocos: imagem reduzida 4×, dilatação 25 × 51 px (mais larga na horizontal), rotulação,
  retângulos envolventes; descarta blocos com menos de 75 px de escrita forte.

## Estado atual

- 18 testes passando (`python -m pytest -q`), comparando com OpenCV.
- Testado com 11 fotos reais do Wikimedia Commons (`amostras/reais/`) + a sintética, com os
  cantos marcados à mão: tipo de quadro certo em 12/12, < 1 s por foto.
  Detalhes e limitações em docs/resultados-fotos-reais.md.
- O clique nos cantos foi testado só com o AppTest do Streamlit, não num navegador de verdade.
- Falta testar com fotos dos quadros da UNIFACS.
- **Resumo de IA não rodou de verdade** (só com cliente falso no teste).

## Próximos passos sugeridos

1. Abrir o app no navegador e conferir o clique nos cantos (inclusive no celular).
2. Rodar a IA com chave real e ajustar o prompt em `scanner/ia.py`.
3. Pessoa na frente do quadro continua no scan.
4. Entrega 4: relatório unificado (juntar docs/entrega1 e entrega2 + resultados), slides e vídeo.

Divisão sugerida: Artur → preprocessamento/geometria; Davi → realce/segmentação; Luiz → IA, app, testes, README.

## Convenções

- Código e textos em português do Brasil.
- Cada função matemática cita a seção do relatório que ela implementa.
- Toda função própria nova ganha um teste comparando com o OpenCV.
