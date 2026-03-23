class HomeBriefCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) throw new Error("You need to define an entity");
    this._config = {
      max_items: 5,
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

  _formatChip(label, value) {
    return `<span class="chip"><span class="chip-label">${label}</span><span class="chip-value">${value}</span></span>`;
  }

  _formatNumber(value, digits = 0) {
    const num = Number(value);
    return Number.isFinite(num) ? num.toFixed(digits) : '—';
  }

  _tone(attrs) {
    if ((attrs.missing_entity_count || 0) > 0) return 'warning';
    if ((attrs.power_price ?? 0) >= 3) return 'warning';
    if (attrs.washer_done || attrs.dryer_done) return 'accent';
    if ((attrs.solar_power ?? 0) > (attrs.home_power ?? Infinity) && (attrs.solar_power ?? 0) > 0) return 'good';
    return 'neutral';
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
    const tone = this._tone(attrs);
    const chips = [];

    if (attrs.power_price !== undefined && attrs.power_price !== null) {
      chips.push(this._formatChip('Price', this._formatNumber(attrs.power_price, 2)));
    }
    if (attrs.solar_power !== undefined && attrs.solar_power !== null) {
      chips.push(this._formatChip('Solar', `${this._formatNumber(attrs.solar_power)} W`));
    }
    if (attrs.home_power !== undefined && attrs.home_power !== null) {
      chips.push(this._formatChip('Home', `${this._formatNumber(attrs.home_power)} W`));
    }
    if (attrs.humidity !== undefined && attrs.humidity !== null) {
      chips.push(this._formatChip('Humidity', `${this._formatNumber(attrs.humidity)}%`));
    }

    const secondary = [];
    if ((attrs.washer_done_minutes ?? -1) >= 0 && attrs.washer_done) {
      secondary.push(`Washer done ${attrs.washer_done_minutes} min ago`);
    }
    if ((attrs.dryer_done_minutes ?? -1) >= 0 && attrs.dryer_done) {
      secondary.push(`Dryer done ${attrs.dryer_done_minutes} min ago`);
    }
    if ((attrs.lights_on ?? 0) > 0 && attrs.occupancy_home === false) {
      secondary.push(`${attrs.lights_on} light${attrs.lights_on === 1 ? '' : 's'} still on`);
    }
    if ((attrs.missing_entity_count ?? 0) > 0) {
      secondary.push(`${attrs.missing_entity_count} source ${attrs.missing_entity_count === 1 ? 'entity is' : 'entities are'} missing`);
    }

    root.innerHTML = `
      <div class="content tone-${tone}">
        <div class="topline">
          <div class="eyebrow">Home Brief</div>
          <div class="count">${insights.length} insight${insights.length === 1 ? '' : 's'}</div>
        </div>
        <div class="summary">${stateObj.state}</div>
        ${this._config.show_secondary && secondary.length ? `<div class="secondary">${secondary.join(' · ')}</div>` : ''}
        ${this._config.show_chips && chips.length ? `<div class="chips">${chips.join('')}</div>` : ''}
        ${insights.length ? `
          <div class="section-title">Right now</div>
          <ul class="insights">
            ${insights.slice(0, this._config.max_items || 5).map((item, index) => `<li class="insight ${index === 0 ? 'primary' : ''}">${item}</li>`).join('')}
          </ul>
        ` : ''}
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
        border-radius: 20px;
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
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: center;
      }
      .eyebrow, .count {
        color: var(--secondary-text-color);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }
      .summary {
        font-size: 24px;
        line-height: 1.28;
        font-weight: 650;
        margin: 10px 0 8px;
      }
      .secondary {
        color: var(--secondary-text-color);
        font-size: 13px;
        line-height: 1.4;
        margin-bottom: 12px;
      }
      .section-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--secondary-text-color);
        margin: 18px 0 10px;
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
        background: var(--secondary-background-color);
        line-height: 1.4;
      }
      .insight.primary {
        background: color-mix(in srgb, var(--primary-color) 12%, var(--card-background-color));
      }
      .chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
      }
      .chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 10px;
        border-radius: 999px;
        background: var(--secondary-background-color);
        font-size: 12px;
      }
      .chip-label {
        color: var(--secondary-text-color);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-size: 11px;
      }
      .chip-value { font-weight: 600; }
    `;
    this.appendChild(style);
  }

  getCardSize() {
    return 4;
  }

  static getStubConfig() {
    return { entity: 'sensor.home_brief_summary', max_items: 5, show_chips: true, show_secondary: true };
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
