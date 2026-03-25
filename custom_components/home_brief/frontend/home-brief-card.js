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

  _formatChip(label, value, tone = 'neutral') {
    return `<span class="chip chip-${tone}"><span class="chip-label">${label}</span><span class="chip-value">${value}</span></span>`;
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

  _metricChips(attrs) {
    const chips = [];

    if (attrs.power_price !== undefined && attrs.power_price !== null) {
      const tone = (attrs.power_price ?? 0) >= 3 ? 'warning' : ((attrs.power_price ?? 99) <= 1 ? 'good' : 'neutral');
      chips.push(this._formatChip('Price', this._formatNumber(attrs.power_price, 2), tone));
    }
    if (attrs.solar_power !== undefined && attrs.solar_power !== null) {
      const tone = attrs.solar_surplus ? 'good' : 'neutral';
      chips.push(this._formatChip('Solar', `${this._formatNumber(attrs.solar_power)} W`, tone));
    }
    if (attrs.home_power !== undefined && attrs.home_power !== null) {
      chips.push(this._formatChip('Home', `${this._formatNumber(attrs.home_power)} W`));
    }
    if (attrs.indoor_temperature !== undefined && attrs.indoor_temperature !== null) {
      chips.push(this._formatChip('Inside', `${this._formatNumber(attrs.indoor_temperature, 1)}°C`));
    }
    if (attrs.weather_temperature !== undefined && attrs.weather_temperature !== null) {
      chips.push(this._formatChip('Outside', `${this._formatNumber(attrs.weather_temperature, 1)}°C`));
    }
    if (attrs.humidity !== undefined && attrs.humidity !== null) {
      const tone = (attrs.humidity ?? 0) >= 70 ? 'warning' : 'neutral';
      chips.push(this._formatChip('Humidity', `${this._formatNumber(attrs.humidity)}%`, tone));
    }

    return chips;
  }

  _statusPills(attrs) {
    const pills = [];

    if ((attrs.washer_done_minutes ?? -1) >= 0 && attrs.washer_done) {
      pills.push(`<span class="pill">Washer ${attrs.washer_done_minutes} min ago</span>`);
    }
    if ((attrs.dryer_done_minutes ?? -1) >= 0 && attrs.dryer_done) {
      pills.push(`<span class="pill">Dryer ${attrs.dryer_done_minutes} min ago</span>`);
    }
    if ((attrs.lights_on ?? 0) > 0 && attrs.occupancy_home === false) {
      pills.push(`<span class="pill pill-warning">${attrs.lights_on} light${attrs.lights_on === 1 ? '' : 's'} still on</span>`);
    }
    if ((attrs.household_chores_count ?? 0) > 0) {
      pills.push(`<span class="pill">${attrs.household_chores_count} chore${attrs.household_chores_count === 1 ? '' : 's'} queued</span>`);
    }
    if ((attrs.waste_pickup_count ?? 0) > 0) {
      pills.push(`<span class="pill pill-accent">${attrs.waste_pickup_count} waste pickup${attrs.waste_pickup_count === 1 ? '' : 's'} soon</span>`);
    }
    if ((attrs.source_autofilled_count ?? 0) > 0) {
      pills.push(`<span class="pill">${attrs.source_autofilled_count} auto-filled source${attrs.source_autofilled_count === 1 ? '' : 's'}</span>`);
    }
    if ((attrs.missing_entity_count ?? 0) > 0) {
      pills.push(`<span class="pill pill-warning">${attrs.missing_entity_count} source ${attrs.missing_entity_count === 1 ? 'entity' : 'entities'} missing</span>`);
    }

    return pills;
  }

  _wasteTimeline(attrs) {
    const pickups = Array.isArray(attrs.waste_pickups) ? attrs.waste_pickups : [];
    if (!pickups.length) return '';

    return `
      <section class="panel panel-agenda">
        <div class="section-title">Waste & recycling</div>
        <div class="waste-list">
          ${pickups.slice(0, 4).map((item) => {
            const days = Number(item.days);
            const when = days <= 0 ? 'Today' : (days === 1 ? 'Tomorrow' : `In ${days} days`);
            const tone = days <= 0 ? 'warning' : (days === 1 ? 'accent' : 'neutral');
            return `
              <div class="agenda-row">
                <div>
                  <div class="agenda-label">${this._escapeHtml(item.name)}</div>
                  <div class="agenda-subtle">${this._escapeHtml(when)}</div>
                </div>
                <span class="agenda-badge agenda-badge-${tone}">${this._escapeHtml(when)}</span>
              </div>
            `;
          }).join('')}
        </div>
      </section>
    `;
  }

  _chorePanel(attrs) {
    const chores = Array.isArray(attrs.household_chores) ? attrs.household_chores : [];
    if (!chores.length) return '';

    return `
      <section class="panel panel-agenda">
        <div class="section-title">Household focus</div>
        <ul class="insights chores">
          ${chores.slice(0, 4).map((item, index) => `
            <li class="insight chore-item ${index === 0 ? 'primary' : ''}">
              <span class="insight-marker">${index === 0 ? 'Next' : `${index + 1}`}</span>
              <span>${this._escapeHtml(item)}</span>
            </li>
          `).join('')}
        </ul>
      </section>
    `;
  }

  _sourcePanel(attrs) {
    const sources = Array.isArray(attrs.source_summary) ? attrs.source_summary : [];
    if (!sources.length) return '';

    return `
      <section class="panel panel-sources">
        <div class="section-title">Sources</div>
        <div class="sources-meta">
          <span>${attrs.source_explicit_count ?? 0} explicit</span>
          <span>${attrs.source_autofilled_count ?? 0} auto-filled</span>
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
    const chips = this._metricChips(attrs);
    const pills = this._statusPills(attrs);
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
        <div class="hero">
          <div class="hero-copy">
            <div class="eyebrow">Home Brief</div>
            <div class="summary">${this._escapeHtml(primaryInsight)}</div>
          </div>
          <div class="hero-stats">
            <div class="count-block">
              <div class="count-value">${insights.length}</div>
              <div class="count-label">active</div>
            </div>
            ${agendaCount ? `
              <div class="count-block soft">
                <div class="count-value">${agendaCount}</div>
                <div class="count-label">agenda</div>
              </div>
            ` : ''}
          </div>
        </div>

        ${this._config.show_secondary && pills.length ? `<div class="pills">${pills.join('')}</div>` : ''}
        ${this._config.show_chips && chips.length ? `<div class="chips">${chips.join('')}</div>` : ''}

        <div class="grid ${agendaCount ? 'with-agenda' : ''}">
          ${agendaCount ? `
            <section class="panel panel-stack">
              <div class="section-title">Upcoming</div>
              <div class="agenda-stack">
                ${this._wasteTimeline(attrs)}
                ${this._chorePanel(attrs)}
              </div>
            </section>
          ` : ''}

          ${filteredInsights.length ? `
            <section class="panel panel-signals">
              <div class="section-title">Signals</div>
              <ul class="insights dense">
                ${filteredInsights.map((item) => `<li class="insight">${this._escapeHtml(item)}</li>`).join('')}
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
      :host { display: block; }
      ha-card {
        overflow: hidden;
        border-radius: 24px;
        transition: transform 120ms ease, box-shadow 120ms ease;
      }
      ha-card:hover {
        transform: translateY(-1px);
        box-shadow: var(--ha-card-box-shadow, 0 8px 26px rgba(0,0,0,0.14));
      }
      .content {
        padding: 18px;
        background:
          radial-gradient(circle at top right, rgba(255,255,255,0.09), transparent 30%),
          linear-gradient(180deg, rgba(255,255,255,0.03), transparent 35%);
      }
      .tone-warning { border-top: 3px solid var(--warning-color); }
      .tone-good { border-top: 3px solid var(--success-color); }
      .tone-accent { border-top: 3px solid var(--primary-color); }
      .tone-neutral { border-top: 3px solid var(--divider-color); }
      .missing { color: var(--error-color); padding: 18px; }
      .hero {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 16px;
        align-items: start;
      }
      .hero-stats {
        display: grid;
        gap: 10px;
      }
      .eyebrow {
        color: var(--secondary-text-color);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
      }
      .summary {
        font-size: 24px;
        line-height: 1.28;
        font-weight: 650;
      }
      .count-block {
        min-width: 74px;
        border-radius: 16px;
        padding: 10px 12px;
        background: color-mix(in srgb, var(--secondary-background-color) 92%, transparent);
        text-align: center;
      }
      .count-block.soft {
        background: color-mix(in srgb, var(--primary-color) 10%, var(--card-background-color));
      }
      .count-value {
        font-size: 22px;
        font-weight: 700;
        line-height: 1;
      }
      .count-label {
        margin-top: 4px;
        color: var(--secondary-text-color);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }
      .pills, .chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
      }
      .pill, .chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 10px;
        border-radius: 999px;
        background: var(--secondary-background-color);
        font-size: 12px;
      }
      .pill-warning, .chip-warning {
        background: color-mix(in srgb, var(--warning-color) 14%, var(--card-background-color));
      }
      .pill-accent {
        background: color-mix(in srgb, var(--primary-color) 13%, var(--card-background-color));
      }
      .chip-good {
        background: color-mix(in srgb, var(--success-color) 14%, var(--card-background-color));
      }
      .chip-label {
        color: var(--secondary-text-color);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-size: 11px;
      }
      .chip-value { font-weight: 600; }
      .grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 12px;
        margin-top: 14px;
      }
      .grid.with-agenda {
        grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
      }
      .panel {
        padding: 14px;
        border-radius: 18px;
        background: color-mix(in srgb, var(--secondary-background-color) 92%, transparent);
      }
      .panel-stack {
        display: grid;
        gap: 10px;
      }
      .agenda-stack {
        display: grid;
        gap: 10px;
      }
      .panel-agenda {
        padding: 0;
        background: transparent;
      }
      .panel-sources {
        margin-top: 12px;
      }
      .panel-signals .insights { gap: 8px; }
      .section-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--secondary-text-color);
        margin-bottom: 10px;
      }
      .insights {
        margin: 0;
        padding: 0;
        list-style: none;
        display: grid;
        gap: 8px;
      }
      .insight {
        padding: 10px 12px;
        border-radius: 14px;
        background: var(--card-background-color);
        line-height: 1.4;
      }
      .dense .insight {
        padding: 10px 12px;
        font-size: 13px;
      }
      .chore-item {
        display: grid;
        grid-template-columns: auto 1fr;
        gap: 10px;
        align-items: start;
      }
      .chore-item.primary {
        background: color-mix(in srgb, var(--primary-color) 12%, var(--card-background-color));
      }
      .insight-marker {
        display: inline-flex;
        min-width: 34px;
        justify-content: center;
        padding: 2px 8px;
        border-radius: 999px;
        background: color-mix(in srgb, var(--secondary-background-color) 82%, transparent);
        color: var(--secondary-text-color);
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }
      .waste-list {
        display: grid;
        gap: 8px;
      }
      .agenda-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 10px 12px;
        border-radius: 14px;
        background: var(--card-background-color);
      }
      .agenda-label {
        font-weight: 600;
        line-height: 1.35;
      }
      .agenda-subtle {
        margin-top: 2px;
        color: var(--secondary-text-color);
        font-size: 12px;
      }
      .agenda-badge {
        white-space: nowrap;
        border-radius: 999px;
        padding: 6px 9px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        background: var(--secondary-background-color);
      }
      .agenda-badge-warning {
        background: color-mix(in srgb, var(--warning-color) 15%, var(--card-background-color));
      }
      .agenda-badge-accent {
        background: color-mix(in srgb, var(--primary-color) 13%, var(--card-background-color));
      }
      .sources-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 8px 16px;
        color: var(--secondary-text-color);
        font-size: 12px;
        margin-bottom: 8px;
      }
      .source-list {
        margin: 0;
        padding-left: 18px;
        color: var(--secondary-text-color);
        display: grid;
        gap: 4px;
        font-size: 12px;
      }
      @media (max-width: 700px) {
        .grid.with-agenda {
          grid-template-columns: 1fr;
        }
      }
      @media (max-width: 600px) {
        .hero {
          grid-template-columns: 1fr;
        }
        .hero-stats {
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .summary {
          font-size: 22px;
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

customElements.define('home-brief-card', HomeBriefCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'home-brief-card',
  name: 'Home Brief Card',
  description: 'Shows a human-readable brief for your home.',
  preview: true,
});
