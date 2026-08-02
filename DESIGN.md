# DESIGN.md

## 1. Direção visual

A interface deve transmitir precisão, clareza e controle. O sistema não deve parecer uma landing page promocional, nem usar excesso de cartões arredondados, ilustrações decorativas ou textos vagos.

O design deve se aproximar de uma ferramenta profissional de análise de dados, com:

- Fundo predominantemente branco;
- Texto principal em preto;
- Azul usado para ações, seleção, foco e destaque de dados;
- Bordas retas ou com arredondamento mínimo;
- Poucas sombras;
- Hierarquia visual baseada em espaçamento, tipografia e contraste;
- Informações organizadas em blocos funcionais;
- Gráficos ocupando espaço relevante na tela.

A prioridade é facilitar a leitura do conjunto de dados, a configuração das análises e a interpretação dos resultados.

---

## 2. Paleta de cores

### Cores principais

| Uso | Cor | Código |
|---|---|---|
| Fundo principal | Branco | `#FFFFFF` |
| Fundo secundário | Cinza muito claro | `#F6F8FA` |
| Texto principal | Preto suave | `#0B0D10` |
| Texto secundário | Cinza escuro | `#4B5563` |
| Azul principal | Azul de ação | `#2563EB` |
| Azul escuro | Azul para estados ativos | `#1D4ED8` |
| Azul claro | Fundo de seleção | `#EAF2FF` |
| Bordas | Cinza claro | `#D8DEE7` |
| Divisórias | Cinza neutro | `#E5E7EB` |

### Cores de estado

| Estado | Cor | Código |
|---|---|---|
| Sucesso | Verde escuro | `#15803D` |
| Atenção | Âmbar | `#B45309` |
| Erro | Vermelho | `#B91C1C` |
| Informação | Azul principal | `#2563EB` |

As cores de estado devem ser usadas apenas quando houver significado funcional. Não utilizar verde, vermelho ou amarelo como decoração.

---

## 3. Variáveis CSS recomendadas

```css
:root {
  --color-background: #ffffff;
  --color-surface: #f6f8fa;
  --color-surface-active: #eaf2ff;

  --color-text: #0b0d10;
  --color-text-secondary: #4b5563;
  --color-text-muted: #6b7280;

  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-primary-soft: #eaf2ff;

  --color-border: #d8dee7;
  --color-divider: #e5e7eb;

  --color-success: #15803d;
  --color-warning: #b45309;
  --color-danger: #b91c1c;

  --radius-small: 2px;
  --radius-default: 4px;

  --shadow-small: 0 1px 2px rgba(11, 13, 16, 0.08);

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;

  --sidebar-width: 248px;
  --content-max-width: 1600px;
}
```

Não criar raios maiores que `4px` sem uma justificativa funcional. Elementos como tabelas, painéis, modais e caixas de upload devem ter aparência predominantemente reta.

---

## 4. Tipografia

Utilizar uma fonte sem serifa de boa leitura. Priorizar:

```css
font-family: Inter, Arial, Helvetica, sans-serif;
```

Caso a fonte Inter não esteja instalada, utilizar a pilha de fontes do sistema.

### Escala tipográfica

| Elemento | Tamanho | Peso |
|---|---:|---:|
| Título da página | `28px` | `700` |
| Título de seção | `20px` | `650` |
| Título de painel | `16px` | `600` |
| Texto comum | `14px` | `400` |
| Label de campo | `13px` | `600` |
| Texto auxiliar | `12px` | `400` |
| Métrica principal | `30px` | `700` |

Evitar títulos excessivamente grandes. A interface deve parecer uma aplicação de trabalho, não uma página de publicidade.

### Regras de escrita

Os textos da interface devem ser específicos.

Evitar:

- “Explore seus dados”;
- “Descubra insights incríveis”;
- “Transforme seus dados”;
- “Comece sua jornada”;
- “Resultados inteligentes”.

Preferir:

- “Envie um arquivo CSV”;
- “Selecione a coluna de data”;
- “Escolha a variável alvo”;
- “Defina o intervalo da análise”;
- “Executar estatística descritiva”;
- “Comparar modelos”;
- “Filtrar registros exibidos”.

---

## 5. Estrutura principal da aplicação

A aplicação deve utilizar uma estrutura com:

1. Barra lateral fixa;
2. Cabeçalho superior compacto;
3. Área central de conteúdo;
4. Painel opcional de configuração ou filtros;
5. Área ampla para tabelas e gráficos.

### Estrutura sugerida

```text
┌──────────────────────────────────────────────────────────────┐
│ Logo / nome       Dataset ativo         Ajuda / usuário      │
├───────────────┬──────────────────────────────────────────────┤
│ Navegação     │ Título da página                              │
│               │ Descrição objetiva                            │
│ Upload        │                                               │
│ Dados         │ Conteúdo principal                            │
│ Estatística   │                                               │
│ Séries        │                                               │
│ Modelos       │                                               │
│ Clusterização │                                               │
│ Relatório     │                                               │
└───────────────┴──────────────────────────────────────────────┘
```

A barra lateral deve ter largura aproximada de `248px` em telas grandes.

---

## 6. Barra lateral

A barra lateral deve utilizar fundo branco ou preto, dependendo da versão escolhida.

### Versão recomendada

- Fundo: `#0B0D10`;
- Texto padrão: `#D1D5DB`;
- Item ativo: fundo azul `#2563EB`;
- Ícones: brancos ou cinza claro;
- Divisórias discretas;
- Sem cartões internos;
- Sem botões em formato de cápsula.

Os itens devem ter altura entre `40px` e `44px`, com raio de `2px`.

Exemplo:

```text
DADOSCOPE

[ Upload de dados ]
[ Visão geral    ]
[ Estatística    ]
[ Séries temporais ]
[ Modelos        ]
[ Clusterização  ]
[ Relatório      ]
```

O nome do produto deve aparecer com tipografia forte e simples. Não adicionar slogan dentro da barra lateral.

---

## 7. Cabeçalho superior

O cabeçalho deve ser compacto, com altura aproximada de `56px`.

Elementos recomendados:

- Nome do conjunto de dados atual;
- Quantidade de linhas e colunas;
- Estado do processamento;
- Botão para trocar arquivo;
- Acesso à ajuda;
- Menu do usuário, caso exista autenticação.

Exemplo:

```text
vendas_2026.csv    18.420 linhas · 14 colunas    Processamento concluído
```

Não usar uma barra superior muito alta ou com elementos decorativos.

---

## 8. Página de upload

A página inicial deve ter uma área de upload centralizada, mas sem aparência excessivamente arredondada.

### Caixa de upload

- Fundo branco;
- Borda tracejada de `1px`;
- Cor da borda: `#AAB4C3`;
- Raio: `4px`;
- Altura aproximada: `240px`;
- Ícone simples de arquivo;
- Botão azul retangular;
- Texto direto.

Texto recomendado:

```text
Envie um arquivo para análise

Formatos aceitos: CSV e XLSX
Tamanho máximo: 20 MB
```

Botão:

```text
Selecionar arquivo
```

Texto após o upload:

```text
Arquivo carregado: vendas_2026.csv
18.420 linhas · 14 colunas
```

Não usar textos como “Arraste seus dados e veja a mágica acontecer”.

---

## 9. Prévia do conjunto de dados

Após o upload, exibir uma página com:

- Nome do arquivo;
- Número de linhas;
- Número de colunas;
- Quantidade de valores ausentes;
- Tipos identificados;
- Prévia das primeiras linhas;
- Avisos de qualidade.

### Painel de resumo

Utilizar uma faixa horizontal com métricas, em vez de vários cartões grandes.

```text
Linhas: 18.420 | Colunas: 14 | Numéricas: 8 | Categóricas: 5 | Datas: 1
```

Cada métrica pode ser separada por divisórias verticais.

### Tabela de prévia

A tabela deve:

- Ocupar a maior largura disponível;
- Ter cabeçalho fixo;
- Permitir rolagem horizontal;
- Exibir tipos abaixo ou ao lado do nome da coluna;
- Destacar valores ausentes;
- Ter linhas compactas;
- Usar bordas apenas entre linhas ou colunas necessárias.

Exemplo de cabeçalho:

```text
valor_total
numérico
```

Não usar bordas arredondadas em cada célula.

---

## 10. Seleção do tipo de análise

Os tipos de análise devem ser exibidos em uma lista ou grade de opções retangulares.

Cada opção deve informar claramente:

- Nome da análise;
- Quando utilizar;
- Quais colunas são necessárias;
- Resultado produzido.

Exemplo:

```text
ESTATÍSTICA DESCRITIVA

Resume distribuição, valores centrais,
dispersão e dados ausentes.

Necessário: ao menos uma coluna numérica
Resultado: tabelas, histogramas e correlações
```

O item selecionado deve usar:

- Borda azul de `2px`;
- Fundo `#EAF2FF`;
- Título em azul escuro;
- Ícone azul.

Não criar cartões com raio alto ou sombra intensa.

---

## 11. Formulários de configuração

Os formulários devem ficar em uma coluna lateral ou em uma área superior compacta.

### Campos

- Altura: `40px`;
- Borda: `1px solid #D8DEE7`;
- Raio: `2px`;
- Fundo branco;
- Texto preto;
- Foco azul;
- Label acima do campo;
- Texto auxiliar abaixo apenas quando necessário.

### Exemplo

```text
Coluna de data
[ data_venda                  ]

Variável analisada
[ valor_total                 ]

Intervalo
[ 01/01/2026 ] até [ 30/06/2026 ]

[ Executar análise ]
```

O botão principal deve ser azul, retangular e com raio de `2px`.

O botão secundário deve ter fundo branco e borda preta ou cinza escuro.

---

## 12. Botões

### Botão principal

```css
.button-primary {
  background: #2563eb;
  color: #ffffff;
  border: 1px solid #2563eb;
  border-radius: 2px;
  min-height: 40px;
  padding: 0 16px;
  font-weight: 600;
}
```

### Botão secundário

```css
.button-secondary {
  background: #ffffff;
  color: #0b0d10;
  border: 1px solid #0b0d10;
  border-radius: 2px;
  min-height: 40px;
  padding: 0 16px;
  font-weight: 600;
}
```

### Botão de perigo

Utilizar apenas para ações destrutivas, como remover conjunto de dados.

Não utilizar botões em formato de cápsula. Não usar gradientes.

---

## 13. Gráficos

Os gráficos são o elemento central da interface.

### Regras gerais

Cada gráfico deve possuir:

- Título descritivo;
- Subtítulo com o intervalo analisado;
- Nome dos eixos;
- Unidade;
- Legenda apenas quando necessária;
- Tooltip;
- Botões de filtro próximos;
- Opção de redefinir zoom;
- Informação de amostragem, caso usada.

Exemplo de título:

```text
Valor total por dia
01/01/2026 a 30/06/2026 · 181 pontos
```

Evitar:

- “Gráfico 1”;
- “Resultados”;
- “Análise visual”;
- Títulos sem indicar a variável.

### Cores dos gráficos

A identidade dos gráficos deve usar fundo branco e elementos visuais em azul ou tons derivados da paleta principal.

Sequência permitida:

```text
#2563EB
#1D4ED8
#60A5FA
#1E40AF
#93C5FD
#3B82F6
```

Não utilizar preto como cor principal dentro dos gráficos. Diferenciar séries por tons de azul, espessura, marcadores e padrões de linha.

Todo texto interno do gráfico deve ser azul (`#2563EB`). Essa regra inclui:

- Títulos e subtítulos;
- Nomes dos eixos;
- Valores e marcações dos eixos;
- Legendas;
- Anotações e valores exibidos sobre os dados;
- Escalas e barras de cor;
- Tooltips e rótulos de hover;
- Seletores, controles e botões da biblioteca de gráficos.

É proibido utilizar texto preto dentro dos gráficos, inclusive em tooltips, menus ou elementos criados automaticamente pela biblioteca.

### Fundo

- Fundo do gráfico e da área de plotagem: branco `#FFFFFF`;
- Linhas de grade: azul muito claro `#DBEAFE`;
- Texto dos eixos: azul `#2563EB`;
- Linha principal: azul `#2563EB`;
- Linhas secundárias: outros tons de azul;
- Marcadores: azuis, pequenos e discretos;
- Tooltips: fundo branco, borda azul e texto azul.

---

## 14. Filtros por intervalo

Os filtros devem aparecer acima do gráfico ou em um painel lateral.

Para dados numéricos:

```text
Valor mínimo [ 0        ]
Valor máximo [ 10.000   ]
```

Para datas:

```text
De [ 01/01/2026 ] até [ 30/06/2026 ]
```

Para categorias:

```text
Região
[x] Nordeste
[x] Sudeste
[ ] Sul
```

O gráfico deve ser atualizado sem recarregar a página inteira.

Os filtros ativos devem aparecer de forma resumida:

```text
Filtros ativos: Região = Nordeste · Valor total = 500 a 5.000
```

Utilizar texto e divisórias, não uma coleção excessiva de chips arredondados.

---

## 15. Estatística descritiva

A página deve dividir os resultados em:

1. Resumo do conjunto;
2. Distribuição;
3. Valores ausentes;
4. Correlação;
5. Valores extremos.

### Resumo numérico

Utilizar tabela:

| Variável | Média | Mediana | Desvio padrão | Mínimo | Máximo |
|---|---:|---:|---:|---:|---:|

### Distribuição

Exibir histograma com seletor de variável.

### Correlação

Utilizar matriz com escala branco, azul claro e azul principal. Todos os textos, valores, nomes e tooltips da matriz devem permanecer azuis.

### Texto interpretativo

Exemplo:

```text
A variável valor_total possui média de R$ 1.284,30 e mediana de
R$ 932,10. A diferença entre essas medidas indica influência de
valores altos na distribuição.
```

Evitar:

```text
Este gráfico fornece insights importantes sobre os dados.
```

---

## 16. Séries temporais

A página de séries temporais deve priorizar o gráfico principal.

Estrutura recomendada:

```text
[ Configuração da série ]
[ Gráfico principal em largura total ]
[ Tendência | Sazonalidade | Resíduos ]
[ Métricas e observações ]
```

O gráfico deve permitir:

- Zoom;
- Seleção de intervalo;
- Alteração de frequência;
- Ativação de média móvel;
- Comparação entre série original e previsão;
- Visualização de pontos anormais.

As previsões devem usar linha azul tracejada e uma área clara para intervalo de confiança.

---

## 17. Machine Learning supervisionado

A interface deve separar claramente:

1. Configuração;
2. Treinamento;
3. Comparação;
4. Avaliação;
5. Interpretação.

### Comparação de modelos

Utilizar tabela:

| Modelo | Métrica principal | Tempo | Status |
|---|---:|---:|---|
| Random Forest | 0,84 | 2,1 s | Concluído |
| Regressão logística | 0,78 | 0,4 s | Concluído |

O melhor resultado pode ser marcado com uma barra azul lateral ou texto “Melhor resultado nesta divisão”.

Não utilizar troféus, medalhas ou elementos decorativos.

### Métricas

Exibir as métricas principais em uma faixa horizontal:

```text
Acurácia 0,84 | Precisão 0,81 | Recall 0,79 | F1-score 0,80
```

A matriz de confusão deve utilizar tons de azul.

---

## 18. Clusterização

A página deve permitir selecionar variáveis antes da execução.

Resultados:

- Gráfico de dispersão;
- Quantidade de registros por grupo;
- Médias por grupo;
- Silhouette Score;
- Tabela de características.

Os grupos devem usar cores diferenciadas, mas manter o azul como referência principal.

Exemplo de texto:

```text
O Grupo 2 concentra clientes com maior valor de compra e menor tempo
de entrega. Essa descrição é baseada nas médias das variáveis selecionadas.
```

Não utilizar rótulos como “clientes premium” sem uma regra explicitamente definida.

---

## 19. Relatório visual

O relatório deve parecer uma página técnica organizada para leitura e exportação.

Estrutura:

```text
Título do relatório
Arquivo analisado
Período
Data de geração

1. Resumo dos dados
2. Configurações utilizadas
3. Principais resultados
4. Gráficos
5. Interpretação
6. Limitações
```

Cada seção deve ser separada por espaçamento e linha horizontal. Evitar colocar todo o relatório dentro de um grande cartão arredondado.

---

## 20. Mensagens e estados

### Carregamento

Texto recomendado:

```text
Processando 18.420 registros...
```

Para treinamento:

```text
Treinando Random Forest...
```

### Sucesso

```text
Análise concluída com 18.420 registros.
```

### Aviso

```text
A coluna satisfação possui 14% de valores ausentes.
Escolha como esses registros devem ser tratados.
```

### Erro

```text
Não foi possível usar data_venda como coluna temporal.
27 valores não puderam ser convertidos para data.
```

Evitar mensagens genéricas como:

```text
Algo deu errado.
```

---

## 21. Modais

Usar modal apenas quando a ação bloquear o fluxo ou exigir confirmação.

Exemplos:

- Excluir conjunto de dados;
- Cancelar processamento;
- Confirmar substituição de arquivo.

Características:

- Fundo branco;
- Borda de `1px`;
- Raio de `2px`;
- Sombra discreta;
- Título direto;
- Ações alinhadas à direita.

Não usar modais para mensagens informativas simples.

---

## 22. Ícones

Utilizar ícones lineares e simples.

Ícones recomendados:

- Upload;
- Tabela;
- Gráfico de barras;
- Linha temporal;
- Modelo;
- Agrupamento;
- Documento;
- Filtro;
- Download;
- Aviso.

Os ícones devem complementar o texto, não substituí-lo.

Não utilizar ícones coloridos de forma aleatória.

---

## 23. Espaçamento e densidade

A interface pode ser relativamente densa, pois lida com tabelas, filtros e gráficos.

Regras:

- Margem externa do conteúdo: `24px` a `32px`;
- Espaço entre seções: `32px`;
- Espaço entre label e campo: `8px`;
- Espaço entre campos: `16px`;
- Altura de linha da tabela: `40px`;
- Cabeçalho de tabela: `44px`;
- Painéis: padding de `16px` ou `24px`.

Não utilizar espaços excessivos que obriguem o usuário a rolar sem necessidade.

---

## 24. Bordas e sombras

### Bordas

Utilizar bordas para:

- Separar painéis;
- Delimitar tabelas;
- Identificar campos;
- Mostrar seleção;
- Organizar relatórios.

Padrão:

```css
border: 1px solid #d8dee7;
border-radius: 2px;
```

### Sombras

Utilizar sombra apenas quando houver sobreposição:

- Dropdowns;
- Menus;
- Modais;
- Tooltips.

Não aplicar sombra em todos os painéis.

---

## 25. Responsividade

### Desktop

A experiência principal deve ser otimizada para telas a partir de `1280px`.

### Tablet

- Barra lateral recolhível;
- Painel de configuração acima dos gráficos;
- Tabelas com rolagem horizontal.

### Celular

O sistema deve continuar utilizável, mas não precisa ocultar informações importantes.

- Menu lateral convertido em gaveta;
- Campos em uma coluna;
- Gráficos com altura mínima de `320px`;
- Tabelas com rolagem horizontal;
- Métricas em linhas compactas;
- Botões principais em largura total quando necessário.

---

## 26. Acessibilidade

- Contraste mínimo adequado;
- Foco visível em azul;
- Labels associados aos campos;
- Navegação por teclado;
- Texto alternativo em ícones funcionais;
- Não depender apenas de cor para indicar estado;
- Gráficos acompanhados por resumo textual;
- Tamanho mínimo de fonte de `12px`;
- Área clicável mínima de `40px`.

Exemplo de foco:

```css
:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}
```

---

## 27. Regras para implementação por agentes

Ao alterar a interface, o agente deve:

1. Preservar a paleta branca, preta e azul;
2. Não adicionar gradientes;
3. Não criar botões em formato de cápsula;
4. Não usar raio maior que `4px` sem justificativa;
5. Não adicionar sombras em todos os elementos;
6. Não substituir textos específicos por frases promocionais;
7. Não reduzir o espaço destinado aos gráficos;
8. Não esconder informações importantes atrás de tooltips;
9. Manter tabelas legíveis e funcionais;
10. Preservar consistência entre páginas;
11. Priorizar componentes HTML sem dependência pesada;
12. Usar JavaScript para interações, filtros e atualização dinâmica;
13. Verificar contraste e estados de foco;
14. Testar a interface com conjuntos de dados pequenos e grandes;
15. Não alterar a identidade visual sem atualizar este arquivo.

---

## 28. Componentes que devem ser evitados

Evitar:

- Cartões com raio de `16px` ou mais;
- Botões em formato de cápsula;
- Gradientes;
- Ícones ilustrativos grandes;
- Fundos com formas abstratas;
- Excesso de cores;
- Sombras fortes;
- Animações longas;
- Textos promocionais;
- Grandes áreas vazias;
- Gráficos dentro de cartões pequenos;
- Informações escondidas apenas em hover;
- Muitos chips para representar filtros;
- Bordas arredondadas em tabelas;
- Cards separados para cada número simples.

---

## 29. Exemplo de página de resultados

```text
SÉRIE TEMPORAL — VALOR TOTAL

Arquivo: vendas_2026.csv
Período: 01/01/2026 a 30/06/2026
Frequência: diária

┌────────────────────────────────────────────────────────────┐
│ Coluna de data   Variável       Frequência     Intervalo   │
│ data_venda       valor_total    Diária         01/01–30/06 │
│                                      [ Atualizar análise ] │
└────────────────────────────────────────────────────────────┘

VALOR TOTAL POR DIA
181 pontos · média móvel de 7 dias

┌────────────────────────────────────────────────────────────┐
│                                                            │
│                     GRÁFICO PRINCIPAL                      │
│                                                            │
└────────────────────────────────────────────────────────────┘

Média: R$ 1.284,30 | Máximo: R$ 7.892,10 | Tendência: +8,4%

A série apresentou crescimento entre março e maio. Os maiores valores
foram observados em 12/04, 03/05 e 18/05.
```

Esse padrão deve orientar as demais páginas da aplicação.
