(function () {
  "use strict";

  var state = { dataset: null, datasetId: null };
  var metricDefinitions = {
    count: [["count", "Contagem"]],
    missing: [["missing", "Ausentes"]],
    unique: [["unique", "Únicos"]],
    mean: [["mean", "Média"]],
    median: [["median", "Mediana"]],
    mode: [["mode", "Moda"]],
    std: [["std", "Desvio padrão"]],
    variance: [["variance", "Variância"]],
    min_max: [["minimum", "Mínimo"], ["maximum", "Máximo"]],
    quartiles: [["q1", "Q1"], ["q3", "Q3"]],
    outliers: [["outliers_iqr", "Discrepantes"]],
  };

  function $(selector) { return document.querySelector(selector); }
  function $all(selector) { return Array.from(document.querySelectorAll(selector)); }
  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (character) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[character];
    });
  }
  function number(value, digits) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
    return new Intl.NumberFormat("pt-BR", { maximumFractionDigits: digits == null ? 2 : digits }).format(Number(value));
  }
  function showAlert(type, message) {
    $("#descriptive-alerts").innerHTML =
      '<div class="alert alert-' + type + '"><span>' +
      (type === "error" ? "!" : type === "warning" ? "△" : "✓") +
      "</span><span>" + escapeHtml(message) + "</span></div>";
  }
  function clearAlert() { $("#descriptive-alerts").innerHTML = ""; }
  async function api(path, options) {
    var response = await fetch(path, options || {});
    var body;
    try { body = await response.json(); } catch (_error) {
      throw new Error("O servidor retornou uma resposta inválida.");
    }
    if (!response.ok || !body.success) {
      throw new Error((body.error && body.error.details) || body.message || "Não foi possível concluir a operação.");
    }
    return body;
  }

  function typeLabel(kind) {
    return {
      numeric: "Numérico",
      categorical: "Categórico",
      date_candidate: "Possível data",
    }[kind] || kind;
  }

  function renderDataset() {
    var data = state.dataset;
    var numeric = data.columns.filter(function (column) { return column.kind === "numeric"; });
    var categorical = data.columns.filter(function (column) { return column.kind === "categorical"; });
    var dates = data.columns.filter(function (column) { return column.kind === "date_candidate"; });
    var missing = data.columns.reduce(function (total, column) { return total + column.missing; }, 0);
    $("#descriptive-dataset-name").textContent = data.filename;
    $("#descriptive-dataset-meta").textContent = number(data.rows, 0) + " linhas · " + data.columns_count + " colunas";
    $("#descriptive-status").className = "processing-status ready";
    $("#descriptive-status").innerHTML = "<i></i> Dataset carregado";

    $("#type-summary").innerHTML = [
      ["Linhas", number(data.rows, 0)],
      ["Colunas", number(data.columns_count, 0)],
      ["Numéricas", number(numeric.length, 0)],
      ["Categóricas", number(categorical.length, 0)],
      ["Possíveis datas", number(dates.length, 0)],
      ["Células ausentes", number(missing, 0)],
    ].map(function (item) {
      return '<div class="type-summary-item"><small>' + item[0] + "</small><strong>" + item[1] + "</strong></div>";
    }).join("");

    $("#data-types-body").innerHTML = data.columns.map(function (column) {
      var detail = "—";
      if (column.kind === "numeric") {
        detail = number(column.minimum) + " a " + number(column.maximum);
      } else if (column.sample_values && column.sample_values.length) {
        detail = column.sample_values.slice(0, 4).map(escapeHtml).join(", ");
      }
      return "<tr><td><strong>" + escapeHtml(column.name) + '</strong></td><td><span class="data-kind ' +
        escapeHtml(column.kind) + '">' + escapeHtml(typeLabel(column.kind)) + "</span></td><td>" +
        escapeHtml(column.dtype) + "</td><td>" + number(column.unique, 0) + "</td><td>" +
        number(column.missing, 0) + "</td><td>" + detail + "</td></tr>";
    }).join("");

    $("#column-options").innerHTML = data.columns.map(function (column, index) {
      var checked = column.kind === "numeric" ? " checked" : "";
      return '<label><input type="checkbox" name="column" value="' + escapeHtml(column.name) + '"' + checked +
        '><span><strong>' + escapeHtml(column.name) + "</strong><small>" +
        escapeHtml(typeLabel(column.kind)) + " · " + number(column.missing, 0) + " ausentes</small></span></label>";
    }).join("");
  }

  function selectedValues(name) {
    return $all('input[name="' + name + '"]:checked').map(function (input) { return input.value; });
  }
  function setColumnSelection(predicate) {
    $all('input[name="column"]').forEach(function (input) {
      var metadata = state.dataset.columns.find(function (column) { return column.name === input.value; });
      input.checked = predicate(metadata);
    });
  }

  function requestPayload() {
    return {
      dataset_id: state.datasetId,
      columns: selectedValues("column"),
      metrics: selectedValues("metric"),
      filters: [],
      include_histograms: $("#include-histograms").checked,
      include_correlations: $("#include-correlations").checked,
      include_missing_chart: $("#include-missing").checked,
    };
  }

  function table(headers, rows) {
    return '<div class="table-wrap"><table class="report-table"><thead><tr>' +
      headers.map(function (header) { return "<th>" + escapeHtml(header) + "</th>"; }).join("") +
      "</tr></thead><tbody>" +
      rows.map(function (row) {
        return "<tr>" + row.map(function (cell) { return "<td>" + escapeHtml(cell) + "</td>"; }).join("") + "</tr>";
      }).join("") + "</tbody></table></div>";
  }

  function metricColumns(metrics) {
    var fields = [];
    metrics.forEach(function (metric) {
      (metricDefinitions[metric] || []).forEach(function (definition) { fields.push(definition); });
    });
    return fields;
  }

  function blueChartLayout(title, xTitle, yTitle) {
    return {
      title: { text: title, x: 0.02, xanchor: "left", font: { color: "#2563eb", size: 16 } },
      margin: { t: 70, r: 30, b: 70, l: 70 },
      paper_bgcolor: "#ffffff",
      plot_bgcolor: "#ffffff",
      font: { color: "#2563eb" },
      xaxis: {
        title: { text: xTitle, font: { color: "#2563eb" } },
        color: "#2563eb",
        tickfont: { color: "#2563eb" },
        gridcolor: "#dbeafe",
        zerolinecolor: "#93c5fd",
      },
      yaxis: {
        title: { text: yTitle, font: { color: "#2563eb" } },
        color: "#2563eb",
        tickfont: { color: "#2563eb" },
        gridcolor: "#dbeafe",
        zerolinecolor: "#93c5fd",
      },
      legend: { font: { color: "#2563eb" } },
      hoverlabel: { bgcolor: "#ffffff", bordercolor: "#2563eb", font: { color: "#2563eb" } },
      modebar: { bgcolor: "#ffffff", color: "#2563eb", activecolor: "#1d4ed8" },
    };
  }

  function plotHistograms(items) {
    if (!items.length) return;
    var traces = items.map(function (item, index) {
      return {
        x: item.x,
        y: item.y,
        type: "bar",
        name: item.column,
        visible: index === 0,
        marker: { color: "#2563eb", line: { color: "#1d4ed8", width: 1 } },
        hovertemplate: "Faixa: %{x}<br>Quantidade: %{y}<extra></extra>",
      };
    });
    var layout = blueChartLayout("Distribuição de " + items[0].column, "Faixa de valor", "Quantidade");
    layout.updatemenus = [{
      buttons: items.map(function (item, index) {
        return {
          label: item.column,
          method: "update",
          args: [
            { visible: items.map(function (_value, itemIndex) { return itemIndex === index; }) },
            { title: { text: "Distribuição de " + item.column, font: { color: "#2563eb" } } },
          ],
        };
      }),
      direction: "down",
      x: 0,
      y: 1.16,
      bgcolor: "#ffffff",
      bordercolor: "#2563eb",
      font: { color: "#2563eb" },
    }];
    Plotly.newPlot("descriptive-histogram", traces, layout, { responsive: true, displaylogo: false });
  }

  function plotMissing(rows) {
    var layout = blueChartLayout("Valores ausentes por coluna", "Coluna", "Percentual ausente");
    layout.yaxis.ticksuffix = "%";
    Plotly.newPlot("descriptive-missing", [{
      x: rows.map(function (row) { return row.column; }),
      y: rows.map(function (row) { return row.percentage; }),
      type: "bar",
      marker: { color: "#2563eb", line: { color: "#1d4ed8", width: 1 } },
      hovertemplate: "%{x}<br>%{y:.1f}% ausente<extra></extra>",
    }], layout, { responsive: true, displaylogo: false });
  }

  function plotCorrelation(rows) {
    var names = rows.map(function (row) { return row.column; });
    var values = rows.map(function (row) {
      return names.map(function (name) { return row[name]; });
    });
    var layout = blueChartLayout("Correlação entre variáveis numéricas", "Variável", "Variável");
    Plotly.newPlot("descriptive-correlation", [{
      z: values,
      x: names,
      y: names,
      type: "heatmap",
      colorscale: [[0, "#ffffff"], [0.5, "#93c5fd"], [1, "#2563eb"]],
      zmin: -1,
      zmax: 1,
      colorbar: { tickfont: { color: "#2563eb" }, title: { text: "Correlação", font: { color: "#2563eb" } } },
      hovertemplate: "%{x} × %{y}: %{z:.2f}<extra></extra>",
    }], layout, { responsive: true, displaylogo: false });
  }

  function renderResults(data, warnings) {
    var fields = metricColumns(data.settings.metrics);
    var numericRows = data.numeric_summary.map(function (row) {
      return [row.column].concat(fields.map(function (field) { return number(row[field[0]]); }));
    });
    var categoricalFields = fields.filter(function (field) {
      return ["count", "missing", "unique", "mode"].includes(field[0]);
    });
    var html = '<div class="result-heading"><div><p class="section-kicker">RESULTADO</p><h2>Estatística descritiva configurada</h2></div><p>' +
      number(data.overview.rows_analyzed, 0) + " linhas · " + number(data.overview.columns_analyzed, 0) +
      " colunas analisadas</p></div>";
    html += '<div class="metric-grid">' +
      '<div class="metric-card"><small>Linhas analisadas</small><strong>' + number(data.overview.rows_analyzed, 0) + "</strong></div>" +
      '<div class="metric-card"><small>Colunas numéricas</small><strong>' + number(data.overview.numeric_columns, 0) + "</strong></div>" +
      '<div class="metric-card"><small>Colunas categóricas</small><strong>' + number(data.overview.categorical_columns, 0) + "</strong></div>" +
      '<div class="metric-card"><small>Células ausentes</small><strong>' + number(data.overview.missing_cells, 0) + "</strong></div></div>";

    if (numericRows.length) {
      html += '<section class="result-section"><h3>Resumo das colunas numéricas</h3><p>A tabela contém somente as métricas selecionadas.</p>' +
        table(["Variável"].concat(fields.map(function (field) { return field[1]; })), numericRows) + "</section>";
    }
    if (data.categorical_summary.length) {
      html += '<section class="result-section"><h3>Resumo das colunas não numéricas</h3><div class="categorical-tables">' +
        data.categorical_summary.map(function (row) {
          var rows = categoricalFields.map(function (field) { return [field[1], number(row[field[0]])]; });
          if (!rows.length) rows = row.top_values.map(function (item) { return [item.value, number(item.count, 0)]; });
          return '<div class="categorical-table"><h4>' + escapeHtml(row.column) + "</h4>" +
            table(["Medida", "Valor"], rows) + "</div>";
        }).join("") + "</div></section>";
    }
    if (data.histograms.length) {
      html += '<section class="result-section"><h3>Distribuições</h3><div id="descriptive-histogram" class="descriptive-chart" aria-label="Histogramas das variáveis selecionadas"></div></section>';
    }
    if (data.settings.include_missing_chart) {
      html += '<section class="result-section"><h3>Valores ausentes</h3><div id="descriptive-missing" class="descriptive-chart" aria-label="Valores ausentes por coluna"></div></section>';
    }
    if (data.correlations.length) {
      html += '<section class="result-section"><h3>Correlação</h3><div id="descriptive-correlation" class="descriptive-chart" aria-label="Matriz de correlação"></div></section>';
    }
    html += '<section class="result-section"><h3>Como interpretar</h3><ul class="interpretation-list">' +
      data.interpretation.map(function (item) { return "<li>" + escapeHtml(item) + "</li>"; }).join("") + "</ul></section>";
    if (warnings.length) {
      html += '<section class="result-section"><h3>Alertas e limitações</h3><ul class="warning-list">' +
        warnings.map(function (item) { return "<li>" + escapeHtml(item) + "</li>"; }).join("") + "</ul></section>";
    }
    $("#empty-result").classList.add("hidden");
    $("#descriptive-result-content").classList.remove("hidden");
    $("#descriptive-result-content").innerHTML = html;
    if (data.histograms.length) plotHistograms(data.histograms);
    if (data.settings.include_missing_chart) plotMissing(data.missing);
    if (data.correlations.length) plotCorrelation(data.correlations);
  }

  async function initialize() {
    var params = new URLSearchParams(window.location.search);
    state.datasetId = params.get("dataset_id") || sessionStorage.getItem("activeDatasetId");
    if (!state.datasetId) {
      showAlert("error", "Nenhum dataset foi informado. Volte à página principal e envie um arquivo.");
      $("#descriptive-status").innerHTML = "<i></i> Dataset ausente";
      return;
    }
    var returnUrl = "/?dataset_id=" + encodeURIComponent(state.datasetId);
    $("#back-to-dataset").href = returnUrl;
    $("#header-back").href = returnUrl;
    $("#sidebar-home").href = returnUrl;
    try {
      var response = await api("/api/datasets/" + encodeURIComponent(state.datasetId));
      state.dataset = response.data;
      sessionStorage.setItem("activeDatasetId", state.datasetId);
      renderDataset();
    } catch (error) {
      showAlert("error", error.message);
      $("#descriptive-status").innerHTML = "<i></i> Dataset indisponível";
    }
  }

  $("#select-numeric").addEventListener("click", function () {
    setColumnSelection(function (column) { return column.kind === "numeric"; });
  });
  $("#select-all-columns").addEventListener("click", function () {
    setColumnSelection(function () { return true; });
  });
  $("#clear-columns").addEventListener("click", function () {
    setColumnSelection(function () { return false; });
  });
  $("#descriptive-form").addEventListener("submit", async function (event) {
    event.preventDefault();
    clearAlert();
    var payload = requestPayload();
    if (!payload.columns.length) {
      showAlert("error", "Selecione ao menos uma coluna para a análise.");
      return;
    }
    if (!payload.metrics.length) {
      showAlert("error", "Selecione ao menos uma métrica.");
      return;
    }
    var button = event.submitter;
    var original = button.textContent;
    button.disabled = true;
    button.textContent = "Processando análise...";
    $("#descriptive-status").className = "processing-status";
    $("#descriptive-status").innerHTML = "<i></i> Processando";
    try {
      var response = await api("/api/analyses/descriptive", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      renderResults(response.data, response.warnings);
      $("#descriptive-status").className = "processing-status ready";
      $("#descriptive-status").innerHTML = "<i></i> Análise concluída";
      $("#descriptive-results").scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
      showAlert("error", error.message);
      $("#descriptive-status").innerHTML = "<i></i> Falha na análise";
    } finally {
      button.disabled = false;
      button.textContent = original;
    }
  });

  initialize();
})();
