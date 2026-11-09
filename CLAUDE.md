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
| 2 | Arquitetura, pipeline, pseudocódigo, bibliotecas | 12/11 | Pronta: docs/entrega2-documentacao-tecnica.pdf |
| 3 | Protótipo executável, repositório organizado, README | 29/11 | Protótipo inicial pronto (este repositório) |
| 4 | Código final comentado, relatório unificado, slides, vídeo de 10–15 min | — | A fazer |

Pendência: confirmar com os professores se podem aceitar a Entrega 1 com atraso e se pode usar API externa de IA.

## Decisões técnicas

- Python + NumPy para toda a matemática avaliada (implementação própria): convolução,
  Sobel separável, média local por imagem integral, sistema 8×8 com eliminação de Gauss,
  homografia, warp inverso bilinear, correção de iluminação, binarização adaptativa,
  flood fill iterativo (pilha explícita), rotulação.
- OpenCV só para extrair contornos (etapa 4) e como referência nos testes.
- Streamlit para a interface (abre no navegador, inclusive no celular).
- IA via SDK `anthropic` (variável ANTHROPIC_API_KEY no .env; modelo em MODELO_IA).
  Sem chave, o app funciona e só o resumo fica desligado.
- O flood fill iterativo corresponde 1:1 à recorrência FF(p, V) do relatório (seção 6.2),
  então valem os Teoremas 1–3 (terminação, correção, custo 4n + 1). Não trocar por
  cv2.floodFill/connectedComponents no código principal: a implementação própria é o que é avaliado.

## Regras de limpeza (segmentacao.limpar_manchas)

- Remove componentes que tocam a faixa de 1,5% da borda (resto da moldura do quadro).
- Remove componentes com área < A_MIN_MANCHA (60 px) que estão isoladas
  (nenhuma letra a menos de RAIO_VIZINHANCA = 16 px). Isso preserva pontos, ":" e pingos do "i".
- Blocos: imagem reduzida 4×, dilatação ~45 px, rotulação, retângulos envolventes.

## Estado atual

- 14 testes passando (`python -m pytest -q`), comparando com OpenCV.
- Testado só com a foto sintética (`gerar_amostra.py`): pipeline leva ~0,6 s.
- **Não testado com fotos reais** de quadros: próximo passo é juntar 20–30 fotos
  (quadro branco e negro, ângulos e luzes diferentes) em `amostras/` e calibrar `scanner/config.py`.
- **Resumo de IA não rodou de verdade** (só com cliente falso no teste).

## Próximos passos sugeridos

1. Testar com fotos reais e calibrar parâmetros.
2. Modo manual de cantos quando a detecção falhar (hoje usa a foto inteira).
3. Rodar a IA com chave real e ajustar os prompts em `scanner/ia.py`.
4. Entrega 4: relatório unificado (juntar docs/entrega1 e entrega2 + resultados), slides e vídeo.

Divisão sugerida: Artur → preprocessamento/geometria; Davi → realce/segmentação; Luiz → IA, app, testes, README.

## Convenções

- Código e textos em português do Brasil.
- Cada função matemática cita a seção do relatório que ela implementa.
- Toda função própria nova ganha um teste comparando com o OpenCV.
