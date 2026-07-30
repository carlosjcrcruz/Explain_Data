(() => {
  "use strict";

  const state = {
    dataset: null,
    analysis: "descriptive",
    result: null,
    filters: [],
    classificationRules: [],
    originalDataset: null,
  };

  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;",
  })[char]);
  const formatNumber = (value, digits = 2) => {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
    return new Intl.NumberFormat("pt-BR", { maximumFractionDigits: digits }).format(Number(value));
  };
  const formatPercent = (value) => value === null || value === undefined ? "—" : `${formatNumber(value, 1)}%`;

  const alertRegion = $("#alert-region");
  const analysisLabels = {
    descriptive: "Estatística descritiva",
    "time-series": "Série temporal",
    supervised: "Modelo supervisionado",
    clustering: "Clusterização",
  };
  function showAlerts(type, messages) {
    const list = (Array.isArray(messages) ? messages : [messages]).filter(Boolean);
    alertRegion.innerHTML = list.map((message) =>
      `<div class="alert alert-${type}"><span>${type === "error" ? "!" : type === "warning" ? "△" : "✓"}</span><span>${escapeHtml(message)}</span></div>`
    ).join("");
  }
  function clearAlerts() { alertRegion.innerHTML = ""; }

  function setStep(step, { preserveScroll = false } = {}) {
    if (step === 2 && !state.dataset) {
      showAlerts("warning", "Envie um arquivo CSV antes de acessar a configuração.");
      return;
    }
    if (step === 3 && !state.result) {
      showAlerts("warning", "Execute uma análise antes de abrir o relatório.");
      return;
    }
    $$("[data-progress]").forEach((item) => {
      const number = Number(item.dataset.progress);
      item.classList.toggle("active", number === step);
      item.classList.toggle("done", number < step);
      item.querySelector("span").textContent = number < step ? "✓" : String(number);
    });
    ["upload-panel", "config-panel", "result-panel"].forEach((id, index) => {
      $(`#${id}`).classList.toggle("hidden", index + 1 !== step);
    });
    const headings = {
      1: ["DADOS / UPLOAD", "Enviar arquivo CSV", "Carregue um conjunto de dados para visualizar as colunas e configurar uma análise."],
      2: ["DADOS / CONFIGURAÇÃO", "Prévia e configuração", "Revise a estrutura do arquivo, selecione o procedimento e defina seus parâmetros."],
      3: ["ANÁLISES / RELATÓRIO", analysisLabels[state.analysis], "Revise métricas, gráficos, transformações aplicadas e limitações da avaliação."],
    };
    $("#breadcrumb").textContent = headings[step][0];
    $("#page-title").textContent = headings[step][1];
    $("#page-description").textContent = headings[step][2];
    $("#sample-button").classList.toggle("hidden", step !== 1);
    $$(".nav-item").forEach((item) => item.classList.remove("active"));
    const activeNav = $(`[data-nav-step="${step}"]`);
    activeNav?.classList.add("active");
    $("#sidebar").classList.remove("open");
    $("#menu-toggle").setAttribute("aria-expanded", "false");
    if (!preserveScroll) {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }

  async function api(path, options = {}) {
    const response = await fetch(path, options);
    let body;
    try { body = await response.json(); } catch { throw new Error("O servidor retornou uma resposta inválida."); }
    if (!response.ok || !body.success) {
      throw new Error(body?.error?.details || body?.message || "Não foi possível concluir a solicitação.");
    }
    return body;
  }

  const dropzone = $("#dropzone");
  const fileInput = $("#file-input");
  ["dragenter", "dragover"].forEach((event) => dropzone.addEventListener(event, (e) => {
    e.preventDefault(); dropzone.classList.add("dragging");
  }));
  ["dragleave", "drop"].forEach((event) => dropzone.addEventListener(event, (e) => {
    e.preventDefault(); dropzone.classList.remove("dragging");
  }));
  dropzone.addEventListener("drop", (event) => {
    const [file] = event.dataTransfer.files;
    if (file) uploadFile(file);
  });
  fileInput.addEventListener("change", () => fileInput.files[0] && uploadFile(fileInput.files[0]));
  $("#browse-button").addEventListener("click", () => fileInput.click());

  async function uploadFile(file) {
    clearAlerts();
    if (!file.name.toLowerCase().endsWith(".csv")) {
      showAlerts("error", "Selecione um arquivo CSV válido.");
      return;
    }
    dropzone.classList.add("hidden");
    $("#upload-loading").classList.remove("hidden");
    $("#processing-status").className = "processing-status";
    $("#processing-status").innerHTML = "<i></i> Validando arquivo";
    const form = new FormData();
    form.append("file", file);
    try {
      const response = await api("/api/datasets/upload", { method: "POST", body: form });
      state.dataset = response.data;
      state.originalDataset = response.data;
      state.classificationRules = [];
      renderDataset();
      renderFields();
      if (response.warnings.length) showAlerts("warning", response.warnings);
      setStep(2);
    } catch (error) {
      showAlerts("error", error.message);
      dropzone.classList.remove("hidden");
      $("#processing-status").innerHTML = "<i></i> Falha na validação";
    } finally {
      $("#upload-loading").classList.add("hidden");
    }
  }

  function renderDataset() {
    const data = state.dataset;
    $("#dataset-name").textContent = data.filename;
    const originText = data.parent_dataset_id ? " · dataset derivado" : "";
    const separatorText = data.separator ? ` · separador “${data.separator}”` : "";
    $("#dataset-meta").textContent = `${formatNumber(data.rows, 0)} linhas · ${data.columns_count} colunas${separatorText}${originText}`;
    const missing = data.columns.reduce((total, column) => total + column.missing, 0);
    $("#quality-chip").textContent = missing ? `${formatNumber(missing, 0)} células ausentes` : "Sem valores ausentes";
    $("#header-dataset-name").textContent = data.filename;
    $("#header-dataset-meta").textContent = `${formatNumber(data.rows, 0)} linhas · ${data.columns_count} colunas`;
    $("#header-change-file").classList.remove("hidden");
    $("#processing-status").className = "processing-status ready";
    $("#processing-status").innerHTML = "<i></i> Arquivo validado";
    $("#summary-rows").textContent = formatNumber(data.rows, 0);
    $("#summary-columns").textContent = formatNumber(data.columns_count, 0);
    $("#summary-numeric").textContent = formatNumber(data.columns.filter((column) => column.kind === "numeric").length, 0);
    $("#summary-categorical").textContent = formatNumber(data.columns.filter((column) => column.kind === "categorical").length, 0);
    $("#summary-dates").textContent = formatNumber(data.columns.filter((column) => column.kind === "date_candidate").length, 0);
    const headers = data.columns.map((column) => `<th scope="col">${escapeHtml(column.name)}<br><small>${escapeHtml(column.kind)}</small></th>`).join("");
    const rows = data.preview.map((row) => `<tr>${data.columns.map((column) => {
      const missingValue = row[column.name] === null || row[column.name] === undefined;
      return `<td${missingValue ? ' class="missing-value"' : ""}>${escapeHtml(missingValue ? "Ausente" : row[column.name])}</td>`;
    }).join("")}</tr>`).join("");
    $("#preview-table").innerHTML = `<thead><tr>${headers}</tr></thead><tbody>${rows}</tbody>`;
    if (data.classification) {
      $("#classification-status").innerHTML = `
        <span>${formatNumber(data.classification.classified_rows, 0)} registros classificados em “${escapeHtml(data.classification.column)}”; ${formatNumber(data.classification.unclassified_rows, 0)} sem rótulo.</span>
        <button class="button button-secondary button-compact" id="restore-original" type="button">Usar dataset original</button>`;
      $("#classification-status").className = "classification-result";
      $("#restore-original").addEventListener("click", () => {
        state.dataset = state.originalDataset;
        state.result = null;
        state.classificationRules = [];
        renderDataset();
        renderFields();
        renderClassificationRules();
        $("#classification-status").textContent = "Dataset original restaurado para as próximas análises.";
        $("#classification-status").className = "";
      });
    } else {
      $("#classification-status").textContent = "Nenhuma alteração foi aplicada ao dataset.";
      $("#classification-status").className = "";
    }
  }

  function options(columns, selected = "") {
    return columns.map((column) => `<option value="${escapeHtml(column.name)}"${column.name === selected ? " selected" : ""}>${escapeHtml(column.name)} · ${escapeHtml(column.kind)}</option>`).join("");
  }
  function inputField(label, id, body, help = "", full = false) {
    return `<div class="field${full ? " full" : ""}"><label for="${id}">${label}</label>${body}${help ? `<small>${help}</small>` : ""}</div>`;
  }

  function renderFields() {
    if (!state.dataset) return;
    const columns = state.dataset.columns;
    const numeric = columns.filter((column) => column.kind === "numeric");
    const dates = columns.filter((column) => column.kind === "date_candidate");
    let html = "";
    if (state.analysis === "descriptive") {
      html = `<div class="fields-grid">${inputField("Colunas analisadas", "columns", `<select id="columns" multiple>${options(columns)}</select>`, "Opcional. Sem seleção, todas as colunas serão analisadas.", true)}</div>`;
    } else if (state.analysis === "time-series") {
      html = `<div class="fields-grid">
        ${inputField("Coluna de data", "date-column", `<select id="date-column" required><option value="">Selecione</option>${options(columns, dates[0]?.name)}</select>`, "A conversão dos valores será validada.")}
        ${inputField("Variável numérica", "value-column", `<select id="value-column" required><option value="">Selecione</option>${options(numeric, numeric[0]?.name)}</select>`)}
        ${inputField("Frequência", "frequency", `<select id="frequency"><option value="auto">Detectar automaticamente</option><option value="D">Diária</option><option value="W">Semanal</option><option value="ME">Mensal</option><option value="QE">Trimestral</option><option value="YE">Anual</option></select>`)}
        ${inputField("Agregação", "aggregation", `<select id="aggregation"><option value="mean">Média</option><option value="sum">Soma</option><option value="median">Mediana</option></select>`)}
        ${inputField("Janela da média móvel", "rolling-window", `<input id="rolling-window" type="number" min="2" max="365" value="7" required>`)}
        ${inputField("Horizonte de previsão", "forecast-horizon", `<input id="forecast-horizon" type="number" min="0" max="90" value="0" required>`, "0 desativa a previsão linear.")}
      </div>`;
    } else if (state.analysis === "supervised") {
      html = `<div class="fields-grid">
        ${inputField("Tipo de problema", "problem-type", `<select id="problem-type"><option value="classification">Classificação</option><option value="regression">Regressão</option></select>`)}
        ${inputField("Modelo", "model", `<select id="model"></select>`, "A avaliação usa uma divisão reprodutível entre treino e teste.")}
        ${inputField("Variável alvo", "target-column", `<select id="target-column" required><option value="">Selecione</option>${options(columns, state.dataset.classification?.column)}</select>`)}
        ${inputField("Percentual para teste", "test-size", `<select id="test-size"><option value=".2">20%</option><option value=".25">25%</option><option value=".3">30%</option></select>`)}
        ${inputField("Variáveis preditoras", "feature-columns", `<select id="feature-columns" multiple required>${options(columns)}</select>`, "Use Ctrl/Cmd para selecionar mais de uma variável.", true)}
      </div>`;
    } else {
      html = `<div class="fields-grid">
        ${inputField("Variáveis numéricas", "cluster-columns", `<select id="cluster-columns" multiple required>${options(numeric)}</select>`, "Selecione ao menos duas. Os valores serão padronizados.", true)}
        ${inputField("Quantidade de grupos", "n-clusters", `<input id="n-clusters" type="number" min="2" max="10" value="3" required>`)}
      </div>`;
    }
    $("#analysis-fields").innerHTML = `${html}
      <div class="filter-section">
        <div class="filter-heading">
          <div><strong>Filtros opcionais</strong><small>Os dados originais são preservados.</small></div>
          <button class="button button-secondary button-compact" id="add-filter" type="button">+ Adicionar filtro</button>
        </div>
        <div id="filter-list"></div>
      </div>`;
    if (state.analysis === "supervised") {
      $("#problem-type").addEventListener("change", renderModelOptions);
      renderModelOptions();
    }
    $("#add-filter").addEventListener("click", () => {
      if (state.filters.length >= 5) {
        showAlerts("warning", "Use no máximo 5 filtros por análise.");
        return;
      }
      state.filters.push({ column: "", kind: "", minimum: "", maximum: "", values: [], start: "", end: "" });
      renderFilters();
    });
    renderFilters();
  }

  function renderModelOptions() {
    const classification = $("#problem-type").value === "classification";
    $("#model").innerHTML = classification
      ? `<option value="logistic">Regressão logística</option><option value="decision_tree">Árvore de decisão</option><option value="random_forest">Random Forest</option>`
      : `<option value="linear">Regressão linear</option><option value="decision_tree">Árvore de regressão</option><option value="random_forest">Random Forest Regressor</option>`;
  }

  function renderFilters() {
    const list = $("#filter-list");
    if (!list) return;
    if (!state.filters.length) {
      list.innerHTML = `<p class="empty-filters">Nenhum filtro aplicado. A análise usará todas as linhas.</p>`;
      return;
    }
    list.innerHTML = state.filters.map((filter, index) => {
      const metadata = state.dataset.columns.find((column) => column.name === filter.column);
      const kind = metadata?.kind === "numeric" ? "range" : metadata?.kind === "date_candidate" ? "date" : "categories";
      let controls = `<div class="filter-control muted-control">Escolha uma coluna para configurar o intervalo.</div>`;
      if (metadata && kind === "range") {
        controls = `<div class="filter-control"><input aria-label="Mínimo de ${escapeHtml(filter.column)}" data-filter-input="${index}" data-key="minimum" type="number" step="any" placeholder="Mínimo" value="${escapeHtml(filter.minimum)}"><span>até</span><input aria-label="Máximo de ${escapeHtml(filter.column)}" data-filter-input="${index}" data-key="maximum" type="number" step="any" placeholder="Máximo" value="${escapeHtml(filter.maximum)}"></div>`;
      } else if (metadata && kind === "date") {
        controls = `<div class="filter-control"><input aria-label="Data inicial de ${escapeHtml(filter.column)}" data-filter-input="${index}" data-key="start" type="date" value="${escapeHtml(filter.start)}"><span>até</span><input aria-label="Data final de ${escapeHtml(filter.column)}" data-filter-input="${index}" data-key="end" type="date" value="${escapeHtml(filter.end)}"></div>`;
      } else if (metadata) {
        const values = metadata.sample_values || [];
        controls = values.length
          ? `<select aria-label="Categorias de ${escapeHtml(filter.column)}" data-filter-categories="${index}" multiple>${values.map((value) => `<option value="${escapeHtml(value)}"${filter.values.includes(value) ? " selected" : ""}>${escapeHtml(value)}</option>`).join("")}</select>`
          : `<div class="filter-control muted-control">Esta coluna tem categorias demais para o filtro visual.</div>`;
      }
      return `<div class="filter-row">
        <select aria-label="Coluna do filtro ${index + 1}" data-filter-column="${index}"><option value="">Selecione uma coluna</option>${options(state.dataset.columns, filter.column)}</select>
        ${controls}
        <button class="icon-button" type="button" data-remove-filter="${index}" aria-label="Remover filtro ${index + 1}">×</button>
      </div>`;
    }).join("");

    $$("[data-filter-column]").forEach((element) => element.addEventListener("change", () => {
      const index = Number(element.dataset.filterColumn);
      const metadata = state.dataset.columns.find((column) => column.name === element.value);
      state.filters[index] = {
        column: element.value,
        kind: metadata?.kind === "numeric" ? "range" : metadata?.kind === "date_candidate" ? "date" : "categories",
        minimum: "", maximum: "", values: [], start: "", end: "",
      };
      renderFilters();
    }));
    $$("[data-filter-input]").forEach((element) => element.addEventListener("input", () => {
      state.filters[Number(element.dataset.filterInput)][element.dataset.key] = element.value;
    }));
    $$("[data-filter-categories]").forEach((element) => element.addEventListener("change", () => {
      state.filters[Number(element.dataset.filterCategories)].values = [...element.selectedOptions].map((option) => option.value);
    }));
    $$("[data-remove-filter]").forEach((element) => element.addEventListener("click", () => {
      state.filters.splice(Number(element.dataset.removeFilter), 1);
      renderFilters();
    }));
  }

  function defaultClassificationRule() {
    const column = state.dataset?.columns[0];
    return {
      source_column: column?.name || "",
      kind: column?.kind === "numeric" ? "range" : "categories",
      label: "",
      minimum: "",
      maximum: "",
      values: [],
      text: "",
      case_sensitive: false,
    };
  }

  function renderClassificationRules() {
    const container = $("#classification-rules");
    if (!container || !state.dataset) return;
    if (!state.classificationRules.length) {
      container.innerHTML = `<p class="empty-filters">Adicione ao menos uma regra para gerar a nova coluna.</p>`;
      return;
    }
    container.innerHTML = state.classificationRules.map((rule, index) => {
      const metadata = state.dataset.columns.find((column) => column.name === rule.source_column);
      const categoryValues = metadata?.sample_values || [];
      let criterion;
      if (rule.kind === "range") {
        criterion = `<div class="rule-criterion-range">
          <input aria-label="Valor mínimo da regra ${index + 1}" data-classification-input="${index}" data-key="minimum" type="number" step="any" placeholder="Mínimo" value="${escapeHtml(rule.minimum)}">
          <input aria-label="Valor máximo da regra ${index + 1}" data-classification-input="${index}" data-key="maximum" type="number" step="any" placeholder="Máximo" value="${escapeHtml(rule.maximum)}">
        </div>`;
      } else if (rule.kind === "categories" && categoryValues.length) {
        criterion = `<select aria-label="Categorias da regra ${index + 1}" data-classification-values="${index}" multiple>${categoryValues.map((value) => `<option value="${escapeHtml(value)}"${rule.values.includes(value) ? " selected" : ""}>${escapeHtml(value)}</option>`).join("")}</select>`;
      } else if (rule.kind === "categories") {
        criterion = `<input aria-label="Categorias da regra ${index + 1}" data-classification-input="${index}" data-key="valuesText" type="text" placeholder="Separe categorias por vírgula" value="${escapeHtml(rule.values.join(", "))}">`;
      } else {
        criterion = `<input aria-label="Texto da regra ${index + 1}" data-classification-input="${index}" data-key="text" type="text" placeholder="Texto contido na coluna" value="${escapeHtml(rule.text)}">`;
      }
      return `<div class="classification-rule">
        <div class="field">
          <label for="classification-source-${index}">Coluna de origem</label>
          <select id="classification-source-${index}" data-classification-source="${index}">${options(state.dataset.columns, rule.source_column)}</select>
        </div>
        <div class="field">
          <label for="classification-kind-${index}">Critério</label>
          <select id="classification-kind-${index}" data-classification-kind="${index}">
            <option value="range"${rule.kind === "range" ? " selected" : ""}>Faixa numérica</option>
            <option value="categories"${rule.kind === "categories" ? " selected" : ""}>Categorias</option>
            <option value="contains"${rule.kind === "contains" ? " selected" : ""}>Texto contém</option>
          </select>
        </div>
        <div class="field">
          <label>Valores correspondentes</label>
          ${criterion}
        </div>
        <div class="field">
          <label for="classification-label-${index}">Rótulo atribuído</label>
          <input id="classification-label-${index}" data-classification-input="${index}" data-key="label" type="text" maxlength="100" placeholder="Ex.: alta prioridade" value="${escapeHtml(rule.label)}" required>
        </div>
        <button class="icon-button" type="button" data-remove-classification-rule="${index}" aria-label="Remover regra ${index + 1}">×</button>
      </div>`;
    }).join("");

    $$("[data-classification-source]").forEach((element) => element.addEventListener("change", () => {
      const index = Number(element.dataset.classificationSource);
      const metadata = state.dataset.columns.find((column) => column.name === element.value);
      state.classificationRules[index] = {
        ...defaultClassificationRule(),
        source_column: element.value,
        kind: metadata?.kind === "numeric" ? "range" : "categories",
        label: state.classificationRules[index].label,
      };
      renderClassificationRules();
    }));
    $$("[data-classification-kind]").forEach((element) => element.addEventListener("change", () => {
      const rule = state.classificationRules[Number(element.dataset.classificationKind)];
      rule.kind = element.value;
      rule.minimum = "";
      rule.maximum = "";
      rule.values = [];
      rule.text = "";
      renderClassificationRules();
    }));
    $$("[data-classification-input]").forEach((element) => element.addEventListener("input", () => {
      const rule = state.classificationRules[Number(element.dataset.classificationInput)];
      if (element.dataset.key === "valuesText") {
        rule.values = element.value.split(",").map((value) => value.trim()).filter(Boolean);
      } else {
        rule[element.dataset.key] = element.value;
      }
    }));
    $$("[data-classification-values]").forEach((element) => element.addEventListener("change", () => {
      state.classificationRules[Number(element.dataset.classificationValues)].values =
        [...element.selectedOptions].map((option) => option.value);
    }));
    $$("[data-remove-classification-rule]").forEach((element) => element.addEventListener("click", () => {
      state.classificationRules.splice(Number(element.dataset.removeClassificationRule), 1);
      renderClassificationRules();
    }));
  }

  function classificationPayload() {
    return {
      dataset_id: state.dataset.dataset_id,
      classification_column: $("#classification-column").value.trim(),
      default_label: $("#classification-default").value.trim() || null,
      rules: state.classificationRules.map((rule) => ({
        source_column: rule.source_column,
        kind: rule.kind,
        label: rule.label.trim(),
        minimum: rule.minimum === "" ? null : Number(rule.minimum),
        maximum: rule.maximum === "" ? null : Number(rule.maximum),
        values: rule.values,
        text: rule.text || null,
        case_sensitive: rule.case_sensitive,
      })),
    };
  }

  function activateAnalysis(analysis) {
    if (state.analysis !== analysis) state.result = null;
    state.analysis = analysis;
    $$(".analysis-card").forEach((item) => {
      const selected = item.dataset.analysis === analysis;
      item.classList.toggle("selected", selected);
      item.setAttribute("aria-checked", String(selected));
    });
    renderFields();
    if (state.dataset) {
      setStep(2, { preserveScroll: true });
      $$(".nav-item").forEach((item) => item.classList.remove("active"));
      $(`[data-nav-analysis="${analysis}"]`)?.classList.add("active");
    }
  }

  $$(".analysis-card").forEach((card) => card.addEventListener("click", () => {
    activateAnalysis(card.dataset.analysis);
  }));

  const selectedValues = (selector) => [...$(selector).selectedOptions].map((option) => option.value);
  function activeFilters() {
    return state.filters.filter((filter) => {
      if (!filter.column) return false;
      if (filter.kind === "range") return filter.minimum !== "" || filter.maximum !== "";
      if (filter.kind === "date") return filter.start || filter.end;
      return filter.values.length;
    }).map((filter) => {
      if (filter.kind === "range") return {
        column: filter.column, kind: filter.kind,
        minimum: filter.minimum === "" ? null : Number(filter.minimum),
        maximum: filter.maximum === "" ? null : Number(filter.maximum),
      };
      if (filter.kind === "date") return {
        column: filter.column, kind: filter.kind, start: filter.start || null, end: filter.end || null,
      };
      return { column: filter.column, kind: filter.kind, values: filter.values };
    });
  }
  function requestPayload() {
    const base = { dataset_id: state.dataset.dataset_id, filters: activeFilters() };
    if (state.analysis === "descriptive") return { ...base, columns: selectedValues("#columns") };
    if (state.analysis === "time-series") return {
      ...base, date_column: $("#date-column").value, value_column: $("#value-column").value,
      frequency: $("#frequency").value, aggregation: $("#aggregation").value,
      rolling_window: Number($("#rolling-window").value), forecast_horizon: Number($("#forecast-horizon").value),
    };
    if (state.analysis === "supervised") return {
      ...base, problem_type: $("#problem-type").value, model: $("#model").value,
      target_column: $("#target-column").value, feature_columns: selectedValues("#feature-columns"),
      test_size: Number($("#test-size").value),
    };
    return { ...base, feature_columns: selectedValues("#cluster-columns"), n_clusters: Number($("#n-clusters").value) };
  }

  $("#analysis-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearAlerts();
    const button = event.submitter;
    const original = button.innerHTML;
    button.disabled = true;
    button.innerHTML = `<span class="spinner" style="width:18px;height:18px;border-width:2px"></span> Processando`;
    $("#processing-status").className = "processing-status";
    $("#processing-status").innerHTML = `<i></i> Processando ${formatNumber(state.dataset.rows, 0)} registros`;
    try {
      const endpoints = { descriptive: "descriptive", "time-series": "time-series", supervised: "supervised", clustering: "clustering" };
      const response = await api(`/api/analyses/${endpoints[state.analysis]}`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(requestPayload()),
      });
      state.result = response;
      setStep(3);
      renderResult(response.data, response.warnings);
      $("#processing-status").className = "processing-status ready";
      $("#processing-status").innerHTML = "<i></i> Análise concluída";
    } catch (error) {
      showAlerts("error", error.message);
      $("#processing-status").className = "processing-status";
      $("#processing-status").innerHTML = "<i></i> Falha na análise";
    } finally {
      button.disabled = false;
      button.innerHTML = original;
    }
  });

  const metricCard = (label, value) => `<div class="metric-card"><small>${escapeHtml(label)}</small><strong>${escapeHtml(value)}</strong></div>`;
  const reportCard = (title, content) => `<section class="report-card"><h4>${escapeHtml(title)}</h4>${content}</section>`;
  const interpretationSection = (items) => reportCard("Como interpretar", `<ul class="interpretation-list">${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`);
  const warningCards = (items) => items.length ? reportCard("Alertas e limitações", `<ul class="warning-list">${items.map((item) => `<li>△ ${escapeHtml(item)}</li>`).join("")}</ul>`) : "";
  const tableHtml = (headers, rows) => `<div class="table-wrap"><table class="report-table"><thead><tr>${headers.map((h) => `<th>${escapeHtml(h)}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;

  function renderResult(data, warnings) {
    if (state.analysis === "descriptive") renderDescriptive(data, warnings);
    else if (state.analysis === "time-series") renderTimeSeries(data, warnings);
    else if (state.analysis === "supervised") renderSupervised(data, warnings);
    else renderClustering(data, warnings);
    $("#report-filename").textContent = state.dataset.filename;
    $("#report-analysis").textContent = analysisLabels[state.analysis];
    $("#report-generated-at").textContent = new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short", timeStyle: "short",
    }).format(new Date());
    const summary = activeFilterSummary();
    if (summary) {
      $("#result-content").insertAdjacentHTML(
        "afterbegin",
        `<div class="active-filter-summary"><strong>Filtros ativos:</strong> ${escapeHtml(summary)}</div>`,
      );
    }
  }

  function activeFilterSummary() {
    return activeFilters().map((filter) => {
      if (filter.kind === "range") {
        return `${filter.column} = ${filter.minimum ?? "sem mínimo"} a ${filter.maximum ?? "sem máximo"}`;
      }
      if (filter.kind === "date") {
        return `${filter.column} = ${filter.start ?? "início"} a ${filter.end ?? "fim"}`;
      }
      return `${filter.column} = ${filter.values.join(", ")}`;
    }).join(" · ");
  }

  function renderDescriptive(data, warnings) {
    const o = data.overview;
    let html = `<div class="metric-grid">
      ${metricCard("Linhas analisadas", formatNumber(o.rows_analyzed, 0))}
      ${metricCard("Variáveis", formatNumber(o.columns_analyzed, 0))}
      ${metricCard("Variáveis numéricas", formatNumber(o.numeric_columns, 0))}
      ${metricCard("Células ausentes", formatNumber(o.missing_cells, 0))}
    </div>`;
    if (data.numeric_summary.length) {
      html += reportCard("Resumo das variáveis numéricas", tableHtml(
        ["Variável", "Média", "Mediana", "Desvio padrão", "Mínimo", "Máximo", "Discrepantes"],
        data.numeric_summary.map((row) => [row.column, formatNumber(row.mean), formatNumber(row.median), formatNumber(row.std), formatNumber(row.minimum), formatNumber(row.maximum), formatNumber(row.outliers_iqr, 0)])
      ));
      html += reportCard("Distribuições", `<div id="distribution-chart" class="chart" aria-label="Histogramas das variáveis numéricas"></div>`);
    }
    html += reportCard("Qualidade dos dados", `<div id="missing-chart" class="chart" aria-label="Percentual de valores ausentes por coluna"></div>`);
    if (data.correlations.length) html += reportCard("Correlação entre variáveis", `<div id="correlation-chart" class="chart" aria-label="Mapa de correlação"></div>`);
    html += interpretationSection(data.interpretation) + warningCards(warnings);
    $("#result-content").innerHTML = html;
    plotMissing(data.missing);
    plotDistributions(data.histograms);
    if (data.correlations.length) plotCorrelation(data.correlations);
  }

  function plotMissing(rows) {
    Plotly.newPlot("missing-chart", [{ x: rows.map((r) => r.column), y: rows.map((r) => r.percentage), type: "bar", marker: { color: "#2563eb" }, hovertemplate: "%{x}: %{y:.1f}%<extra></extra>" }], {
      title: { text: "Valores ausentes por coluna", x: .01, xanchor: "left", font: { size: 15 } }, margin: { t: 55, r: 20, b: 80, l: 55 }, yaxis: { title: "% ausente", rangemode: "tozero", gridcolor: "#e5e7eb" }, xaxis: { gridcolor: "#e5e7eb" }, font: { color: "#4b5563" }, paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff",
    }, { responsive: true, displaylogo: false });
  }
  function plotDistributions(items) {
    if (!items.length) return;
    const traces = items.map((item, index) => ({ x: item.x, y: item.y, type: "bar", name: item.column, visible: index === 0, marker: { color: "#2563eb" } }));
    const buttons = items.map((item, index) => ({ label: item.column, method: "update", args: [{ visible: items.map((_, i) => i === index) }, { title: `Distribuição de ${item.column}` }] }));
    Plotly.newPlot("distribution-chart", traces, { title: { text: `Distribuição de ${items[0].column}`, x: .01, xanchor: "left", font: { size: 15 } }, updatemenus: [{ buttons, direction: "down", x: 0, y: 1.18 }], margin: { t: 75, r: 20, b: 60, l: 55 }, xaxis: { title: "Faixa de valor", gridcolor: "#e5e7eb" }, yaxis: { title: "Quantidade", gridcolor: "#e5e7eb" }, font: { color: "#4b5563" }, paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff" }, { responsive: true, displaylogo: false });
  }
  function plotCorrelation(rows) {
    const names = rows.map((r) => r.column);
    const z = rows.map((r) => names.map((name) => r[name]));
    Plotly.newPlot("correlation-chart", [{ z, x: names, y: names, type: "heatmap", colorscale: [[0, "#0b0d10"], [.5, "#ffffff"], [1, "#2563eb"]], zmin: -1, zmax: 1, hovertemplate: "%{x} × %{y}: %{z:.2f}<extra></extra>" }], { title: { text: "Correlação entre variáveis numéricas", x: .01, xanchor: "left", font: { size: 15 } }, margin: { t: 55, r: 25, b: 75, l: 90 }, font: { color: "#4b5563" }, paper_bgcolor: "#ffffff" }, { responsive: true, displaylogo: false });
  }

  function renderTimeSeries(data, warnings) {
    const m = data.metrics;
    let html = `<div class="metric-grid">
      ${metricCard("Observações", formatNumber(m.observations, 0))}
      ${metricCard("Média", formatNumber(m.average))}
      ${metricCard("Variação total", formatPercent(m.total_change_percentage))}
      ${metricCard("Tendência por período", formatNumber(m.trend_per_period))}
    </div>`;
    html += reportCard("Série, média móvel e tendência", `<div id="time-chart" class="chart" aria-label="Gráfico da série temporal"></div>`);
    if (data.evaluation) html += reportCard("Avaliação da previsão", `<div class="metric-grid">${metricCard("MAE", formatNumber(data.evaluation.mae))}${metricCard("RMSE", formatNumber(data.evaluation.rmse))}${metricCard("Pontos de teste", formatNumber(data.evaluation.test_observations, 0))}</div>`);
    html += interpretationSection(data.interpretation) + warningCards(warnings);
    $("#result-content").innerHTML = html;
    const series = data.series;
    const traces = [
      { x: series.map((r) => r.date), y: series.map((r) => r.value), name: "Valor", mode: "lines", line: { color: "#2563eb", width: 3 } },
      { x: series.map((r) => r.date), y: series.map((r) => r.rolling), name: "Média móvel", mode: "lines", line: { color: "#60a5fa", width: 2 } },
      { x: series.map((r) => r.date), y: series.map((r) => r.trend), name: "Tendência", mode: "lines", line: { color: "#0b0d10", dash: "dot" } },
    ];
    if (data.forecast.length) traces.push({ x: data.forecast.map((r) => r.date), y: data.forecast.map((r) => r.value), name: "Previsão linear", mode: "lines+markers", line: { color: "#1d4ed8", dash: "dash" } });
    Plotly.newPlot("time-chart", traces, { title: { text: `${data.settings.frequency} · ${m.observations} pontos`, x: .01, xanchor: "left", font: { size: 15 } }, margin: { t: 65, r: 20, b: 70, l: 60 }, xaxis: { title: "Tempo", rangeslider: { visible: true }, gridcolor: "#e5e7eb" }, yaxis: { title: "Valor", gridcolor: "#e5e7eb" }, legend: { orientation: "h", y: 1.12 }, hovermode: "x unified", font: { color: "#4b5563" }, paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff" }, { responsive: true, displaylogo: false });
  }

  function renderSupervised(data, warnings) {
    const m = data.metrics;
    const classification = data.settings.problem_type === "classification";
    const cards = classification
      ? [metricCard("Acurácia", formatPercent(m.accuracy * 100)), metricCard("Precisão", formatPercent(m.precision * 100)), metricCard("Recall", formatPercent(m.recall * 100)), metricCard("F1-score", formatPercent(m.f1 * 100))]
      : [metricCard("MAE", formatNumber(m.mae)), metricCard("MSE", formatNumber(m.mse)), metricCard("RMSE", formatNumber(m.rmse)), metricCard("R²", formatNumber(m.r2, 3))];
    let html = `<div class="metric-grid">${cards.join("")}</div>`;
    html += reportCard(classification ? "Matriz de confusão" : "Valores reais × previstos", `<div id="model-chart" class="chart"></div>`);
    html += reportCard("Como os dados foram preparados", `<ul class="transformation-list">${data.transformations.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul><p><small>${data.split.training_rows} linhas de treino · ${data.split.test_rows} linhas de teste · random_state 42</small></p>`);
    html += interpretationSection(data.interpretation) + warningCards(warnings);
    $("#result-content").innerHTML = html;
    if (classification) {
      Plotly.newPlot("model-chart", [{ z: data.chart.values, x: data.chart.labels, y: data.chart.labels, type: "heatmap", colorscale: [[0, "#ffffff"], [1, "#2563eb"]], text: data.chart.values, texttemplate: "%{text}", hovertemplate: "Real: %{y}<br>Previsto: %{x}<br>Casos: %{z}<extra></extra>" }], { title: { text: "Matriz de confusão no conjunto de teste", x: .01, xanchor: "left", font: { size: 15 } }, margin: { t: 55, r: 25, b: 70, l: 85 }, xaxis: { title: "Classe prevista" }, yaxis: { title: "Classe real" }, font: { color: "#4b5563" }, paper_bgcolor: "#ffffff" }, { responsive: true, displaylogo: false });
    } else {
      Plotly.newPlot("model-chart", [{ x: data.chart.actual, y: data.chart.predicted, mode: "markers", marker: { color: "#2563eb", opacity: .7 }, hovertemplate: "Real: %{x}<br>Previsto: %{y}<extra></extra>" }, { x: [Math.min(...data.chart.actual), Math.max(...data.chart.actual)], y: [Math.min(...data.chart.actual), Math.max(...data.chart.actual)], mode: "lines", line: { dash: "dot", color: "#0b0d10" }, name: "Referência ideal" }], { title: { text: "Valores reais e previstos no conjunto de teste", x: .01, xanchor: "left", font: { size: 15 } }, margin: { t: 55, r: 25, b: 60, l: 60 }, xaxis: { title: "Valor real", gridcolor: "#e5e7eb" }, yaxis: { title: "Valor previsto", gridcolor: "#e5e7eb" }, font: { color: "#4b5563" }, paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff" }, { responsive: true, displaylogo: false });
    }
  }

  function renderClustering(data, warnings) {
    const m = data.metrics;
    let html = `<div class="metric-grid">
      ${metricCard("Grupos", formatNumber(m.groups, 0))}
      ${metricCard("Observações", formatNumber(m.observations, 0))}
      ${metricCard("Silhouette", formatNumber(m.silhouette, 3))}
      ${metricCard("Variação visível no PCA", formatPercent(m.pca_explained_variance * 100))}
    </div>`;
    html += reportCard("Representação dos grupos em duas dimensões", `<div id="cluster-chart" class="chart"></div>`);
    const featureNames = data.settings.features;
    html += reportCard("Perfil numérico dos grupos", tableHtml(["Grupo", "Tamanho", "%", ...featureNames], data.profiles.map((profile) => [profile.group, profile.size, formatPercent(profile.percentage), ...featureNames.map((name) => formatNumber(profile.averages[name]))])));
    html += reportCard("Transformações aplicadas", `<ul class="transformation-list">${data.transformations.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`);
    html += interpretationSection(data.interpretation) + warningCards(warnings);
    $("#result-content").innerHTML = html;
    const groups = [...new Set(data.points.map((point) => point.group))];
    const traces = groups.map((group) => {
      const points = data.points.filter((point) => point.group === group);
      return { x: points.map((point) => point.x), y: points.map((point) => point.y), name: group, mode: "markers", marker: { size: 8, opacity: .72 }, hovertemplate: `${group}<br>PC1: %{x:.2f}<br>PC2: %{y:.2f}<extra></extra>` };
    });
    Plotly.newPlot("cluster-chart", traces, { title: { text: `Grupos projetados em duas dimensões · ${m.observations} registros`, x: .01, xanchor: "left", font: { size: 15 } }, colorway: ["#2563eb", "#0b0d10", "#60a5fa", "#64748b", "#1d4ed8", "#94a3b8"], margin: { t: 65, r: 25, b: 60, l: 60 }, xaxis: { title: "Componente principal 1", gridcolor: "#e5e7eb" }, yaxis: { title: "Componente principal 2", gridcolor: "#e5e7eb" }, legend: { orientation: "h", y: 1.12 }, font: { color: "#4b5563" }, paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff" }, { responsive: true, displaylogo: false });
  }

  function resetDataset() {
    state.dataset = null;
    state.result = null;
    state.filters = [];
    state.classificationRules = [];
    state.originalDataset = null;
    fileInput.value = "";
    clearAlerts();
    dropzone.classList.remove("hidden");
    $("#header-dataset-name").textContent = "Nenhum arquivo carregado";
    $("#header-dataset-meta").textContent = "Envie um CSV para iniciar";
    $("#header-change-file").classList.add("hidden");
    $("#processing-status").className = "processing-status";
    $("#processing-status").innerHTML = "<i></i> Aguardando arquivo";
    $("#classification-form").classList.add("hidden");
    $("#toggle-classification").setAttribute("aria-expanded", "false");
    $("#toggle-classification").textContent = "Configurar classificação";
    setStep(1);
  }

  $("#change-file").addEventListener("click", resetDataset);
  $("#header-change-file").addEventListener("click", resetDataset);
  $("#back-config").addEventListener("click", () => { clearAlerts(); setStep(2); });
  $("#print-report").addEventListener("click", () => window.print());
  $$("[data-nav-step]").forEach((item) => item.addEventListener("click", () => {
    setStep(Number(item.dataset.navStep));
  }));
  $$("[data-nav-analysis]").forEach((item) => item.addEventListener("click", () => {
    if (!state.dataset) {
      showAlerts("warning", "Envie um arquivo CSV antes de selecionar uma análise.");
      setStep(1);
      return;
    }
    activateAnalysis(item.dataset.navAnalysis);
  }));
  $("#menu-toggle").addEventListener("click", () => {
    const open = $("#sidebar").classList.toggle("open");
    $("#menu-toggle").setAttribute("aria-expanded", String(open));
  });
  $("#toggle-classification").addEventListener("click", () => {
    const form = $("#classification-form");
    const willOpen = form.classList.contains("hidden");
    form.classList.toggle("hidden", !willOpen);
    $("#toggle-classification").setAttribute("aria-expanded", String(willOpen));
    $("#toggle-classification").textContent = willOpen ? "Fechar configuração" : "Configurar classificação";
    if (willOpen && !state.classificationRules.length) {
      state.classificationRules.push(defaultClassificationRule());
    }
    if (willOpen) renderClassificationRules();
  });
  $("#add-classification-rule").addEventListener("click", () => {
    if (state.classificationRules.length >= 20) {
      showAlerts("warning", "Use no máximo 20 regras de classificação pela interface.");
      return;
    }
    state.classificationRules.push(defaultClassificationRule());
    renderClassificationRules();
  });
  $("#classification-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearAlerts();
    if (!state.classificationRules.length) {
      showAlerts("error", "Adicione ao menos uma regra de classificação.");
      return;
    }
    const button = event.submitter;
    const original = button.textContent;
    button.disabled = true;
    button.textContent = "Classificando registros...";
    $("#processing-status").className = "processing-status";
    $("#processing-status").innerHTML = `<i></i> Classificando ${formatNumber(state.dataset.rows, 0)} registros`;
    try {
      const response = await api("/api/datasets/classify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(classificationPayload()),
      });
      state.dataset = response.data;
      state.result = null;
      renderDataset();
      renderFields();
      renderClassificationRules();
      const messages = [response.message, ...response.warnings];
      showAlerts(response.warnings.length ? "warning" : "success", messages);
      $("#processing-status").className = "processing-status ready";
      $("#processing-status").innerHTML = "<i></i> Dataset classificado";
    } catch (error) {
      showAlerts("error", error.message);
      $("#processing-status").className = "processing-status";
      $("#processing-status").innerHTML = "<i></i> Falha na classificação";
    } finally {
      button.disabled = false;
      button.textContent = original;
    }
  });
  $("#sample-button").addEventListener("click", () => {
    const csv = "mes,receita,custos,canal\\n2026-01-01,68000,41000,Online\\n2026-02-01,72000,43500,Parceiros\\n2026-03-01,76500,44800,Online\\n2026-04-01,80300,46200,Loja\\n2026-05-01,89200,48900,Online\\n2026-06-01,96400,51200,Parceiros\\n2026-07-01,101500,53400,Online\\n2026-08-01,108900,55700,Loja\\n2026-09-01,114300,57600,Online\\n2026-10-01,121000,60100,Parceiros\\n2026-11-01,129800,62600,Online\\n2026-12-01,138400,65500,Loja";
    uploadFile(new File([csv], "exemplo_receita.csv", { type: "text/csv" }));
  });
})();
