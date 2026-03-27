class HomeBriefCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) throw new Error("You need to define an entity");
    this._config = {
      max_items: 6,
      show_chips: true,
      show_secondary: true,
      ...config,
    };
  }

  connectedCallback() {
    this.addEventListener('click', this._handleClick);
    this.style.cursor = 'pointer';
  }

  disconnectedCallback() {
    this.removeEventListener('click', this._handleClick);
  }

  _handleClick = () => {
    if (!this._config?.entity) return;
    this.dispatchEvent(new CustomEvent('hass-more-info', {
      bubbles: true,
      composed: true,
      detail: { entityId: this._config.entity },
    }));
  };

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  _formatNumber(value, digits = 0) {
    const num = Number(value);
    return Number.isFinite(num) ? num.toFixed(digits) : '—';
  }

  _escapeHtml(value) {
    return String(value ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  _tone(attrs) {
    if ((attrs.missing_entity_count || 0) > 0) return 'warning';
    if ((attrs.power_price ?? 0) >= 3) return 'warning';
    if ((attrs.waste_pickup_count ?? 0) > 0 || attrs.washer_done || attrs.dryer_done) return 'accent';
    if ((attrs.solar_power ?? 0) > (attrs.home_power ?? Infinity) && (attrs.solar_power ?? 0) > 0) return 'good';
    return 'neutral';
  }

  _metricTiles(attrs) {
    const tiles = [];

    if (attrs.power_price !== undefined && attrs.power_price !== null) {
      const tone = (attrs.power_price ?? 0) >= 3 ? 'warning' : ((attrs.power_price ?? 99) <= 1 ? 'good' : 'neutral');
      tiles.push({ label: 'Price', value: this._formatNumber(attrs.power_price, 2), unit: '', tone });
    }
    if (attrs.solar_power !== undefined && attrs.solar_power !== null) {
      tiles.push({ label: 'Solar', value: this._formatNumber(attrs.solar_power), unit: 'W', tone: attrs.solar_surplus ? 'good' : 'neutral' });
    }
    if (attrs.home_power_meaningful && attrs.home_power !== undefined && attrs.home_power !== null) {
      tiles.push({ label: 'Home', value: this._formatNumber(attrs.home_power), unit: 'W', tone: 'neutral' });
    }
    if (attrs.indoor_temperature !== undefined && attrs.indoor_temperature !== null) {
      tiles.push({ label: 'Inside', value: this._formatNumber(attrs.indoor_temperature, 1), unit: '°C', tone: 'neutral' });
    }
    if (attrs.weather_temperature !== undefined && attrs.weather_temperature !== null) {
      tiles.push({ label: 'Outside', value: this._formatNumber(attrs.weather_temperature, 1), unit: '°C', tone: 'neutral' });
    }
    if (attrs.humidity !== undefined && attrs.humidity !== null) {
      tiles.push({ label: 'Humidity', value: this._formatNumber(attrs.humidity), unit: '%', tone: (attrs.humidity ?? 0) >= 70 ? 'warning' : 'neutral' });
    }

    return tiles;
  }

  _statusItems(attrs) {
    const items = [];

    if ((attrs.washer_done_minutes ?? -1) >= 0 && attrs.washer_done) {
      items.push({ label: 'Laundry', text: `Washer done ${attrs.washer_done_minutes} min ago`, tone: 'neutral' });
    }
    if ((attrs.dryer_done_minutes ?? -1) >= 0 && attrs.dryer_done) {
      items.push({ label: 'Laundry', text: `Dryer done ${attrs.dryer_done_minutes} min ago`, tone: 'neutral' });
    }
    if ((attrs.lights_on ?? 0) > 0 && attrs.occupancy_home === false) {
      items.push({ label: 'Lights', text: `${attrs.lights_on} light${attrs.lights_on === 1 ? '' : 's'} still on`, tone: 'warning' });
    }
    if ((attrs.household_chores_count ?? 0) > 0) {
      items.push({ label: 'Chores', text: `${attrs.household_chores_count} task${attrs.household_chores_count === 1 ? '' : 's'} queued`, tone: 'accent' });
    }
    if ((attrs.waste_pickup_count ?? 0) > 0) {
      items.push({ label: 'Waste', text: `${attrs.waste_pickup_count} pickup${attrs.waste_pickup_count === 1 ? '' : 's'} soon`, tone: 'accent' });
    }
    if ((attrs.source_autofilled_count ?? 0) > 0) {
      items.push({ label: 'Setup', text: `${attrs.source_autofilled_count} auto-filled source${attrs.source_autofilled_count === 1 ? '' : 's'}`, tone: 'subtle' });
    }
    if ((attrs.missing_entity_count ?? 0) > 0) {
      items.push({ label: 'Setup', text: `${attrs.missing_entity_count} source ${attrs.missing_entity_count === 1 ? 'entity' : 'entities'} missing`, tone: 'warning' });
    }

    return items;
  }

  _wasteTimeline(attrs) {
    const pickups = Array.isArray(attrs.waste_pickups) ? attrs.waste_pickups : [];
    if (!pickups.length) return '';

    return `
      <section class="subpanel">
        <div class="subpanel-header">
          <div>
            <div class="subpanel-title">Waste & recycling</div>
            <div class="subpanel-subtitle">What needs attention next</div>
          </div>
        </div>
        <div class="agenda-list">
          ${pickups.slice(0, 4).map((item) => {
            const days = Number(item.days);
            const when = days <= 0 ? 'Today' : (days === 1 ? 'Tomorrow' : `In ${days} days`);
            const tone = days <= 0 ? 'warning' : (days === 1 ? 'accent' : 'neutral');
            return `
              <div class="agenda-row">
                <div class="agenda-copy">
                  <div class="agenda-label">${this._escapeHtml(item.name)}</div>
                  <div class="agenda-subtle">Collection ${this._escapeHtml(when.toLowerCase())}</div>
                </div>
                <span class="agenda-badge agenda-badge-${tone}">${this._escapeHtml(when)}</span>
              </div>
            `;
          }).join('')}
        </div>
      </section>
    `;
  }

  _normalizeChore(item) {
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      const fallback = String(item ?? '').trim();
      return fallback ? { title: fallback, date: null, assignee_names: [] } : null;
    }

    const title = String(item.title ?? '').trim();
    if (!title) return null;
    const date = item.date ? String(item.date).trim() : null;
    const assignee_names = Array.isArray(item.assignee_names)
      ? item.assignee_names.map((name) => String(name).trim()).filter(Boolean)
      : [];

    return { title, date, assignee_names };
  }

  _chorePanel(attrs) {
    const chores = (Array.isArray(attrs.household_chores) ? attrs.household_chores : [])
      .map((item) => this._normalizeChore(item))
      .filter(Boolean);
    if (!chores.length) return '';

    return `
      <section class="subpanel">
        <div class="subpanel-header">
          <div>
            <div class="subpanel-title">Household focus</div>
            <div class="subpanel-subtitle">The next few tasks worth doing</div>
          </div>
        </div>
        <div class="agenda-list">
          ${chores.slice(0, 4).map((item, index) => {
            const meta = [item.date, item.assignee_names.length ? item.assignee_names.join(', ') : null].filter(Boolean);
            return `
              <div class="agenda-row ${index === 0 ? 'agenda-row-primary' : ''}">
                <div class="agenda-copy">
                  <div class="agenda-label">${this._escapeHtml(item.title)}</div>
                  ${meta.length ? `<div class="agenda-subtle">${this._escapeHtml(meta.join(' • '))}</div>` : ''}
                </div>
                <span class="agenda-badge ${index === 0 ? 'agenda-badge-accent' : 'agenda-badge-neutral'}">${index === 0 ? 'Next' : `${index + 1}`}</span>
              </div>
            `;
          }).join('')}
        </div>
      </section>
    `;
  }

  _sourcePanel(attrs) {
    const sources = Array.isArray(attrs.source_summary) ? attrs.source_summary : [];
    if (!sources.length) return '';

    return `
      <section class="panel panel-sources">
        <div class="panel-header compact">
          <div>
            <div class="section-kicker">Configuration</div>
            <div class="section-title">Sources</div>
          </div>
          <div class="sources-meta">
            <span>${attrs.source_explicit_count ?? 0} explicit</span>
            <span>${attrs.source_autofilled_count ?? 0} auto-filled</span>
          </div>
        </div>
        <ul class="source-list">
          ${sources.slice(0, 6).map((item) => `<li>${this._escapeHtml(item)}</li>`).join('')}
        </ul>
      </section>
    `;
  }

  render() {
    const entityId = this._config.entity;
    const stateObj = this._hass?.states?.[entityId];

    if (!this.innerHTML) {
      this.innerHTML = `<ha-card><div class="wrap"></div></ha-card>`;
    }

    const root = this.querySelector('.wrap');

    if (!stateObj) {
      root.innerHTML = `<div class="content missing">Entity not found: ${entityId}</div>`;
      this._applyStyles();
      return;
    }

    const attrs = stateObj.attributes || {};
    const insights = Array.isArray(attrs.insights) ? attrs.insights : [];
    const chores = Array.isArray(attrs.household_chores) ? attrs.household_chores : [];
    const tone = this._tone(attrs);
    const metrics = this._metricTiles(attrs);
    const statusItems = this._statusItems(attrs);
    const maxItems = this._config.max_items || 6;
    const primaryInsight = insights[0] || stateObj.state;
    const filteredInsights = insights.filter((item, index) => {
      if (index === 0) return false;
      if (attrs.household_chores_summary && item === attrs.household_chores_summary) return false;
      if (attrs.waste_pickup_summary && item === attrs.waste_pickup_summary) return false;
      return true;
    }).slice(0, maxItems - 1);

    const agendaCount = (chores.length ? 1 : 0) + ((attrs.waste_pickup_count ?? 0) > 0 ? 1 : 0);

    root.innerHTML = `
      <div class="content tone-${tone}">
        <div class="hero-shell">
          <div class="hero-copy">
            <div class="eyebrow-row">
              <div class="eyebrow">Home Brief</div>
              <div class="live-dot tone-${tone}"></div>
            </div>
            <div class="summary">${this._escapeHtml(primaryInsight)}</div>
          </div>
          <div class="hero-aside">
            <div class="scorecard">
              <div class="scorecard-value">${insights.length}</div>
              <div class="scorecard-label">Active signals</div>
            </div>
            ${agendaCount ? `
              <div class="scorecard scorecard-soft">
                <div class="scorecard-value">${agendaCount}</div>
                <div class="scorecard-label">Agenda sections</div>
              </div>
            ` : ''}
          </div>
        </div>

        ${this._config.show_chips && metrics.length ? `
          <section class="metrics-strip" aria-label="Key metrics">
            ${metrics.map((item) => `
              <div class="metric-tile tone-${item.tone}">
                <div class="metric-label">${this._escapeHtml(item.label)}</div>
                <div class="metric-value">${this._escapeHtml(item.value)}${item.unit ? `<span class="metric-unit">${this._escapeHtml(item.unit)}</span>` : ''}</div>
              </div>
            `).join('')}
          </section>
        ` : ''}

        ${this._config.show_secondary && statusItems.length ? `
          <section class="panel panel-status">
            <div class="panel-header compact">
              <div>
                <div class="section-kicker">At a glance</div>
                <div class="section-title">What needs attention</div>
              </div>
            </div>
            <div class="status-list">
              ${statusItems.map((item) => `
                <div class="status-item status-${item.tone}">
                  <span class="status-label">${this._escapeHtml(item.label)}</span>
                  <span class="status-text">${this._escapeHtml(item.text)}</span>
                </div>
              `).join('')}
            </div>
          </section>
        ` : ''}

        <div class="grid ${agendaCount ? 'with-agenda' : ''}">
          ${agendaCount ? `
            <section class="panel panel-agenda-stack">
              <div class="panel-header">
                <div>
                  <div class="section-kicker">Upcoming</div>
                  <div class="section-title">Agenda</div>
                </div>
              </div>
              <div class="agenda-stack">
                ${this._wasteTimeline(attrs)}
                ${this._chorePanel(attrs)}
              </div>
            </section>
          ` : ''}

          ${filteredInsights.length ? `
            <section class="panel panel-signals">
              <div class="panel-header">
                <div>
                  <div class="section-kicker">House state</div>
                  <div class="section-title">Signals</div>
                </div>
              </div>
              <ul class="insights">
                ${filteredInsights.map((item, index) => `
                  <li class="insight">
                    <span class="insight-index">${index + 1}</span>
                    <span class="insight-text">${this._escapeHtml(item)}</span>
                  </li>
                `).join('')}
              </ul>
            </section>
          ` : ''}
        </div>

        ${this._sourcePanel(attrs)}
      </div>
    `;

    this._applyStyles();
  }

  _applyStyles() {
    if (this.querySelector('style')) return;
    const style = document.createElement('style');
    style.textContent = `
      :host {
        display: block;
        color: var(--primary-text-color);
      }
      ha-card {
        overflow: hidden;
        border-radius: 26px;
        border: 1px solid color-mix(in srgb, var(--divider-color) 60%, transparent);
        background: var(--ha-card-background, var(--card-background-color));
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
        transition: transform 140ms ease, box-shadow 140ms ease, border-color 140ms ease;
      }
      ha-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 16px 36px rgba(15, 23, 42, 0.12);
        border-color: color-mix(in srgb, var(--primary-color) 18%, var(--divider-color));
      }
      .content {
        padding: 18px;
        background:
          radial-gradient(circle at top right, color-mix(in srgb, var(--primary-color) 10%, transparent), transparent 32%),
          linear-gradient(180deg, color-mix(in srgb, var(--primary-color) 3%, transparent), transparent 42%);
      }
      .tone-warning {
        box-shadow: inset 0 3px 0 var(--warning-color);
      }
      .tone-good {
        box-shadow: inset 0 3px 0 var(--success-color);
      }
      .tone-accent {
        box-shadow: inset 0 3px 0 var(--primary-color);
      }
      .tone-neutral {
        box-shadow: inset 0 3px 0 color-mix(in srgb, var(--divider-color) 92%, transparent);
      }
      .missing {
        color: var(--error-color);
        padding: 18px;
      }
      .hero-shell {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 16px;
        align-items: start;
      }
      .hero-copy {
        min-width: 0;
      }
      .eyebrow-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 10px;
      }
      .eyebrow {
        color: var(--secondary-text-color);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 700;
      }
      .live-dot {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: color-mix(in srgb, var(--divider-color) 85%, transparent);
        box-shadow: 0 0 0 4px color-mix(in srgb, var(--divider-color) 18%, transparent);
      }
      .live-dot.tone-warning {
        background: var(--warning-color);
        box-shadow: 0 0 0 4px color-mix(in srgb, var(--warning-color) 18%, transparent);
      }
      .live-dot.tone-good {
        background: var(--success-color);
        box-shadow: 0 0 0 4px color-mix(in srgb, var(--success-color) 18%, transparent);
      }
      .live-dot.tone-accent {
        background: var(--primary-color);
        box-shadow: 0 0 0 4px color-mix(in srgb, var(--primary-color) 18%, transparent);
      }
      .summary {
        font-size: 28px;
        line-height: 1.22;
        font-weight: 680;
        letter-spacing: -0.02em;
        text-wrap: balance;
      }
      .hero-aside {
        display: grid;
        gap: 10px;
        min-width: 120px;
      }
      .scorecard {
        padding: 12px 14px;
        border-radius: 18px;
        background: color-mix(in srgb, var(--secondary-background-color) 88%, transparent);
        border: 1px solid color-mix(in srgb, var(--divider-color) 55%, transparent);
      }
      .scorecard-soft {
        background: color-mix(in srgb, var(--primary-color) 8%, var(--card-background-color));
      }
      .scorecard-value {
        font-size: 24px;
        line-height: 1;
        font-weight: 730;
        letter-spacing: -0.03em;
      }
      .scorecard-label {
        margin-top: 6px;
        color: var(--secondary-text-color);
        font-size: 11px;
        line-height: 1.35;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }
      .metrics-strip {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
        gap: 10px;
        margin-top: 16px;
      }
      .metric-tile {
        padding: 12px 12px 13px;
        border-radius: 18px;
        background: color-mix(in srgb, var(--secondary-background-color) 80%, transparent);
        border: 1px solid color-mix(in srgb, var(--divider-color) 55%, transparent);
      }
      .metric-tile.tone-warning {
        background: color-mix(in srgb, var(--warning-color) 11%, var(--card-background-color));
        border-color: color-mix(in srgb, var(--warning-color) 22%, transparent);
      }
      .metric-tile.tone-good {
        background: color-mix(in srgb, var(--success-color) 11%, var(--card-background-color));
        border-color: color-mix(in srgb, var(--success-color) 22%, transparent);
      }
      .metric-label {
        color: var(--secondary-text-color);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
      }
      .metric-value {
        margin-top: 8px;
        font-size: 24px;
        line-height: 1;
        font-weight: 700;
        letter-spacing: -0.03em;
      }
      .metric-unit {
        margin-left: 4px;
        font-size: 13px;
        color: var(--secondary-text-color);
        font-weight: 600;
        letter-spacing: 0;
      }
      .grid {
        display: grid;
        gap: 12px;
        margin-top: 14px;
      }
      .grid.with-agenda {
        grid-template-columns: minmax(0, 1.08fr) minmax(0, 0.92fr);
      }
      .panel {
        padding: 14px;
        border-radius: 22px;
        background: color-mix(in srgb, var(--secondary-background-color) 74%, transparent);
        border: 1px solid color-mix(in srgb, var(--divider-color) 55%, transparent);
      }
      .panel-header {
        display: flex;
        align-items: start;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 12px;
      }
      .panel-header.compact {
        margin-bottom: 10px;
      }
      .section-kicker {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--secondary-text-color);
        font-weight: 700;
      }
      .section-title {
        margin-top: 4px;
        font-size: 18px;
        line-height: 1.2;
        font-weight: 680;
        letter-spacing: -0.01em;
      }
      .panel-status {
        margin-top: 14px;
      }
      .status-list {
        display: grid;
        gap: 8px;
      }
      .status-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 12px;
        border-radius: 16px;
        background: var(--card-background-color);
        border: 1px solid color-mix(in srgb, var(--divider-color) 48%, transparent);
        line-height: 1.35;
      }
      .status-label {
        flex: 0 0 auto;
        min-width: 54px;
        color: var(--secondary-text-color);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
      }
      .status-text {
        min-width: 0;
        font-size: 13px;
        font-weight: 560;
      }
      .status-warning {
        background: color-mix(in srgb, var(--warning-color) 9%, var(--card-background-color));
        border-color: color-mix(in srgb, var(--warning-color) 18%, transparent);
      }
      .status-accent {
        background: color-mix(in srgb, var(--primary-color) 8%, var(--card-background-color));
        border-color: color-mix(in srgb, var(--primary-color) 16%, transparent);
      }
      .status-subtle .status-text {
        color: var(--secondary-text-color);
      }
      .panel-agenda-stack,
      .panel-signals {
        min-width: 0;
      }
      .agenda-stack {
        display: grid;
        gap: 10px;
      }
      .subpanel {
        padding: 12px;
        border-radius: 18px;
        background: color-mix(in srgb, var(--card-background-color) 88%, transparent);
        border: 1px solid color-mix(in srgb, var(--divider-color) 46%, transparent);
      }
      .subpanel-header {
        margin-bottom: 10px;
      }
      .subpanel-title {
        font-size: 15px;
        line-height: 1.25;
        font-weight: 650;
      }
      .subpanel-subtitle {
        margin-top: 3px;
        color: var(--secondary-text-color);
        font-size: 12px;
        line-height: 1.4;
      }
      .agenda-list {
        display: grid;
        gap: 8px;
      }
      .agenda-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 11px 12px;
        border-radius: 16px;
        background: color-mix(in srgb, var(--secondary-background-color) 52%, transparent);
        border: 1px solid color-mix(in srgb, var(--divider-color) 38%, transparent);
      }
      .agenda-row-primary {
        background: color-mix(in srgb, var(--primary-color) 9%, var(--card-background-color));
        border-color: color-mix(in srgb, var(--primary-color) 18%, transparent);
      }
      .agenda-copy {
        min-width: 0;
      }
      .agenda-label {
        font-weight: 620;
        line-height: 1.35;
      }
      .agenda-subtle {
        margin-top: 3px;
        color: var(--secondary-text-color);
        font-size: 12px;
        line-height: 1.35;
      }
      .agenda-badge {
        flex: 0 0 auto;
        white-space: nowrap;
        border-radius: 999px;
        padding: 6px 10px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
      }
      .agenda-badge-neutral {
        background: color-mix(in srgb, var(--secondary-background-color) 80%, transparent);
      }
      .agenda-badge-warning {
        background: color-mix(in srgb, var(--warning-color) 15%, var(--card-background-color));
      }
      .agenda-badge-accent {
        background: color-mix(in srgb, var(--primary-color) 13%, var(--card-background-color));
      }
      .insights {
        margin: 0;
        padding: 0;
        list-style: none;
        display: grid;
        gap: 8px;
      }
      .insight {
        display: grid;
        grid-template-columns: auto minmax(0, 1fr);
        gap: 10px;
        align-items: start;
        padding: 12px;
        border-radius: 16px;
        background: var(--card-background-color);
        border: 1px solid color-mix(in srgb, var(--divider-color) 46%, transparent);
      }
      .insight-index {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        border-radius: 999px;
        background: color-mix(in srgb, var(--primary-color) 10%, var(--card-background-color));
        color: var(--secondary-text-color);
        font-size: 11px;
        font-weight: 700;
      }
      .insight-text {
        line-height: 1.45;
        font-size: 13px;
      }
      .panel-sources {
        margin-top: 12px;
      }
      .sources-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 8px 16px;
        color: var(--secondary-text-color);
        font-size: 12px;
      }
      .source-list {
        margin: 0;
        padding-left: 18px;
        color: var(--secondary-text-color);
        display: grid;
        gap: 5px;
        font-size: 12px;
      }
      @media (max-width: 760px) {
        .grid.with-agenda {
          grid-template-columns: 1fr;
        }
      }
      @media (max-width: 600px) {
        .content {
          padding: 16px;
        }
        .hero-shell {
          grid-template-columns: 1fr;
        }
        .hero-aside {
          grid-template-columns: repeat(2, minmax(0, 1fr));
          min-width: 0;
        }
        .summary {
          font-size: 24px;
        }
        .metrics-strip {
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .status-item,
        .agenda-row {
          align-items: start;
        }
      }
    `;
    this.appendChild(style);
  }

  getCardSize() {
    return 5;
  }

  static getStubConfig() {
    return { entity: 'sensor.home_brief_summary', max_items: 6, show_chips: true, show_secondary: true };
  }
}

if (!customElements.get('home-brief-card')) {
  customElements.define('home-brief-card', HomeBriefCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card?.type === 'home-brief-card')) {
  window.customCards.push({
    type: 'home-brief-card',
    name: 'Home Brief Card',
    description: 'Shows a human-readable brief for your home.',
    preview: true,
  });
}
