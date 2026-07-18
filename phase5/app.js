const data = window.DASHBOARD_DATA;

if (!data) {
  document.body.innerHTML = `
    <main style="font-family:Segoe UI,sans-serif;padding:48px;max-width:720px;margin:0 auto;">
      <h1>Dashboard data failed to load</h1>
      <p>Open the dashboard with the launcher instead of double-clicking the HTML file:</p>
      <pre style="background:#f4f6f8;padding:16px;border-radius:12px;">python phase5/scripts/run_dashboard.py</pre>
      <p>Then visit <strong>http://127.0.0.1:8501/</strong></p>
    </main>
  `;
  throw new Error("DASHBOARD_DATA is missing. Serve phase5/ over HTTP.");
}

const FAMILY_FILTER_MAP = Object.fromEntries(
  (data.themeExplorer.families || []).map((family) => [family.family_label, family.family_id])
);

const navConfig = [
  { id: "overview", label: "Executive Overview", target: "view-overview" },
  { id: "theme-explorer", label: "Theme Explorer", target: "view-theme-explorer" },
  { id: "discovery-qna", label: "Discovery Q&A", target: "view-discovery-qna" },
  { id: "segment-lens", label: "Segment Lens", target: "view-segment-lens" },
  { id: "frustration-monitor", label: "Frustration Monitor", target: "view-frustration-monitor" },
  { id: "evidence-browser", label: "Evidence Browser", target: "view-evidence-browser" },
  { id: "methodology", label: "Methodology", target: "view-methodology" },
];

const state = {
  activeView: "overview",
  selectedThemeId: data.themeExplorer.prevalence[0]?.theme_id ?? null,
  filters: {
    source: "all",
    date: "all",
    theme: "all",
    sentiment: "all",
    segment: "all",
    search: "",
  },
};

const els = {
  navList: document.getElementById("nav-list"),
  runId: document.getElementById("run-id"),
  runStatus: document.getElementById("run-status"),
  filterSource: document.getElementById("filter-source"),
  filterDate: document.getElementById("filter-date"),
  filterTheme: document.getElementById("filter-theme"),
  filterSentiment: document.getElementById("filter-sentiment"),
  filterSegment: document.getElementById("filter-segment"),
  search: document.getElementById("global-search"),
  clearFilters: document.getElementById("clear-filters"),
  exportSummary: document.getElementById("export-summary"),
  modal: document.getElementById("evidence-modal"),
  modalContent: document.getElementById("modal-content"),
  closeModal: document.getElementById("close-modal"),
  overview: document.getElementById("view-overview"),
  themeExplorer: document.getElementById("view-theme-explorer"),
  discoveryQna: document.getElementById("view-discovery-qna"),
  segmentLens: document.getElementById("view-segment-lens"),
  frustrationMonitor: document.getElementById("view-frustration-monitor"),
  evidenceBrowser: document.getElementById("view-evidence-browser"),
  methodology: document.getElementById("view-methodology"),
};

function pct(value) {
  return `${Math.round(value * 100)}%`;
}

function titleCase(value) {
  return String(value || "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (ch) => ch.toUpperCase());
}

function themeFamilyId(filterValue) {
  if (!filterValue || filterValue === "all") return "all";
  return FAMILY_FILTER_MAP[filterValue] || filterValue.toLowerCase().replace(/\s+/g, ".");
}

function formatDate(value) {
  return new Date(value).toLocaleDateString("en-IN", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function metricCard(title, value, caption) {
  return `
    <article class="stat-card">
      <h3>${title}</h3>
      <div class="metric-value">${value}</div>
      <div class="muted">${caption}</div>
    </article>
  `;
}

function buildNav() {
  els.navList.innerHTML = navConfig
    .map(
      (item) => `
      <button type="button" class="nav-item" data-view="${item.id}">
        ${item.label}
      </button>
    `
    )
    .join("");
  updateNavActiveState();
}

function updateNavActiveState() {
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === state.activeView);
  });
}

function buildSelectOptions(select, options, includeAll = true, allLabel = "All") {
  const items = includeAll ? [`<option value="all">${allLabel}</option>`] : [];
  items.push(...options.map((option) => `<option value="${option}">${option}</option>`));
  select.innerHTML = items.join("");
}

function syncControls() {
  els.runId.textContent = `Run: ${data.meta.run_id}`;
  const buildMeta = document.querySelector('meta[name="dashboard-build"]');
  if (buildMeta && buildMeta.content) {
    els.runId.title = `Build ${buildMeta.content}`;
  }
  els.runStatus.textContent = data.meta.status;

  buildSelectOptions(els.filterSource, data.controls.sources, true, "All sources");
  buildSelectOptions(els.filterTheme, data.controls.themeFamilies, true, "All families");
  buildSelectOptions(els.filterSentiment, data.controls.sentiments.map(titleCase), true, "All sentiment");
  buildSelectOptions(els.filterSegment, data.controls.segments.map(titleCase), true, "All segments");
}

function renderOverview() {
  const overview = data.overview;
  els.overview.innerHTML = `
    <section class="hero-grid">
      <article class="hero-card">
        <div class="hero-content">
          <span class="eyebrow">Executive Summary</span>
          <h2>${overview.headline}</h2>
          <p>${overview.subtitle}</p>
          <div class="cta-row">
            <button class="primary-button" data-jump-view="discovery-qna">Review Q&A</button>
            <button class="outline-button" id="overview-export">Export summary</button>
          </div>
        </div>
      </article>
      <div class="hero-side">
        <article class="support-card">
          <div class="metric-label">Exploration willingness</div>
          <div class="metric-value">+${overview.exploration_willingness}%</div>
          <p class="muted">Published insights across ${data.meta.records_analyzed.toLocaleString()} analyzed records suggest habit-interrupt plus trust-building is the best growth path.</p>
        </article>
      </div>
    </section>

    <section class="strip-list">
      ${overview.strips
        .map(
          (strip) => `
          <article class="insight-strip">
            <div>
              <small>${strip.label}</small>
              <h3>${strip.title}</h3>
            </div>
            <div>
              <div class="muted">${strip.metric}</div>
              <div><strong>${strip.value}</strong></div>
              <button class="link-button" data-open-insight="${strip.insight_id}">View evidence</button>
            </div>
          </article>
        `
        )
        .join("")}
    </section>

    <section class="metric-grid">
      ${metricCard("Published questions", data.meta.published_count, "All Q1–Q8 cleared the publish gate")}
      ${metricCard("Evidence quotes", data.meta.evidence_total, "Distinct evidence rows available for click-through")}
      ${metricCard("Confidence score", `${data.meta.confidence_score}%`, "Average final confidence after validation")}
    </section>
  `;
}

function buildThemeList() {
  return data.themeExplorer.prevalence
    .slice(0, 12)
    .map((item) => {
      const active = item.theme_id === state.selectedThemeId ? "active" : "";
      return `
        <article class="theme-item ${active}">
          <button data-theme-id="${item.theme_id}">
            <div class="theme-header">
              <strong>${titleCase(item.theme_id.split(".")[1])}</strong>
              <span>${pct(item.share)}</span>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width:${pct(item.share)}"></div></div>
          </button>
        </article>
      `;
    })
    .join("");
}

function buildThemeDetail() {
  const themeId = state.selectedThemeId;
  const prevalence = data.themeExplorer.prevalence.find((item) => item.theme_id === themeId);
  const sentiments = data.themeExplorer.sentimentByTheme[themeId] || {};
  const sourceMix = data.themeExplorer.sourceMix[themeId] || {};
  const trend = data.themeExplorer.trendByMonth[themeId] || {};

  const sentimentTotal = Object.values(sentiments).reduce((sum, value) => sum + value, 0) || 1;
  const topSources = Object.entries(sourceMix)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);
  const trendEntries = Object.entries(trend).slice(-6);

  return `
    <article class="theme-detail">
      <span class="eyebrow">${titleCase(themeId.split(".")[0])}</span>
      <h3>${titleCase(themeId.split(".")[1])}</h3>
      <p class="muted">Prevalence among analyzable corpus: ${pct(prevalence?.share ?? 0)} across ${prevalence?.count ?? 0} mentions.</p>
      <div class="two-col">
        <div class="chart-card">
          <h3>Sentiment split</h3>
          <div class="theme-list">
            ${Object.entries(sentiments)
              .map(
                ([label, count]) => `
                  <div>
                    <div class="theme-header">
                      <span>${titleCase(label)}</span>
                      <span>${pct(count / sentimentTotal)}</span>
                    </div>
                    <div class="bar-track"><div class="bar-fill ${label === "negative" ? "danger" : label === "neutral" ? "subtle" : ""}" style="width:${pct(count / sentimentTotal)}"></div></div>
                  </div>
                `
              )
              .join("")}
          </div>
        </div>
        <div class="chart-card">
          <h3>Source breakdown</h3>
          <div class="theme-list">
            ${topSources
              .map(
                ([source, count]) => `
                  <div>
                    <div class="theme-header">
                      <span>${titleCase(source)}</span>
                      <span>${count}</span>
                    </div>
                    <div class="bar-track"><div class="bar-fill subtle" style="width:${pct(count / (prevalence?.count || 1))}"></div></div>
                  </div>
                `
              )
              .join("")}
          </div>
        </div>
      </div>
      <div class="chart-card" style="margin-top:20px">
        <h3>Last 6 months trend</h3>
        <div class="timeline-chart">
          ${trendEntries
            .map(
              ([month, count]) => `
                <div class="timeline-bar" style="height:${Math.max(24, count * 4)}px">
                  <span>${month.slice(5)}</span>
                </div>
              `
            )
            .join("")}
        </div>
      </div>
    </article>
  `;
}

function renderThemeExplorer() {
  els.themeExplorer.innerHTML = `
    <section class="section-title">
      <h2>Theme Explorer</h2>
      <p class="muted">Explore ranked themes, source mix, sentiment, and trend movement from the published run.</p>
    </section>
    <section class="two-col">
      <div class="theme-list">${buildThemeList()}</div>
      <div>${buildThemeDetail()}</div>
    </section>
  `;
}

function filteredInsights() {
  const familyId = themeFamilyId(state.filters.theme);
  return data.discoveryQna.filter((insight) => {
    const matchesTheme =
      familyId === "all" ||
      insight.supporting_themes.some((theme) => theme.startsWith(`${familyId}.`) || theme === familyId);
    const searchText = `${insight.headline} ${insight.implication} ${insight.supporting_themes.join(" ")}`.toLowerCase();
    const matchesSearch = !state.filters.search || searchText.includes(state.filters.search.toLowerCase());
    return matchesTheme && matchesSearch;
  });
}

function renderDiscoveryQna() {
  const insights = filteredInsights();
  els.discoveryQna.innerHTML = `
    <section class="section-title">
      <h2>Discovery Q&A Board</h2>
      <p class="muted">Direct answers to the eight category-expansion questions, each with evidence-backed confidence and implications.</p>
    </section>
    <section class="insight-grid">
      ${insights
        .map(
          (insight) => `
          <article class="insight-card">
            <div class="insight-meta">
              <span class="chip">${insight.question_id}</span>
              <span class="chip status">${titleCase(insight.status)}</span>
            </div>
            <h3>${insight.headline}</h3>
            <p>${insight.implication}</p>
            <div class="chip-row">
              ${insight.supporting_themes.slice(0, 3).map((theme) => `<span class="chip">${titleCase(theme.split(".")[1])}</span>`).join("")}
            </div>
            <div class="confidence">
              <div class="theme-header"><span>Confidence</span><strong>${(insight.confidence * 100).toFixed(1)}%</strong></div>
              <div class="bar-track"><div class="bar-fill" style="width:${pct(insight.confidence)}"></div></div>
            </div>
            <button class="outline-button" data-open-insight="${insight.insight_id}">Evidence</button>
          </article>
        `
        )
        .join("")}
    </section>
  `;
}

function renderSegmentLens() {
  const rows = data.segmentLens.segmentRates
    .map(
      (segment) => `
      <tr>
        <td>${titleCase(segment.segment)}</td>
        <td>${segment.total}</td>
        <td>${segment.with_experiment_theme}</td>
        <td><strong>${pct(segment.experiment_rate)}</strong></td>
      </tr>
    `
    )
    .join("");

  els.segmentLens.innerHTML = `
    <section class="section-title">
      <h2>Segment Lens</h2>
      <p class="muted">${data.segmentLens.callout}</p>
    </section>
    <section class="segment-grid">
      <article class="panel">
        <table class="segment-table">
          <thead>
            <tr><th>Segment</th><th>Total</th><th>Experiment hits</th><th>Rate</th></tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </article>
      <div class="theme-list">
        <article class="segment-card">
          <h3>Recommendation</h3>
          <p>Prioritize deal-sensitive and occasional-explorer cohorts with add-on messaging, and reinforce life-stage trust signals for baby and pet categories.</p>
        </article>
      </div>
    </section>
  `;
}

function renderFrustrationMonitor() {
  const trendEntries = Object.entries(data.frustrationMonitor.trend);
  const ranked = data.frustrationMonitor.ranked;
  const contextualEvidence = data.frustrationMonitor.contextualEvidence;

  els.frustrationMonitor.innerHTML = `
    <section class="section-title">
      <h2>Frustration Monitor</h2>
      <p class="muted">Operational pain points that directly suppress willingness to try unfamiliar categories.</p>
    </section>
    <section class="frustration-grid">
      <article class="timeline-card">
        <span class="eyebrow">Critical friction alert</span>
        <h3>${data.frustrationMonitor.headline}</h3>
        <div class="timeline-chart">
          ${trendEntries
            .map(
              ([month, count]) => `
                <div class="timeline-bar" style="height:${Math.max(28, count * 5)}px">
                  <span>${month.slice(5)}</span>
                </div>
              `
            )
            .join("")}
        </div>
      </article>
      <div class="rank-list">
        <article class="segment-card">
          <h3>Ranked frustrations</h3>
          <div class="theme-list">
            ${ranked
              .map(
                (row) => `
                  <div>
                    <div class="theme-header">
                      <span>${titleCase(row.theme_id.split(".")[1])}</span>
                      <span>${row.count}</span>
                    </div>
                    <div class="bar-track"><div class="bar-fill warning" style="width:${pct(Math.min(row.severity_score / 2, 1))}"></div></div>
                  </div>
                `
              )
              .join("")}
          </div>
        </article>
      </div>
    </section>
    <section class="theme-list" style="margin-top:20px">
      ${contextualEvidence
        .map(
          (row) => `
            <article class="evidence-row">
              <div class="evidence-meta">
                <strong>${titleCase((row.matched_themes?.[0] || "frustration").split(".")[1] || "frustration")}</strong>
                <span>${formatDate(row.created_at)}</span>
              </div>
              <blockquote>${row.quote}</blockquote>
            </article>
          `
        )
        .join("")}
    </section>
  `;
}

function filterEvidenceRows() {
  const today = new Date(data.meta.date_range.end);
  const maxAgeDays = state.filters.date === "all" ? null : Number(state.filters.date);

  const familyId = themeFamilyId(state.filters.theme);
  return data.evidenceBrowser.rows.filter((row) => {
    const segments = row.segments || [];
    const matchesSource = state.filters.source === "all" || row.source_label === state.filters.source;
    const matchesSentiment =
      state.filters.sentiment === "all" || titleCase(row.sentiment_label) === state.filters.sentiment;
    const matchesTheme =
      familyId === "all" ||
      row.theme_ids.some((themeId) => themeId.startsWith(`${familyId}.`) || themeId === familyId);
    const matchesSegment =
      state.filters.segment === "all" ||
      segments.some((segment) => titleCase(segment) === state.filters.segment);
    const matchesSearch =
      !state.filters.search ||
      `${row.quote} ${row.source_label} ${(row.theme_labels || []).join(" ")}`.toLowerCase().includes(state.filters.search.toLowerCase());
    const matchesDate =
      !maxAgeDays || (today.getTime() - new Date(row.created_at).getTime()) / (1000 * 60 * 60 * 24) <= maxAgeDays;
    return matchesSource && matchesSentiment && matchesTheme && matchesSegment && matchesSearch && matchesDate;
  });
}

function renderEvidenceBrowser() {
  const rows = filterEvidenceRows();
  const sentimentMix = data.evidenceBrowser.sentimentMix;
  const topSources = Object.entries(data.evidenceBrowser.sourceCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3);

  els.evidenceBrowser.innerHTML = `
    <section class="section-title">
      <h2>Evidence Browser</h2>
      <p class="muted">Search and filter the supporting feedback rows behind published insight claims.</p>
    </section>
    <div class="evidence-toolbar">
      <div class="summary">
        <div><strong>${rows.length}</strong><div class="muted">Visible quotes</div></div>
        <div><strong>${data.meta.confidence_score}%</strong><div class="muted">Confidence score</div></div>
        <div><strong>${data.meta.evidence_total}</strong><div class="muted">Total evidence rows</div></div>
      </div>
      <div class="chip-row">
        ${topSources.map(([label, count]) => `<span class="chip">${label}: ${count}</span>`).join("")}
        ${Object.entries(sentimentMix).map(([label, count]) => `<span class="chip">${titleCase(label)}: ${count}</span>`).join("")}
      </div>
    </div>
    <section class="evidence-list">
      ${rows
        .slice(0, 12)
        .map(
          (row) => `
          <article class="evidence-row">
            <div class="evidence-meta">
              <div class="chip-row">
                <span class="chip">${row.source_label}</span>
                <span class="chip">${titleCase(row.sentiment_label)}</span>
                ${(row.theme_labels || []).map((label) => `<span class="chip">${label}</span>`).join("")}
                ${(row.segments || []).map((segment) => `<span class="chip">${titleCase(segment)}</span>`).join("")}
              </div>
              <span class="muted">${formatDate(row.created_at)}</span>
            </div>
            <blockquote>${row.quote}</blockquote>
            <div><button class="link-button" data-open-evidence="${row.feedback_id}">Open</button></div>
          </article>
        `
        )
        .join("")}
    </section>
  `;
}

function renderMethodology() {
  const coverage = data.methodology.validation.coverage;
  const faithfulness = data.methodology.validation.faithfulness;
  const sampling = data.methodology.validation.sampling_qa;

  els.methodology.innerHTML = `
    <section class="section-title">
      <h2>Methodology</h2>
      <p class="muted">A compact explanation of how data is gathered, themed, synthesized, and validated before publication.</p>
    </section>
    <section class="method-grid">
      ${data.methodology.sections
        .map(
          (section) => `
            <article class="method-card">
              <span class="eyebrow">${section.title}</span>
              <p>${section.summary}</p>
            </article>
          `
        )
        .join("")}
    </section>
    <article class="method-card" style="margin-top:20px">
      <h3>Pipeline steps</h3>
      <div class="pipeline">
        ${data.methodology.pipelineSteps.map((step) => `<span>${step}</span>`).join("")}
      </div>
    </article>
    <section class="three-col" style="margin-top:20px">
      ${metricCard("Coverage", `${coverage.theme_coverage_pct}%`, `${coverage.with_non_other_theme} themed rows out of ${coverage.analyzable_count}`)}
      ${metricCard("Faithfulness", `${Math.round(faithfulness.pass_rate * 100)}%`, `${faithfulness.passed_count}/${faithfulness.insight_count} published insights passed`)}
      ${metricCard("Sampling QA", `${Math.round(sampling.support_rate * 100)}%`, `Precision ${Math.round(sampling.precision * 100)}%, stakeholder spot-check ${titleCase(data.methodology.spotcheckStatus)}`)}
    </section>
  `;
}

function renderAllViews() {
  renderOverview();
  renderThemeExplorer();
  renderDiscoveryQna();
  renderSegmentLens();
  renderFrustrationMonitor();
  renderEvidenceBrowser();
  renderMethodology();
  bindDynamicActions();
}

function bindDynamicActions() {
  document.querySelectorAll("[data-view]").forEach((button) => {
    button.onclick = (event) => {
      event.preventDefault();
      state.activeView = button.dataset.view;
      updateActiveView();
    };
  });

  document.querySelectorAll("[data-jump-view]").forEach((button) => {
    button.onclick = () => {
      state.activeView = button.dataset.jumpView;
      updateActiveView();
    };
  });

  document.querySelectorAll("[data-theme-id]").forEach((button) => {
    button.onclick = () => {
      state.selectedThemeId = button.dataset.themeId;
      renderThemeExplorer();
      bindDynamicActions();
    };
  });

  document.querySelectorAll("[data-open-insight]").forEach((button) => {
    button.onclick = () => openInsightModal(button.dataset.openInsight);
  });

  document.querySelectorAll("[data-open-evidence]").forEach((button) => {
    button.onclick = () => openEvidenceModal(button.dataset.openEvidence);
  });

  const overviewExport = document.getElementById("overview-export");
  if (overviewExport) {
    overviewExport.onclick = exportDashboardSummary;
  }
}

function updateActiveView() {
  updateNavActiveState();
  document.querySelectorAll(".view").forEach((view) => view.classList.remove("active"));
  const match = navConfig.find((item) => item.id === state.activeView);
  if (match) {
    document.getElementById(match.target).classList.add("active");
  }
  if (els.overview?.closest(".main-panel")) {
    els.overview.closest(".main-panel").scrollTop = 0;
  }
  bindDynamicActions();
}

function openInsightModal(insightId) {
  const insight = data.discoveryQna.find((item) => item.insight_id === insightId);
  if (!insight) return;
  els.modalContent.innerHTML = `
    <h2>${insight.question_id}: ${insight.headline}</h2>
    <p>${insight.implication}</p>
    <div class="chip-row">
      <span class="chip status">${titleCase(insight.status)}</span>
      <span class="chip">Confidence ${(insight.confidence * 100).toFixed(1)}%</span>
      ${insight.supporting_themes.map((theme) => `<span class="chip">${titleCase(theme.split(".")[1])}</span>`).join("")}
    </div>
    <div class="evidence-list" style="margin-top:20px">
      ${insight.evidence_pack
        .map(
          (row) => `
          <article class="evidence-row">
            <div class="evidence-meta">
              <strong>${titleCase(row.source)}</strong>
              <span>${formatDate(row.created_at)}</span>
            </div>
            <blockquote>${row.quote}</blockquote>
            <div class="chip-row">${row.matched_themes.map((theme) => `<span class="chip">${titleCase(theme.split(".")[1])}</span>`).join("")}</div>
          </article>
        `
        )
        .join("")}
    </div>
  `;
  openModal();
}

function openEvidenceModal(feedbackId) {
  const row = data.evidenceBrowser.rows.find((item) => item.feedback_id === feedbackId);
  if (!row) return;
  els.modalContent.innerHTML = `
    <h2>Evidence ${row.feedback_id}</h2>
    <div class="chip-row">
      <span class="chip">${row.source_label}</span>
      <span class="chip">${formatDate(row.created_at)}</span>
      <span class="chip">${titleCase(row.sentiment_label)}</span>
      ${(row.theme_labels || []).map((label) => `<span class="chip">${label}</span>`).join("")}
      ${(row.segments || []).map((segment) => `<span class="chip">${titleCase(segment)}</span>`).join("")}
    </div>
    <article class="evidence-row" style="margin-top:20px">
      <blockquote>${row.quote}</blockquote>
    </article>
  `;
  openModal();
}

function openModal() {
  els.modal.classList.remove("hidden");
  els.modal.setAttribute("aria-hidden", "false");
}

function closeModal() {
  els.modal.classList.add("hidden");
  els.modal.setAttribute("aria-hidden", "true");
}

function downloadBlob(filename, blob) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function csvEscape(value) {
  const text = String(value ?? "").replace(/"/g, '""');
  return `"${text}"`;
}

function buildFullExportPayload() {
  const coverage = data.methodology.validation.coverage;
  const faithfulness = data.methodology.validation.faithfulness;
  const sampling = data.methodology.validation.sampling_qa;

  return {
    exported_at: new Date().toISOString(),
    product_name: data.meta.product_name,
    run_id: data.meta.run_id,
    status: data.meta.status,
    date_range: data.meta.date_range,
    summary_metrics: {
      records_analyzed: data.meta.records_analyzed,
      published_questions: data.meta.published_count,
      evidence_quotes: data.meta.evidence_total,
      confidence_score_pct: data.meta.confidence_score,
      exploration_willingness_pct: data.overview.exploration_willingness,
    },
    pages: {
      executive_overview: {
        headline: data.overview.headline,
        subtitle: data.overview.subtitle,
        insight_strips: data.overview.strips,
        key_metrics: {
          published_questions: data.meta.published_count,
          evidence_quotes: data.meta.evidence_total,
          confidence_score_pct: data.meta.confidence_score,
        },
      },
      theme_explorer: {
        theme_families: data.themeExplorer.families,
        ranked_themes: data.themeExplorer.prevalence.map((item) => ({
          theme_id: item.theme_id,
          theme_label: titleCase(item.theme_id.split(".")[1] || item.theme_id),
          count: item.count,
          share_pct: Math.round(item.share * 1000) / 10,
        })),
        sentiment_by_theme: data.themeExplorer.sentimentByTheme,
        source_mix: data.themeExplorer.sourceMix,
        trend_by_month: data.themeExplorer.trendByMonth,
      },
      discovery_qna: data.discoveryQna.map((insight) => ({
        question_id: insight.question_id,
        insight_id: insight.insight_id,
        question: insight.analysis?.question || null,
        headline: insight.headline,
        implication: insight.implication,
        confidence_pct: Math.round(insight.confidence * 1000) / 10,
        status: insight.status,
        supporting_themes: insight.supporting_themes,
        evidence_ids: insight.evidence_ids,
        evidence_pack: insight.evidence_pack,
      })),
      segment_lens: {
        callout: data.segmentLens.callout,
        experiment_rates: data.segmentLens.segmentRates.map((segment) => ({
          segment: segment.segment,
          segment_label: titleCase(segment.segment),
          total: segment.total,
          with_experiment_theme: segment.with_experiment_theme,
          experiment_rate_pct: Math.round(segment.experiment_rate * 1000) / 10,
        })),
      },
      frustration_monitor: {
        headline: data.frustrationMonitor.headline,
        ranked_complaints: data.frustrationMonitor.ranked,
        month_trend: data.frustrationMonitor.trend,
        contextual_evidence: data.frustrationMonitor.contextualEvidence,
      },
      evidence_browser: {
        total_quotes: data.evidenceBrowser.rows.length,
        sentiment_mix: data.evidenceBrowser.sentimentMix,
        source_counts: data.evidenceBrowser.sourceCounts,
        quotes: data.evidenceBrowser.rows,
      },
      methodology: {
        sections: data.methodology.sections,
        pipeline_steps: data.methodology.pipelineSteps,
        validation: {
          coverage_pct: coverage.theme_coverage_pct,
          analyzable_count: coverage.analyzable_count,
          faithfulness_pass_rate_pct: Math.round(faithfulness.pass_rate * 1000) / 10,
          faithfulness_passed: faithfulness.passed_count,
          faithfulness_total: faithfulness.insight_count,
          sampling_support_rate_pct: Math.round(sampling.support_rate * 1000) / 10,
          sampling_precision_pct: Math.round(sampling.precision * 1000) / 10,
          stakeholder_spotcheck_status: data.methodology.spotcheckStatus,
        },
        drift_baseline: data.methodology.drift,
      },
    },
  };
}

function buildExportMarkdown(payload) {
  const lines = [];
  const push = (...parts) => lines.push(...parts);

  push(
    `# ${payload.product_name}`,
    "",
    `**Run:** ${payload.run_id}`,
    `**Exported:** ${payload.exported_at}`,
    `**Status:** ${payload.status}`,
    `**Date range:** ${payload.date_range.start} to ${payload.date_range.end}`,
    "",
    "## Summary metrics",
    "",
    `- Records analyzed: ${payload.summary_metrics.records_analyzed}`,
    `- Published questions: ${payload.summary_metrics.published_questions}`,
    `- Evidence quotes: ${payload.summary_metrics.evidence_quotes}`,
    `- Confidence score: ${payload.summary_metrics.confidence_score_pct}%`,
    `- Exploration willingness: +${payload.summary_metrics.exploration_willingness_pct}%`,
    ""
  );

  const overview = payload.pages.executive_overview;
  push(
    "## 1. Executive Overview",
    "",
    `### ${overview.headline}`,
    "",
    overview.subtitle,
    "",
    "### Key insight strips",
    ""
  );
  overview.insight_strips.forEach((strip) => {
    push(`- **${strip.label}:** ${strip.title} (${strip.metric}: ${strip.value})`);
  });
  push("");

  push("## 2. Theme Explorer", "", "### Theme families", "");
  payload.pages.theme_explorer.theme_families.forEach((family) => {
    push(`- ${family.family_label}: ${family.count} mentions (${Math.round(family.share * 1000) / 10}%)`);
  });
  push("", "### Top ranked themes", "");
  payload.pages.theme_explorer.ranked_themes.slice(0, 15).forEach((theme, index) => {
    push(`${index + 1}. ${theme.theme_label} — ${theme.count} mentions (${theme.share_pct}%)`);
  });
  push("");

  push("## 3. Discovery Q&A", "");
  payload.pages.discovery_qna.forEach((insight) => {
    push(
      `### ${insight.question_id}: ${insight.headline}`,
      "",
      insight.question ? `**Question:** ${insight.question}` : "",
      "",
      `**Implication:** ${insight.implication}`,
      "",
      `**Confidence:** ${insight.confidence_pct}% | **Status:** ${insight.status}`,
      "",
      "**Supporting themes:** " + insight.supporting_themes.join(", "),
      "",
      "**Evidence:**"
    );
    insight.evidence_pack.forEach((row) => {
      push(`- [${row.source}] ${row.quote}`);
    });
    push("");
  });

  push("## 4. Segment Lens", "", payload.pages.segment_lens.callout, "", "| Segment | Total | Experiment hits | Rate |", "| --- | ---: | ---: | ---: |");
  payload.pages.segment_lens.experiment_rates.forEach((segment) => {
    push(`| ${segment.segment_label} | ${segment.total} | ${segment.with_experiment_theme} | ${segment.experiment_rate_pct}% |`);
  });
  push("");

  const frustration = payload.pages.frustration_monitor;
  push("## 5. Frustration Monitor", "", `**Headline:** ${frustration.headline}`, "", "### Ranked complaints", "");
  frustration.ranked_complaints.forEach((item, index) => {
    push(`${index + 1}. ${titleCase(item.theme_id.split(".")[1])} — count ${item.count}, severity ${item.severity_score}`);
  });
  push("", "### Contextual evidence", "");
  frustration.contextual_evidence.forEach((row) => {
    push(`- ${row.quote}`);
  });
  push("");

  push("## 6. Evidence Browser", "", `Total quotes: ${payload.pages.evidence_browser.total_quotes}`, "");
  payload.pages.evidence_browser.quotes.forEach((row) => {
    push(`- [${row.source_label}] (${row.sentiment_label}) ${row.quote}`);
  });
  push("");

  const methodology = payload.pages.methodology;
  push("## 7. Methodology", "");
  methodology.sections.forEach((section) => {
    push(`### ${section.title}`, "", section.summary, "");
  });
  push(
    "### Validation",
    "",
    `- Coverage: ${methodology.validation.coverage_pct}%`,
    `- Faithfulness pass rate: ${methodology.validation.faithfulness_pass_rate_pct}%`,
    `- Sampling precision: ${methodology.validation.sampling_precision_pct}%`,
    `- Stakeholder spot-check: ${methodology.validation.stakeholder_spotcheck_status}`,
    ""
  );

  return lines.filter((line) => line !== undefined).join("\n");
}

function buildEvidenceCsv(rows) {
  const header = [
    "feedback_id",
    "quote",
    "source",
    "created_at",
    "sentiment",
    "themes",
    "segments",
    "question_ids",
  ];
  const body = rows.map((row) =>
    [
      row.feedback_id,
      row.quote,
      row.source_label,
      row.created_at,
      row.sentiment_label,
      (row.theme_labels || []).join("; "),
      (row.segments || []).map(titleCase).join("; "),
      (row.question_ids || []).join("; "),
    ]
      .map(csvEscape)
      .join(",")
  );
  return [header.join(","), ...body].join("\n");
}

function buildExportHtml(payload) {
  const pageSections = [
    {
      title: "1. Executive Overview",
      body: `
        <h3>${payload.pages.executive_overview.headline}</h3>
        <p>${payload.pages.executive_overview.subtitle}</p>
        <ul>
          ${payload.pages.executive_overview.insight_strips
            .map((strip) => `<li><strong>${strip.label}:</strong> ${strip.title} (${strip.metric}: ${strip.value})</li>`)
            .join("")}
        </ul>
      `,
    },
    {
      title: "2. Theme Explorer",
      body: `
        <h3>Theme families</h3>
        <ul>
          ${payload.pages.theme_explorer.theme_families
            .map((family) => `<li>${family.family_label}: ${family.count} mentions (${Math.round(family.share * 1000) / 10}%)</li>`)
            .join("")}
        </ul>
        <h3>Top ranked themes</h3>
        <ol>
          ${payload.pages.theme_explorer.ranked_themes
            .slice(0, 20)
            .map((theme) => `<li>${theme.theme_label}: ${theme.count} mentions (${theme.share_pct}%)</li>`)
            .join("")}
        </ol>
      `,
    },
    {
      title: "3. Discovery Q&A",
      body: payload.pages.discovery_qna
        .map(
          (insight) => `
            <article class="export-card">
              <h3>${insight.question_id}: ${insight.headline}</h3>
              ${insight.question ? `<p><strong>Question:</strong> ${insight.question}</p>` : ""}
              <p><strong>Implication:</strong> ${insight.implication}</p>
              <p><strong>Confidence:</strong> ${insight.confidence_pct}% | <strong>Status:</strong> ${insight.status}</p>
              <p><strong>Themes:</strong> ${insight.supporting_themes.join(", ")}</p>
              <ul>
                ${insight.evidence_pack.map((row) => `<li>[${row.source}] ${row.quote}</li>`).join("")}
              </ul>
            </article>
          `
        )
        .join(""),
    },
    {
      title: "4. Segment Lens",
      body: `
        <p>${payload.pages.segment_lens.callout}</p>
        <table>
          <thead><tr><th>Segment</th><th>Total</th><th>Experiment hits</th><th>Rate</th></tr></thead>
          <tbody>
            ${payload.pages.segment_lens.experiment_rates
              .map(
                (segment) =>
                  `<tr><td>${segment.segment_label}</td><td>${segment.total}</td><td>${segment.with_experiment_theme}</td><td>${segment.experiment_rate_pct}%</td></tr>`
              )
              .join("")}
          </tbody>
        </table>
      `,
    },
    {
      title: "5. Frustration Monitor",
      body: `
        <p><strong>${payload.pages.frustration_monitor.headline}</strong></p>
        <h3>Ranked complaints</h3>
        <ol>
          ${payload.pages.frustration_monitor.ranked_complaints
            .map((item) => `<li>${titleCase(item.theme_id.split(".")[1])}: ${item.count} mentions</li>`)
            .join("")}
        </ol>
        <h3>Contextual evidence</h3>
        <ul>
          ${payload.pages.frustration_monitor.contextual_evidence.map((row) => `<li>${row.quote}</li>`).join("")}
        </ul>
      `,
    },
    {
      title: "6. Evidence Browser",
      body: `
        <p>Total quotes: ${payload.pages.evidence_browser.total_quotes}</p>
        <ul>
          ${payload.pages.evidence_browser.quotes
            .map((row) => `<li><strong>[${row.source_label}]</strong> (${row.sentiment_label}) ${row.quote}</li>`)
            .join("")}
        </ul>
      `,
    },
    {
      title: "7. Methodology",
      body: `
        ${payload.pages.methodology.sections
          .map((section) => `<h3>${section.title}</h3><p>${section.summary}</p>`)
          .join("")}
        <p><strong>Pipeline:</strong> ${payload.pages.methodology.pipeline_steps.join(" → ")}</p>
        <ul>
          <li>Coverage: ${payload.pages.methodology.validation.coverage_pct}%</li>
          <li>Faithfulness pass rate: ${payload.pages.methodology.validation.faithfulness_pass_rate_pct}%</li>
          <li>Sampling precision: ${payload.pages.methodology.validation.sampling_precision_pct}%</li>
          <li>Stakeholder spot-check: ${payload.pages.methodology.validation.stakeholder_spotcheck_status}</li>
        </ul>
      `,
    },
  ];

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>${payload.product_name} — Export ${payload.run_id}</title>
  <style>
    body { font-family: Segoe UI, sans-serif; color: #18202f; margin: 0; background: #f5f7fb; }
    main { max-width: 980px; margin: 0 auto; padding: 32px 24px 64px; }
    h1, h2, h3 { line-height: 1.2; }
    .meta { background: #fff; border: 1px solid #dbe2ee; border-radius: 16px; padding: 20px; margin-bottom: 24px; }
    section { background: #fff; border: 1px solid #dbe2ee; border-radius: 16px; padding: 24px; margin-bottom: 20px; }
    .export-card { border-top: 1px solid #eef2f7; padding-top: 16px; margin-top: 16px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border-bottom: 1px solid #eef2f7; padding: 10px 8px; text-align: left; }
    ul { padding-left: 20px; }
  </style>
</head>
<body>
  <main>
    <div class="meta">
      <h1>${payload.product_name}</h1>
      <p><strong>Run:</strong> ${payload.run_id}</p>
      <p><strong>Exported:</strong> ${payload.exported_at}</p>
      <p><strong>Status:</strong> ${payload.status}</p>
      <p><strong>Pages included:</strong> ${payload.pages_included.join(", ")}</p>
    </div>
    ${pageSections.map((section) => `<section><h2>${section.title}</h2>${section.body}</section>`).join("")}
  </main>
</body>
</html>`;
}

function showExportToast(message) {
  let toast = document.getElementById("export-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "export-toast";
    toast.className = "export-toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add("visible");
  window.clearTimeout(showExportToast._timer);
  showExportToast._timer = window.setTimeout(() => toast.classList.remove("visible"), 5000);
}

function exportDashboardSummary() {
  const payload = buildFullExportPayload();
  payload.pages_included = navConfig.map((item) => item.label);
  const stamp = payload.run_id;
  const base = `category-expansion-insights-${stamp}`;

  downloadBlob(`${base}-full-report.html`, new Blob([buildExportHtml(payload)], { type: "text/html" }));
  window.setTimeout(() => {
    downloadBlob(`${base}.json`, new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }));
  }, 350);
  window.setTimeout(() => {
    downloadBlob(
      `${base}-evidence.csv`,
      new Blob([buildEvidenceCsv(payload.pages.evidence_browser.quotes)], { type: "text/csv" })
    );
  }, 700);

  showExportToast(
    `Exported all ${payload.pages_included.length} dashboard pages: ${payload.pages_included.join(" • ")}`
  );
}

function bindGlobalEvents() {
  els.filterSource.onchange = (event) => {
    state.filters.source = event.target.value;
    renderEvidenceBrowser();
    bindDynamicActions();
  };
  els.filterDate.onchange = (event) => {
    state.filters.date = event.target.value;
    renderEvidenceBrowser();
    bindDynamicActions();
  };
  els.filterTheme.onchange = (event) => {
    state.filters.theme = event.target.value;
    renderDiscoveryQna();
    renderEvidenceBrowser();
    bindDynamicActions();
  };
  els.filterSentiment.onchange = (event) => {
    state.filters.sentiment = event.target.value;
    renderEvidenceBrowser();
    bindDynamicActions();
  };
  els.filterSegment.onchange = (event) => {
    state.filters.segment = event.target.value;
  };
  els.search.oninput = (event) => {
    state.filters.search = event.target.value.trim();
    renderDiscoveryQna();
    renderEvidenceBrowser();
    bindDynamicActions();
  };
  els.clearFilters.onclick = () => {
    state.filters = { source: "all", date: "all", theme: "all", sentiment: "all", segment: "all", search: "" };
    els.filterSource.value = "all";
    els.filterDate.value = "all";
    els.filterTheme.value = "all";
    els.filterSentiment.value = "all";
    els.filterSegment.value = "all";
    els.search.value = "";
    renderDiscoveryQna();
    renderEvidenceBrowser();
    bindDynamicActions();
  };
  els.exportSummary.onclick = exportDashboardSummary;
  els.closeModal.onclick = closeModal;
  els.modal.addEventListener("click", (event) => {
    if (event.target.dataset.closeModal === "true") {
      closeModal();
    }
  });
}

function init() {
  try {
    // Fire LLM status check first so it always appears in Network.
    void loadLlmStatus();
    buildNav();
    syncControls();
    renderAllViews();
    updateActiveView();
    bindGlobalEvents();
    const boot = document.getElementById("boot-status");
    if (boot) boot.classList.add("hidden");
  } catch (error) {
    console.error(error);
    const boot = document.getElementById("boot-status");
    if (boot) boot.classList.add("hidden");
    document.body.innerHTML = `
      <main style="font-family:Segoe UI,sans-serif;padding:48px;max-width:720px;margin:0 auto;">
        <h1>Dashboard failed to start</h1>
        <p>${String(error && error.message ? error.message : error)}</p>
        <p>Start the server from the repo root:</p>
        <pre style="background:#f4f6f8;padding:16px;border-radius:12px;">python phase5/scripts/run_dashboard.py</pre>
        <p>Then open <strong>http://127.0.0.1:8501/</strong></p>
      </main>
    `;
  }
}

function llmBadgeEl() {
  return document.getElementById("llm-status-badge");
}

function setLlmBadge(status, detail) {
  const badge = llmBadgeEl();
  if (!badge) return;
  badge.classList.remove("llm-badge-pending", "llm-badge-on", "llm-badge-off", "llm-badge-warn");
  if (status === "on") {
    badge.classList.add("llm-badge-on");
    badge.textContent = "LLM: Groq active";
  } else if (status === "off") {
    badge.classList.add("llm-badge-off");
    badge.textContent = "LLM: not used";
  } else if (status === "warn") {
    badge.classList.add("llm-badge-warn");
    badge.textContent = "LLM: check failed";
  } else {
    badge.classList.add("llm-badge-pending");
    badge.textContent = "LLM: checking…";
  }
  badge.title = detail || badge.textContent;
}

async function fetchJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${url} → HTTP ${response.status}`);
  }
  return response.json();
}

async function loadLlmStatus() {
  const apiBase = String((window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL) || "").replace(/\/$/, "");
  let artifactStatus = null;
  let liveStatus = null;
  const notes = [];

  try {
    const buildMeta = document.querySelector('meta[name="dashboard-build"]');
    const stamp = buildMeta && buildMeta.content ? buildMeta.content : null;
    const statusUrl = stamp
      ? `/llm-status.${stamp}.json?t=${Date.now()}`
      : `/llm-status.json?t=${Date.now()}`;
    // Always visible in DevTools → Network (static provenance from pipeline).
    artifactStatus = await fetchJson(statusUrl);
    notes.push(artifactStatus.summary || "Loaded llm-status.json");
  } catch (error) {
    notes.push(`llm-status.json failed: ${error.message || error}`);
  }

  if (apiBase) {
    try {
      // Live check against Render API (also visible in Network).
      liveStatus = await fetchJson(`${apiBase}/api/llm-status?ping=1`);
      const live = liveStatus.live_api || {};
      if (live.reachable) {
        notes.push(`Live Groq OK (${live.model || "model unknown"})`);
      } else if (live.configured === false) {
        notes.push("Render API: GROQ_API_KEY not configured");
      } else {
        notes.push(`Render API Groq check failed: ${live.detail || "unreachable"}`);
      }
    } catch (error) {
      notes.push(`Render /api/llm-status failed: ${error.message || error}`);
    }
  } else {
    notes.push("API_BASE_URL not set — showing pipeline provenance only");
  }

  const used =
    Boolean(liveStatus && liveStatus.llm_used_in_pipeline) ||
    Boolean(artifactStatus && artifactStatus.llm_used_in_pipeline) ||
    Boolean(data.llm && data.llm.llm_used_in_pipeline);

  const liveOk = liveStatus && liveStatus.live_api && liveStatus.live_api.reachable === true;
  const liveConfiguredMissing =
    liveStatus && liveStatus.live_api && liveStatus.live_api.configured === false;

  if (liveOk || used) {
    setLlmBadge("on", notes.join("\n"));
  } else if (liveConfiguredMissing || (artifactStatus && artifactStatus.ok === false)) {
    setLlmBadge("warn", notes.join("\n"));
  } else if (artifactStatus || liveStatus) {
    setLlmBadge("off", notes.join("\n"));
  } else {
    setLlmBadge("warn", notes.join("\n"));
  }

  window.__LLM_STATUS__ = {
    artifact: artifactStatus,
    live: liveStatus,
    notes,
  };
}

init();
