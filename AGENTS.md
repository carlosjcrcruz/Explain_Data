# AGENTS.md

## 1. Visão geral do projeto

Este projeto é uma aplicação web desenvolvida com **FastAPI**, HTML, CSS e JavaScript, criada para facilitar a compreensão de análises de dados por usuários que não necessariamente possuem conhecimento avançado em estatística, ciência de dados ou programação.

A aplicação deve permitir que o usuário:

1. Envie um arquivo contendo dados.
2. Visualize uma prévia do conjunto de dados.
3. Escolha o tipo de análise que deseja executar.
4. Configure os parâmetros necessários para a análise.
5. Execute a análise selecionada.
6. Visualize os resultados por meio de gráficos, métricas e explicações.
7. Altere o intervalo dos dados exibidos utilizando filtros baseados em colunas específicas.
8. Gere relatórios visuais compreensíveis.

O objetivo principal não é apenas calcular métricas, mas **apresentar os resultados de maneira clara, visual e acessível**.

---

## 2. Tecnologias principais

### Backend

* Python
* FastAPI
* Pydantic
* Pandas
* NumPy
* Scikit-learn
* Bibliotecas específicas para séries temporais, quando necessárias

### Frontend

* HTML
* CSS
* JavaScript
* Templates do FastAPI, quando utilizados pelo projeto
* Biblioteca de gráficos já adotada no projeto

Não adicionar frameworks ou bibliotecas sem necessidade. Antes de incluir uma dependência nova, verificar se a funcionalidade pode ser implementada com as tecnologias já existentes.

Caso ainda não exista uma biblioteca de gráficos definida, priorizar uma solução que permita:

* Gráficos interativos;
* Zoom;
* Seleção de intervalos;
* Atualização dinâmica;
* Tooltips;
* Filtros;
* Exportação da visualização, quando possível.

---

## 3. Tipos de análise

A aplicação deverá oferecer suporte aos seguintes grupos de análise.

### 3.1 Estatística descritiva

Deve permitir a geração de informações como:

* Quantidade de linhas e colunas;
* Tipos das variáveis;
* Valores ausentes;
* Valores únicos;
* Média;
* Mediana;
* Moda;
* Desvio padrão;
* Variância;
* Valores mínimos e máximos;
* Quartis;
* Distribuição dos dados;
* Correlação entre variáveis numéricas;
* Identificação preliminar de valores discrepantes.

Os resultados devem ser acompanhados por explicações simples. Não apresentar apenas tabelas ou números sem indicar o que eles representam.

Exemplo:

> A média representa o valor central aproximado da variável, enquanto o desvio padrão indica o quanto os valores costumam se afastar dessa média.

---

### 3.2 Séries temporais

As análises de séries temporais devem considerar a existência de uma coluna temporal e uma variável numérica observada ao longo do tempo.

Possíveis funcionalidades:

* Ordenação cronológica;
* Identificação de frequência temporal;
* Visualização da série;
* Média móvel;
* Tendência;
* Sazonalidade;
* Variação percentual;
* Comparação entre períodos;
* Decomposição da série;
* Detecção de valores anormais;
* Previsão de valores futuros;
* Avaliação de modelos de previsão.

Antes de executar a análise, permitir que o usuário selecione:

* Coluna de data ou tempo;
* Variável numérica que será analisada;
* Intervalo temporal;
* Frequência dos dados, quando não puder ser identificada automaticamente;
* Modelo ou técnica desejada;
* Horizonte de previsão, quando aplicável.

Nunca assumir automaticamente que uma coluna representa uma data apenas com base em seu nome. Validar a conversão dos valores.

---

### 3.3 Machine Learning supervisionado

O sistema deve oferecer análises supervisionadas para problemas de:

* Classificação;
* Regressão.

O usuário deve selecionar explicitamente a variável alvo.

Antes do treinamento, o sistema deve:

1. Identificar variáveis numéricas e categóricas.
2. Verificar valores ausentes.
3. Verificar se a variável alvo é válida.
4. Apresentar possíveis problemas nos dados.
5. Explicar as transformações aplicadas.
6. Separar dados de treinamento e teste.
7. Evitar vazamento de dados.

Os modelos devem ser apresentados por nomes compreensíveis. Quando possível, incluir uma breve explicação sobre suas características.

Exemplos de modelos:

#### Classificação

* Regressão logística;
* Árvore de decisão;
* Random Forest;
* K-Nearest Neighbors;
* Support Vector Machine.

#### Regressão

* Regressão linear;
* Árvore de regressão;
* Random Forest Regressor;
* K-Nearest Neighbors Regressor;
* Support Vector Regression.

As métricas devem ser adequadas ao tipo de problema.

Para classificação:

* Acurácia;
* Precisão;
* Recall;
* F1-score;
* Matriz de confusão.

Para regressão:

* MAE;
* MSE;
* RMSE;
* R².

Não afirmar que um modelo é bom apenas com base em uma única métrica. Apresentar as limitações da avaliação.

---

### 3.4 Clusterização e segmentação

As análises não supervisionadas devem permitir a identificação de grupos de registros com características semelhantes.

Possíveis técnicas:

* K-Means;
* Clusterização hierárquica;
* DBSCAN.

O usuário deve poder selecionar as variáveis utilizadas na segmentação.

Antes da execução:

* Utilizar apenas variáveis compatíveis;
* Tratar valores ausentes;
* Normalizar ou padronizar os dados quando necessário;
* Explicar a transformação realizada;
* Informar que os grupos são identificados matematicamente e precisam ser interpretados de acordo com o domínio dos dados.

Os resultados podem incluir:

* Quantidade de elementos por grupo;
* Médias das variáveis em cada grupo;
* Características predominantes;
* Gráfico de dispersão;
* Representação por PCA, quando houver muitas dimensões;
* Métricas auxiliares, como Silhouette Score.

Os grupos devem ser identificados de maneira neutra, como “Grupo 1”, “Grupo 2” e “Grupo 3”. Não atribuir significados comerciais, sociais ou comportamentais sem evidências presentes nos dados.

---

## 4. Fluxo principal da aplicação

O fluxo esperado é:

```text
Upload do arquivo
        ↓
Validação do arquivo
        ↓
Leitura e identificação das colunas
        ↓
Prévia dos dados
        ↓
Escolha do tipo de análise
        ↓
Configuração dos parâmetros
        ↓
Processamento no backend
        ↓
Retorno dos resultados
        ↓
Exibição de gráficos, métricas e explicações
        ↓
Aplicação de filtros e seleção de intervalos
        ↓
Geração do relatório visual
```

Cada etapa deve apresentar mensagens claras de sucesso, aviso ou erro.

---

## 5. Upload e validação de dados

Não assumir formatos de arquivo que ainda não estejam implementados no projeto.

Quando um formato for suportado, ele deve ser validado tanto pela extensão quanto pelo conteúdo.

A validação deve considerar:

* Formato do arquivo;
* Tamanho máximo permitido;
* Arquivo vazio;
* Cabeçalho ausente;
* Nomes de colunas duplicados;
* Tipos inconsistentes;
* Quantidade excessiva de linhas ou colunas;
* Valores ausentes;
* Caracteres inválidos;
* Problemas de codificação;
* Separador do arquivo;
* Colunas completamente vazias.

Nunca confiar apenas no nome ou na extensão enviada pelo usuário.

Os arquivos não devem ser executados como código.

Utilizar nomes internos seguros para arquivos temporários. Não utilizar diretamente o nome enviado pelo usuário em caminhos do sistema.

Quando possível, remover o arquivo temporário após o processamento.

---

## 6. Estrutura recomendada

Ao criar ou reorganizar o projeto, priorizar separação de responsabilidades.

```text
project/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── routes/
│   │   │   ├── upload.py
│   │   │   ├── descriptive.py
│   │   │   ├── time_series.py
│   │   │   ├── supervised.py
│   │   │   ├── clustering.py
│   │   │   └── reports.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── security.py
│   ├── schemas/
│   │   ├── analysis.py
│   │   ├── datasets.py
│   │   └── responses.py
│   ├── services/
│   │   ├── dataset_service.py
│   │   ├── descriptive_service.py
│   │   ├── time_series_service.py
│   │   ├── supervised_service.py
│   │   ├── clustering_service.py
│   │   └── report_service.py
│   ├── utils/
│   │   ├── data_validation.py
│   │   ├── preprocessing.py
│   │   └── serialization.py
│   ├── templates/
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
├── tests/
├── uploads/
├── requirements.txt
├── README.md
└── AGENTS.md
```

Essa estrutura é uma recomendação. Não reorganizar todo o projeto sem necessidade quando já existir uma arquitetura definida.

---

## 7. Responsabilidade das camadas

### Rotas

As rotas devem:

* Receber requisições;
* Validar os dados de entrada;
* Chamar os serviços;
* Retornar respostas;
* Tratar exceções previstas.

As rotas não devem concentrar toda a lógica de análise de dados.

### Serviços

Os serviços devem:

* Processar os dados;
* Executar análises;
* Treinar modelos;
* Calcular métricas;
* Preparar resultados;
* Gerar estruturas compatíveis com os gráficos.

### Schemas

Os schemas Pydantic devem definir:

* Parâmetros das análises;
* Configurações dos modelos;
* Filtros;
* Intervalos;
* Estrutura das respostas;
* Mensagens de erro.

### Frontend

O frontend deve:

* Coletar as escolhas do usuário;
* Validar campos básicos;
* Enviar requisições;
* Exibir carregamento;
* Renderizar gráficos;
* Atualizar filtros;
* Exibir mensagens de erro;
* Apresentar explicações sobre os resultados.

---

## 8. APIs e respostas

As respostas devem seguir uma estrutura consistente.

Exemplo:

```json
{
  "success": true,
  "message": "Análise concluída com sucesso.",
  "data": {
    "summary": {},
    "metrics": {},
    "charts": [],
    "interpretation": []
  },
  "warnings": []
}
```

Em caso de erro:

```json
{
  "success": false,
  "message": "Não foi possível executar a análise.",
  "error": {
    "code": "INVALID_TARGET_COLUMN",
    "details": "A coluna selecionada como alvo não foi encontrada."
  }
}
```

Não retornar diretamente exceções internas, caminhos do sistema, stack traces ou informações sensíveis.

Utilizar códigos HTTP adequados.

Exemplos:

* `200`: operação concluída;
* `201`: recurso criado;
* `400`: parâmetros inválidos;
* `404`: recurso ou conjunto de dados não encontrado;
* `413`: arquivo maior que o limite;
* `422`: erro de validação;
* `500`: erro interno inesperado.

---

## 9. Gráficos e filtros

Os gráficos devem ser tratados como parte central da aplicação.

Cada gráfico deve possuir, quando aplicável:

* Título;
* Nome dos eixos;
* Unidade de medida;
* Legenda;
* Tooltip;
* Descrição textual;
* Informação sobre filtros ativos;
* Opção de seleção de intervalo.

Os filtros podem utilizar:

* Intervalo de datas;
* Valores mínimos e máximos;
* Categorias;
* Grupos;
* Variáveis específicas;
* Faixas numéricas.

Quando o usuário alterar um intervalo, atualizar somente os dados necessários. Evitar recarregar toda a página.

Os filtros devem preservar os valores originais do conjunto de dados. Não modificar permanentemente o arquivo enviado.

O backend deve validar novamente todos os intervalos recebidos do frontend.

---

## 10. Relatórios visuais

O relatório deve apresentar os resultados de forma organizada e progressiva.

Estrutura recomendada:

1. Informações gerais do conjunto de dados;
2. Qualidade dos dados;
3. Configurações utilizadas;
4. Principais métricas;
5. Gráficos;
6. Interpretação dos resultados;
7. Alertas e limitações;
8. Possíveis próximos passos.

Evitar textos que garantam conclusões absolutas.

Utilizar termos como:

* “Os dados indicam”;
* “O resultado observado sugere”;
* “Dentro da amostra analisada”;
* “O modelo apresentou”;
* “Esta conclusão depende das variáveis utilizadas”.

Não apresentar resultados estatísticos ou preditivos como certeza sobre eventos futuros.

---

## 11. Explicação dos resultados

A aplicação deve reduzir a dificuldade de interpretação dos dados.

Cada análise deve retornar:

* Resultado técnico;
* Explicação em linguagem simples;
* Possíveis limitações;
* Alertas relevantes.

Exemplo:

```json
{
  "metric": "F1-score",
  "value": 0.82,
  "explanation": "O F1-score combina precisão e capacidade de encontrar os casos positivos. Valores mais próximos de 1 indicam melhor equilíbrio entre essas duas medidas."
}
```

As explicações devem ser objetivas e não devem substituir a análise de um especialista quando o domínio exigir conhecimento específico.

---

## 12. Processamento e preparação dos dados

Toda transformação deve ser registrada ou retornada ao usuário.

Exemplos:

* Remoção de linhas;
* Preenchimento de valores ausentes;
* Conversão de tipos;
* Codificação de categorias;
* Normalização;
* Padronização;
* Remoção de colunas;
* Seleção de variáveis;
* Divisão entre treino e teste.

Não remover dados silenciosamente.

Quando uma decisão automática for tomada, incluir uma mensagem explicando o que aconteceu.

Exemplo:

> Foram removidas 12 linhas porque a coluna de data continha valores inválidos.

Sempre que possível, permitir que o usuário escolha como os valores ausentes serão tratados.

---

## 13. Regras para Machine Learning

Ao implementar ou modificar modelos:

* Definir `random_state` quando o algoritmo permitir;
* Evitar vazamento entre dados de treino e teste;
* Aplicar transformações dentro de pipelines;
* Ajustar transformações somente com dados de treino;
* Registrar os hiperparâmetros utilizados;
* Informar o tamanho do conjunto de treino e teste;
* Verificar desbalanceamento de classes;
* Não comparar modelos usando divisões diferentes sem deixar isso explícito;
* Não utilizar o conjunto de teste para ajuste de hiperparâmetros;
* Validar dados temporais de forma cronológica quando necessário.

Em séries temporais, não embaralhar os dados automaticamente.

---

## 14. Segurança

Considerar que todo arquivo e parâmetro recebido é potencialmente inválido.

Regras obrigatórias:

* Validar uploads;
* Limitar o tamanho dos arquivos;
* Limitar a quantidade de registros processados;
* Sanitizar nomes de arquivos;
* Não executar conteúdo enviado;
* Não aceitar caminhos informados diretamente pelo usuário;
* Não expor arquivos de outros usuários;
* Não armazenar dados indefinidamente sem necessidade;
* Não registrar dados sensíveis em logs;
* Validar parâmetros no backend;
* Evitar mensagens de erro com informações internas;
* Configurar CORS apenas para origens necessárias;
* Manter segredos fora do código-fonte.

Chaves, tokens e senhas devem ser armazenados em variáveis de ambiente.

---

## 15. Desempenho

Arquivos grandes podem bloquear o servidor ou consumir muita memória.

Ao desenvolver funcionalidades:

* Evitar cópias desnecessárias de DataFrames;
* Selecionar apenas colunas necessárias;
* Limitar a quantidade de pontos enviados para gráficos;
* Utilizar amostragem visual quando houver muitos registros;
* Manter os cálculos completos no backend quando a precisão for necessária;
* Informar quando um gráfico utiliza amostragem;
* Considerar processamento em segundo plano apenas quando a infraestrutura do projeto oferecer suporte;
* Não carregar conjuntos de dados inteiros repetidamente sem necessidade.

Nunca reduzir silenciosamente a quantidade de registros utilizada em uma análise.

---

## 16. Acessibilidade e experiência do usuário

A interface deve ser utilizável por pessoas com diferentes níveis de conhecimento.

Priorizar:

* Textos legíveis;
* Contraste adequado;
* Navegação por teclado;
* Labels em campos;
* Mensagens de erro próximas ao campo correspondente;
* Estados de carregamento;
* Descrições em gráficos;
* Indicação clara das etapas;
* Botões com nomes objetivos;
* Layout responsivo.

Evitar mensagens genéricas como:

> Algo deu errado.

Preferir:

> Não foi possível ler o arquivo. Verifique se ele possui cabeçalho e se utiliza um formato suportado.

---

## 17. JavaScript

O código JavaScript deve:

* Ser organizado por responsabilidade;
* Evitar variáveis globais;
* Validar respostas da API;
* Tratar erros de rede;
* Exibir estados de carregamento;
* Evitar duplicação de eventos;
* Remover gráficos antigos antes de recriá-los, quando necessário;
* Preservar filtros durante atualizações;
* Não confiar somente na validação do navegador.

Separar, quando possível:

```text
static/js/
├── api.js
├── upload.js
├── analysis.js
├── filters.js
├── charts.js
└── reports.js
```

---

## 18. CSS e interface

Evitar estilos repetidos ou inseridos diretamente no HTML.

Utilizar:

* Classes reutilizáveis;
* Variáveis CSS;
* Componentes visuais consistentes;
* Espaçamentos padronizados;
* Estados de sucesso, alerta e erro;
* Estilos responsivos.

Não alterar toda a identidade visual do projeto ao implementar uma funcionalidade isolada.

---

## 19. Testes

Novas funcionalidades devem incluir testes adequados.

### Testes do backend

Testar:

* Upload válido;
* Arquivo inválido;
* Arquivo vazio;
* Colunas inexistentes;
* Tipos incompatíveis;
* Valores ausentes;
* Parâmetros inválidos;
* Cada tipo de análise;
* Filtros;
* Limites de intervalo;
* Estrutura das respostas;
* Tratamento de exceções.

### Testes das análises

Utilizar conjuntos de dados pequenos e controlados para verificar:

* Cálculos estatísticos;
* Divisão dos dados;
* Métricas;
* Transformações;
* Previsões;
* Clusterização;
* Filtros;
* Reprodutibilidade.

Não validar algoritmos apenas verificando se o código executou sem erro. Conferir se o resultado está correto.

---

## 20. Logs

Os logs devem ajudar no diagnóstico sem expor os dados enviados.

Registrar:

* Início e fim das operações;
* Tipo de análise;
* Tempo de processamento;
* Quantidade de linhas e colunas;
* Avisos;
* Erros internos.

Não registrar:

* Conteúdo completo do arquivo;
* Senhas;
* Tokens;
* Dados pessoais;
* Caminhos sensíveis;
* Informações desnecessárias sobre o ambiente.

---

## 21. Estilo de código Python

Seguir as seguintes práticas:

* PEP 8;
* Type hints;
* Funções pequenas;
* Nomes claros;
* Docstrings em funções públicas;
* Tratamento específico de exceções;
* Evitar `except Exception` sem tratamento ou registro;
* Evitar valores fixos espalhados pelo código;
* Centralizar configurações;
* Separar lógica de negócio das rotas;
* Evitar código duplicado.

Exemplo:

```python
from pandas import DataFrame


def calculate_numeric_summary(dataframe: DataFrame) -> dict[str, dict]:
    """Calculate descriptive statistics for numeric columns."""
    numeric_data = dataframe.select_dtypes(include="number")

    if numeric_data.empty:
        return {}

    return numeric_data.describe().to_dict()
```

---

## 22. Regras para alterações feitas por agentes

Ao modificar o projeto, o agente deve:

1. Ler a estrutura existente antes de criar arquivos.
2. Verificar as convenções já adotadas.
3. Fazer alterações pequenas e relacionadas ao pedido.
4. Não reescrever módulos inteiros sem necessidade.
5. Não remover funcionalidades existentes sem autorização.
6. Não alterar contratos da API silenciosamente.
7. Atualizar testes quando o comportamento mudar.
8. Atualizar documentação quando necessário.
9. Explicar decisões que afetem a arquitetura.
10. Informar limitações ou partes não implementadas.

Antes de criar uma nova funcionalidade, procurar implementações semelhantes no projeto.

---

## 23. Situações que exigem confirmação

O agente deve solicitar mais informações antes de tomar decisões que alterem significativamente o projeto, especialmente sobre:

* Formatos de arquivo suportados;
* Limite máximo de upload;
* Biblioteca de gráficos;
* Persistência dos arquivos;
* Banco de dados;
* Autenticação;
* Múltiplos usuários;
* Exportação dos relatórios;
* Modelos específicos de Machine Learning;
* Hiperparâmetros disponíveis ao usuário;
* Execução síncrona ou assíncrona;
* Implantação;
* Armazenamento de resultados;
* Tratamento padrão de valores ausentes;
* Identidade visual.

Quando a informação ausente não impedir uma implementação segura, utilizar a solução mais simples e registrar a suposição feita.

---

## 24. Critérios de conclusão

Uma funcionalidade só deve ser considerada concluída quando:

* A entrada é validada;
* O processamento está separado da rota;
* Os erros são tratados;
* A resposta segue o padrão do projeto;
* A interface apresenta carregamento;
* O resultado é explicado;
* Os gráficos possuem identificação adequada;
* Os filtros são validados;
* A funcionalidade possui testes;
* Não há exposição de dados internos;
* A documentação necessária foi atualizada;
* O comportamento foi verificado com dados válidos e inválidos.

---

## 25. Prioridades do projeto

Em caso de dúvida, seguir esta ordem de prioridade:

1. Correção dos resultados;
2. Segurança dos dados;
3. Clareza das explicações;
4. Facilidade de uso;
5. Estabilidade da API;
6. Qualidade dos gráficos;
7. Desempenho;
8. Expansão da quantidade de modelos.

É preferível oferecer poucos modelos bem explicados e corretamente avaliados do que muitos modelos sem validação ou interpretação adequada.
