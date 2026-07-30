# Explica Dados

Aplicação FastAPI para transformar arquivos CSV em análises visuais, explicadas e responsáveis.

## Escopo desta versão

- Upload validado de CSV (até 10 MB, 100 mil linhas e 200 colunas).
- Prévia, tipos inferidos e diagnóstico inicial de valores ausentes.
- Classificação opcional de dados sem rótulo por faixas numéricas, categorias ou texto.
- Estatística descritiva, distribuição, correlação e sinalização preliminar de discrepantes.
- Série temporal com agregação, média móvel, tendência e previsão linear opcional.
- Classificação ou regressão com pipelines que evitam vazamento entre treino e teste.
- Segmentação K-Means com padronização, Silhouette Score e visualização PCA.
- Relatório visual imprimível com explicações, transformações e limitações.

Os arquivos não são gravados no disco: os DataFrames ficam em memória enquanto o processo está ativo. A memória mantém no máximo 20 conjuntos; dados antigos são descartados automaticamente. Esta versão suporta apenas CSV e usa Plotly pelo CDN para gráficos interativos.

### Dados sem classificação

Arquivos tabulares não precisam possuir uma variável alvo para serem enviados ou analisados. Quando o usuário precisar criar rótulos, a interface permite definir uma nova coluna e regras transparentes:

- faixa mínima e/ou máxima de uma coluna numérica;
- correspondência com categorias selecionadas;
- presença de texto, com comparação sem diferenciar maiúsculas por padrão;
- rótulo padrão opcional para linhas não correspondidas.

As regras são aplicadas na ordem e não sobrescrevem uma classificação anterior. O resultado é um novo dataset em memória; o upload original continua disponível e inalterado. Esta etapa não classifica automaticamente nem atribui significado aos registros sem regras explícitas do usuário.

## Executar

Requer Python 3.11 ou superior.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse `http://127.0.0.1:8000`.

## Testes

```powershell
pytest -q
```

## Segurança e limites

- Extensão e conteúdo do upload são validados.
- Conteúdo binário e arquivos vazios são rejeitados.
- O nome original é reduzido ao nome base e nunca é usado para criar caminhos.
- Respostas de erro não expõem stack traces nem caminhos locais.
- A API revalida colunas, intervalos, tipos e parâmetros.
- Gráficos com séries grandes usam amostra ou redução declarada; métricas continuam usando o conjunto filtrado completo.


