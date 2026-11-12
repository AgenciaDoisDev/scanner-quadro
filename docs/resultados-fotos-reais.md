# Teste com fotos reais (atualizado em 11/11/2026)

O pipeline foi testado com 11 fotos reais de quadros com licença livre, baixadas do Wikimedia
Commons (`amostras/reais/`, créditos em `amostras/reais/CREDITOS.md`), e com a foto sintética.
São 6 quadros brancos e 5 quadros negros/verdes, com pessoas na frente, perspectiva, reflexo
e fotos fechadas (close).

Cada imagem em `docs/resultados/` mostra: foto com os cantos marcados (vermelho) |
binarização | scan final com os blocos (azul). Os cantos foram marcados à mão, como o
usuário faz no app; nas fotos fechadas foi usada a foto inteira.

## Resultado por foto

| Foto | Situação | Tipo de quadro | Blocos | Observação |
| --- | --- | --- | --- | --- |
| branco_01 | close, professor na frente | branco ✔ | 1 | pessoa aparece no scan |
| branco_02 | close, duas pessoas | branco ✔ | 2 | pessoas aparecem no scan |
| branco_03 | quadro inteiro, pessoa e planta na frente | branco ✔ | 1 | pessoa aparece no scan |
| branco_04 | idem | branco ✔ | 5 | desenhos separados em blocos |
| branco_05 | quadro em cavalete, exercícios | branco ✔ | 18 | cada resposta emoldurada vira um bloco |
| branco_06 | quadro largo, texto miúdo e denso | branco ✔ | 2 | texto miúdo preservado |
| negro_01 | close de quadro verde, 3 colunas | negro ✔ | 7 | bom |
| negro_02 | quadro verde com moldura de madeira | negro ✔ | 7 | ótimo |
| negro_03 | sala com 3 painéis | negro ✔ | 2 | linha divisória vira um bloco grande |
| negro_04 | close de giz | negro ✔ | 16 | bom |
| negro_05 | anfiteatro, plateia na frente | negro ✔ | 1 | escrita densa: um bloco só |
| sintética | — | branco ✔ | 6 | título, fórmulas, coordenadas, composição e desenho separados |

**Tipo de quadro:** 12 de 12. **Tempo:** menos de 1 s por foto.

## O que mudou no código depois dos testes

1. **Cantos marcados pelo usuário.** O usuário clica nos 4 cantos do quadro no app. A detecção
   automática da primeira versão errava quando a moldura encostava em outras bordas.
2. **Quadro negro pela assimetria** (`realce.e_quadro_negro`). A regra "média < 100" falhava com
   quadro verde iluminado. Agora usa o sinal da assimetria γ = E[(f − μ)³] / σ³ dos tons: a
   escrita é a cauda do histograma (escura no branco, γ < 0; clara no negro, γ > 0). Nas 12
   fotos, branco ficou entre −0,6 e −2,1 e negro entre +0,9 e +4,6.
3. **Fundo em duas passadas** (`realce.corrigir_iluminacao`): b₁ = média(f), b = média(max(f, b₁)).
   A segunda passada tira a tinta da estimativa do fundo.
4. **Limpeza por vizinhança** (`segmentacao.limpar_manchas`): componente com ao menos 25 px é
   escrita; de 4 a 24 px só fica se estiver a até 12 px de escrita; menos de 4 px sai sempre.
   Com 40 ou 60 px de corte, o texto miúdo de branco_06 sumia.
5. **Blocos** com dilatação mais larga na horizontal (25 × 51 px) e mínimo de 75 px de escrita
   forte.

## Limitações conhecidas

- **Pessoa na frente do quadro** continua no scan (vira um borrão preto).
- **Linhas divisórias** do quadro podem virar um bloco grande (negro_03).
- **Escrita densa** vira um bloco só (negro_05). Para a IA não é problema: ela recebe o quadro.
- As fotos são de outras instituições. Ainda vale testar com fotos dos quadros da UNIFACS.
