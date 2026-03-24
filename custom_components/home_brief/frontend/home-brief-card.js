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
    if (attrs.washer_done || attrs.dryer_done) return 'accent';
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
      const tone = (attrs.solar_surplus || 0) ? 'good' : 'neutral';
      chips.push(this._formatChip('Solar', `${this._formatNumber(attrs.solar_power)} W`, tone));
    }
    if (attrs.home_power !== undefined && attrs.home_power !== null) {
      chips.push(this._formatChip('Home', `${this._formatNumber(attrs.home_power)} W`));
    }
    if (attrs.indoor_temperature !== undefined && attrs.indoor_temperature !== null) {
      chips.push(this._formatChip('Inside', `${this._formatNumber(attrs.indoor_temperature, 1)}°C`));
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
    if ((attrs.missing_entity_count ?? 0) > 0) {
      pills.push(`<span class="pill pill-warning">${attrs.missing_entity_count} source ${attrs.missing_entity_count === 1 ? 'entity' : 'entities'} missing</span>`);
    }

    return pills;
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
    const extraInsights = insights.slice(1, maxItems);

    root.innerHTML = `
      <div class="content tone-${tone}">
        <div class="topline">
          <div>
            <div class="eyebrow">Home Brief</div>
            <div class="summary">${this._escapeHtml(primaryInsight)}</div>
          </div>
          <div class="count-block">
            <div class="count-value">${insights.length}</div>
            <div class="count-label">active</div>
          </div>
        </div>

        ${this._config.show_secondary && pills.length ? `<div class="pills">${pills.join('')}</div>` : ''}
        ${this._config.show_chips && chips.length ? `<div class="chips">${chips.join('')}</div>` : ''}

        <div class="grid ${chores.length ? 'with-chores' : ''}">
          ${extraInsights.length ? `
            <section class="panel">
              <div class="section-title">Signals</div>
              <ul class="insights dense">
                ${extraInsights.map((item) => `<li class="insight">${this._escapeHtml(item)}</li>`).join('')}
              </ul>
            </section>
          ` : ''}

          ${chores.length ? `
            <section class="panel">
              <div class="section-title">Household chores</div>
              <ul class="insights chores">
                ${chores.slice(0, 3).map((item, index) => `<li class="insight chore-item ${index === 0 ? 'primary' : ''}">${this._escapeHtml(item)}</li>`).join('')}
              </ul>
            </section>
          ` : ''}
        </div>
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
        border-radius: 22px;
        transition: transform 120ms ease, box-shadow 120ms ease;
      }
      ha-card:hover {
        transform: translateY(-1px);
        box-shadow: var(--ha-card-box-shadow, 0 2px 8px rgba(0,0,0,0.12));
      }
      .content {
        padding: 18px;
        background:
          radial-gradient(circle at top right, rgba(255,255,255,0.08), transparent 30%),
          linear-gradient(180deg, rgba(255,255,255,0.02), transparent 35%);
      }
      .tone-warning { border-top: 3px solid var(--warning-color); }
      .tone-good { border-top: 3px solid var(--success-color); }
      .tone-accent { border-top: 3px solid var(--primary-color); }
      .tone-neutral { border-top: 3px solid var(--divider-color); }
      .missing { color: var(--error-color); padding: 18px; }
      .topline {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 16px;
        align-items: start;
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
        min-width: 72px;
        border-radius: 16px;
        padding: 10px 12px;
        background: color-mix(in srgb, var(--secondary-background-color) 92%, transparent);
        text-align: center;
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
      .grid.with-chores {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
      .panel {
        padding: 12px;
        border-radius: 16px;
        background: color-mix(in srgb, var(--secondary-background-color) 92%, transparent);
      }
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
        border-radius: 12px;
        background: var(--card-background-color);
        line-height: 1.4;
      }
      .dense .insight {
        padding: 9px 11px;
        font-size: 13px;
      }
      .chore-item.primary {
        background: color-mix(in srgb, var(--primary-color) 12%, var(--card-background-color));
      }
      @media (max-width: 600px) {
        .grid.with-chores {
          grid-template-columns: 1fr;
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
