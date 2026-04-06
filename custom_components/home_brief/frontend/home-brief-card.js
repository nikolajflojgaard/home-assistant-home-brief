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
    const solar = Number(attrs.solar_power ?? 0);
    const home = Number(attrs.home_power ?? 0);
    if ((attrs.missing_entity_count || 0) > 0) return 'warning';
    if ((attrs.power_price ?? 0) >= 3) return 'warning';
    if (solar > 0 && home > 0 && solar < home) return 'danger';
    if ((attrs.waste_pickup_count ?? 0) > 0 || attrs.washer_done || attrs.dryer_done) return 'accent';
    if (solar > home && solar > 0) return 'good';
    return 'neutral';
  }

  _metricTiles(attrs) {
    const tiles = [];

    if (attrs.power_price !== undefined && attrs.power_price !== null) {
      const tone = (attrs.power_price ?? 0) >= 3 ? 'warning' : ((attrs.power_price ?? 99) <= 1 ? 'good' : 'neutral');
      tiles.push({ label: 'Price', value: this._formatNumber(attrs.power_price, 2), unit: '', tone });
    }
    if (attrs.solar_power !== undefined && attrs.solar_power !== null) {
      const solar = Number(attrs.solar_power ?? 0);
      const home = Number(attrs.home_power ?? 0);
      if (solar > 0) {
        const tone = attrs.solar_surplus ? 'good' : (home > 0 && solar < home ? 'danger' : 'neutral');
        tiles.push({ label: 'Solar', value: this._formatNumber(attrs.solar_power), unit: 'W', tone });
      }
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

  _normalizeAssigneeNames(value) {
    if (typeof value === 'string') {
      const text = value.trim();
      return text ? [text] : [];
    }
    if (Array.isArray(value)) {
      return value.flatMap((item) => this._normalizeAssigneeNames(item));
    }
    if (value && typeof value === 'object') {
      const text = String(value.name ?? value.display_name ?? value.full_name ?? value.title ?? '').trim();
      return text ? [text] : [];
    }
    return [];
  }

  _formatChoreDate(value) {
    const text = String(value ?? '').trim();
    if (!text) return null;
    const normalized = text.endsWith('Z') ? `${text.slice(0, -1)}+00:00` : text;
    const date = new Date(normalized);
    if (Number.isNaN(date.getTime())) return text;

    try {
      return new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric' }).format(date);
    } catch (_error) {
      return text;
    }
  }

  _normalizeChore(item) {
    if (!item || typeof item !== 'object' || Array.isArray(item)) {
      const fallback = String(item ?? '').trim();
      return fallback ? { title: fallback, date: null, assignee_names: [] } : null;
    }

    const title = String(item.title ?? item.name ?? item.task ?? item.summary ?? '').trim();
    if (!title) return null;
    const date = this._formatChoreDate(item.date ?? item.due ?? item.due_date ?? item.deadline);
    const assignee_names = this._normalizeAssigneeNames(item.assignee_names ?? item.assignees ?? item.assigned_to)
      .map((name) => String(name).trim())
      .filter(Boolean);

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
    if (!sources.length || !this._config?.show_debug) return '';

    return `
      <section class="debug-panel">
        <div class="debug-title-row">
          <div class="debug-title">Source mapping</div>
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

  _actionPanel(attrs) {
    const topAction = attrs.top_action && typeof attrs.top_action === 'object' ? attrs.top_action : null;
    if (!topAction) return '';

    const meta = [topAction?.time_window ? `Window: ${topAction.time_window}` : null, topAction?.why_now || null]
      .filter(Boolean)
      .join(' • ');

    return `
      <section class="action-panel compact">
        <div class="action-eyebrow">Suggested move</div>
        <div class="action-inline">${this._escapeHtml(topAction.title || 'No strong move right now')}</div>
        ${topAction.summary ? `<div class="action-summary">${this._escapeHtml(topAction.summary)}</div>` : ''}
        ${meta ? `<div class="action-why">${this._escapeHtml(meta)}</div>` : ''}
      </section>
    `;
  }

  _focusItems(attrs) {
    const items = [];
    const chores = (Array.isArray(attrs.household_chores) ? attrs.household_chores : []).slice(0, 3);

    if (chores.length) {
      chores.forEach((chore, index) => {
        const names = Array.isArray(chore.assignee_names) ? chore.assignee_names.filter(Boolean) : [];
        const date = chore.date ? String(chore.date) : null;
        const meta = [names.length ? names.join(', ') : null, date].filter(Boolean).join(' • ') || 'Household focus';
        items.push({
          title: String(chore.title || `Household task ${index + 1}`),
          meta,
          tone: index === 0 ? 'accent' : 'neutral',
        });
      });
    }

    const wastePickups = Array.isArray(attrs.waste_pickups) ? attrs.waste_pickups : [];
    const nearWaste = wastePickups.filter((item) => Number(item?.days ?? 99) <= 2);
    if (nearWaste.length) {
      const first = nearWaste[0] || {};
      const name = String(first.name || 'Affald');
      const days = Number(first.days ?? 99);
      const when = days <= 0 ? '0 dage' : `+${days} dag${days === 1 ? '' : 'e'}`;
      items.push({
        title: `Affald: ${name}`,
        meta: when,
        tone: 'warning',
      });
    } else if ((attrs.waste_pickup_count ?? 0) > 0) {
      items.push({
        title: attrs.waste_pickup_summary || `${attrs.waste_pickup_count} pickup${attrs.waste_pickup_count === 1 ? '' : 's'} coming up`,
        meta: 'Waste & recycling',
        tone: 'warning',
      });
    }

    if ((attrs.washer_done_minutes ?? -1) >= 0 && attrs.washer_done) {
      items.push({
        title: `Washer finished ${attrs.washer_done_minutes} min ago`,
        meta: 'Laundry',
        tone: 'neutral',
      });
    }

    if ((attrs.dryer_done_minutes ?? -1) >= 0 && attrs.dryer_done) {
      items.push({
        title: `Dryer finished ${attrs.dryer_done_minutes} min ago`,
        meta: 'Laundry',
        tone: 'neutral',
      });
    }

    if ((attrs.lights_on ?? 0) > 0 && attrs.occupancy_home === false) {
      items.push({
        title: `${attrs.lights_on} light${attrs.lights_on === 1 ? '' : 's'} still on`,
        meta: 'Away mode',
        tone: 'warning',
      });
    }

    if ((attrs.missing_entity_count ?? 0) > 0) {
      items.push({
        title: `${attrs.missing_entity_count} configured source ${attrs.missing_entity_count === 1 ? 'is' : 'are'} missing`,
        meta: 'Setup',
        tone: 'warning',
      });
    }

    return items.slice(0, 4);
  }

  _signalRows(insights) {
    if (!insights.length) return '';

    return `
      <section class="signal-stack" aria-label="Supporting signals">
        <div class="focus-title">Background</div>
        ${insights.map((item) => `
          <div class="signal-row">
            <span class="signal-dot"></span>
            <span class="signal-text">${this._escapeHtml(item)}</span>
          </div>
        `).join('')}
      </section>
    `;
  }

  _slotPanel(attrs) {
    const pressure = Array.isArray(attrs.household_slot_pressure) ? attrs.household_slot_pressure : [];
    const slots = attrs.household_chore_slots && typeof attrs.household_chore_slots === 'object' ? attrs.household_chore_slots : {};
    if (!pressure.length) return '';

    const rows = pressure.filter((row) => Number(row.task_count || 0) > 0);
    if (!rows.length) return '';

    return `
      <section class="slot-panel">
        <div class="focus-title">Today by slot</div>
        ${(attrs.household_today_chores_count ?? 0) === 0 ? `<div class="focus-meta">No tasks due today</div>` : ''}
        <div class="slot-list">
          ${rows.map((row) => {
            const key = String(row.slot || '').toLowerCase();
            const items = Array.isArray(slots[key]) ? slots[key].slice(0, 3) : [];
            return `
              <div class="slot-row ${row.level === 'contention' || row.level === 'busy' ? 'slot-row-busy' : ''}">
                <div>
                  <div class="slot-name">${this._escapeHtml((row.slot || '').toUpperCase())}</div>
                  ${items.length ? `<div class="slot-task-list">${items.map((item) => this._escapeHtml([item.title || '', Array.isArray(item.assignee_names) && item.assignee_names.length ? item.assignee_names.join(', ') : ''].filter(Boolean).join(' — '))).join(' · ')}</div>` : ''}
                  ${Array.isArray(row.people) && row.people.length ? `<div class="slot-people">${this._escapeHtml(row.people.join(', '))}</div>` : ''}
                </div>
                <div class="slot-count">${this._escapeHtml(row.level || 'normal')} · ${row.task_count} task${row.task_count === 1 ? '' : 's'}</div>
              </div>
            `;
          }).join('')}
        </div>
      </section>
    `;
  }

  _parseBriefSections(briefText) {
    if (!briefText) return [];

    const names = [
      'Global',
      'Denmark / EU',
      'Markets',
      'Tech / AI',
      'Today to watch',
      'Copenhagen weather',
      'If I only do 3 things today',
    ];

    const blocks = briefText
      .split(/\n\s*\n/)
      .map((part) => part.trim())
      .filter(Boolean);

    const sections = [];
    let current = null;

    for (const block of blocks) {
      if (/^Daily brief/i.test(block)) continue;
      const matched = names.find((name) => block === name);
      if (matched) {
        current = { title: matched, body: [] };
        sections.push(current);
        continue;
      }
      if (!current) continue;
      current.body.push(block);
    }

    return sections.filter((section) => section.body.length);
  }

  _renderBriefSectionPart(part) {
    const lines = String(part || '')
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean);

    if (!lines.length) return '';

    const bulletLines = lines.filter((line) => line.startsWith('•')).slice(0, 4);
    if (bulletLines.length === lines.length || bulletLines.length >= 2) {
      return `
        <div class="brief-section-copy brief-section-copy-bullets">
          ${bulletLines.map((line) => `
            <div class="brief-bullet-row">
              <span class="brief-bullet-dot"></span>
              <span class="brief-bullet-text">${this._escapeHtml(line.replace(/^•\s*/, ''))}</span>
            </div>
          `).join('')}
        </div>
      `;
    }

    const text = lines.join(' ');
    const clipped = text.length > 420 ? `${text.slice(0, 417).trim()}…` : text;
    return `<div class="brief-section-copy">${this._escapeHtml(clipped)}</div>`;
  }

  _briefSections(attrs) {
    const pkg = attrs.daily_brief_package && typeof attrs.daily_brief_package === 'object' ? attrs.daily_brief_package : null;
    const briefText = pkg && typeof pkg.brief_text === 'string' ? pkg.brief_text.trim() : '';
    const sections = this._parseBriefSections(briefText)
      .map((section) => ({
        ...section,
        body: (Array.isArray(section.body) ? section.body : []).filter(Boolean),
      }))
      .filter((section) => section.body.length);

    if (!sections.length) {
      const fallback = String(pkg?.summary || '').trim();
      return fallback
        ? `<div class="brief-sections brief-sections-fallback"><div class="brief-section-copy">${this._escapeHtml(fallback)}</div></div>`
        : '';
    }

    return `
      <div class="brief-sections">
        ${sections.map((section, index) => `
          <div class="brief-section">
            <div class="brief-section-head">
              <div class="brief-section-badge">${index + 1}</div>
              <div class="brief-section-title">${this._escapeHtml(section.title)}</div>
            </div>
            <div class="brief-section-body">
              ${section.body.slice(0, 3).map((part) => this._renderBriefSectionPart(part)).join('')}
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  _morningBriefPanel(attrs) {
    const pkg = attrs.daily_brief_package && typeof attrs.daily_brief_package === 'object' ? attrs.daily_brief_package : null;
    const lines = Array.isArray(attrs.morning_brief_top3) ? attrs.morning_brief_top3.filter(Boolean).slice(0, 3) : [];
    const packageSummary = pkg && typeof pkg.summary === 'string' ? pkg.summary.trim() : '';
    if (!lines.length && !packageSummary) return '';

    const weatherState = String(attrs.weather_state || pkg?.weather?.state || '').trim();
    const weatherTemp = attrs.weather_temperature !== undefined && attrs.weather_temperature !== null
      ? `${this._formatNumber(attrs.weather_temperature, 1)}°C`
      : (pkg?.weather?.temperature !== undefined && pkg?.weather?.temperature !== null
        ? `${this._formatNumber(pkg.weather.temperature, 1)}°C`
        : null);
    const generatedAt = attrs.morning_brief_generated_at ? new Date(attrs.morning_brief_generated_at) : null;
    const generatedLabel = generatedAt && !Number.isNaN(generatedAt.getTime())
      ? generatedAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      : null;

    const chips = [
      weatherState ? `Weather: ${weatherState}` : null,
      weatherTemp,
      generatedLabel ? `Updated ${generatedLabel}` : null,
    ].filter(Boolean);

    const meta = attrs.morning_brief_meta ? `<div class="morning-brief-meta">${this._escapeHtml(attrs.morning_brief_meta)}</div>` : '';
    const summaryBlock = packageSummary && (!lines.length || packageSummary !== lines[0])
      ? `<div class="morning-brief-summary">${this._escapeHtml(packageSummary)}</div>`
      : '';
    const briefText = pkg && typeof pkg.brief_text === 'string' ? pkg.brief_text.trim() : '';
    const synopsisText = briefText
      ? briefText
          .split(/\n\s*\n/)
          .map((part) => part.trim())
          .filter((part) => part && !/^Daily brief/i.test(part) && !/^If I only do 3 things today/i.test(part) && !/^Nikolaj’s Tasks/i.test(part) && !/^Household Chores/i.test(part) && !/^Solar/i.test(part))
          .slice(0, 2)
          .join(' ')
          .replace(/\s+/g, ' ')
      : '';
    const synopsisBlock = synopsisText
      ? `<div class="morning-brief-synopsis">${this._escapeHtml(synopsisText)}</div>`
      : '';
    const lead = this._escapeHtml(lines[0] || packageSummary);
    const rest = lines.slice(1);
    const packageRows = [
      pkg?.solar?.yesterday_kwh !== undefined && pkg?.solar?.yesterday_kwh !== null ? {
        title: 'Solar',
        value: `Yesterday ${pkg.solar.yesterday_kwh} kWh`,
      } : null,
    ].filter(Boolean);

    return `
      <section class="morning-brief-panel">
        <div class="morning-brief-header">
          <div>
            <div class="morning-brief-eyebrow">Morning brief</div>
            ${summaryBlock}
            ${synopsisBlock}
            <div class="morning-brief-lead">${lead}</div>
            ${meta}
          </div>
          ${chips.length ? `
            <div class="morning-brief-chips">
              ${chips.map((chip) => `<span class="morning-brief-chip">${this._escapeHtml(chip)}</span>`).join('')}
            </div>
          ` : ''}
        </div>
        ${rest.length ? `
          <div class="morning-brief-list">
            ${rest.map((line, index) => `
              <div class="morning-brief-item">
                <div class="morning-brief-rank">${index + 2}</div>
                <div class="morning-brief-text">${this._escapeHtml(line)}</div>
              </div>
            `).join('')}
          </div>
        ` : ''}
        ${this._briefSections(attrs)}
        ${packageRows.length ? `
          <div class="morning-brief-package">
            ${packageRows.map((row) => `
              <div class="morning-brief-package-row">
                <div class="morning-brief-package-title">${this._escapeHtml(row.title)}</div>
                <div class="morning-brief-package-value">${this._escapeHtml(row.value)}</div>
              </div>
            `).join('')}
          </div>
        ` : ''}
      </section>
    `;
  }

  _morningCoverage(attrs) {
    const pkg = attrs.daily_brief_package && typeof attrs.daily_brief_package === 'object' ? attrs.daily_brief_package : null;
    const sectionsText = Array.isArray(pkg?.top3) ? pkg.top3 : [];
    const summaryParts = [pkg?.summary, pkg?.brief_text, ...(Array.isArray(attrs.morning_brief_top3) ? attrs.morning_brief_top3 : []), ...sectionsText]
      .map((item) => String(item || '').trim().toLowerCase())
      .filter(Boolean);
    return new Set(summaryParts);
  }

  _focusPanel(attrs) {
    const items = this._focusItems(attrs);
    if (!items.length) return '';

    const morningCoverage = this._morningCoverage(attrs);

    const filtered = items.filter((item) => {
      const title = String(item.title || '').trim().toLowerCase();
      const meta = String(item.meta || '').trim().toLowerCase();
      return title && !morningCoverage.has(title) && !morningCoverage.has(meta);
    });

    if (!filtered.length) return '';

    return `
      <section class="focus-panel">
        <div class="focus-title">Household focus</div>
        <div class="focus-list compact">
          ${filtered.map((item, index) => `
            <div class="focus-item focus-${item.tone} ${index === 0 ? 'focus-primary' : ''}">
              <div class="focus-copy">
                <div class="focus-headline">${this._escapeHtml(item.title)}</div>
                <div class="focus-meta">${this._escapeHtml(item.meta)}</div>
              </div>
            </div>
          `).join('')}
        </div>
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
    const tone = this._tone(attrs);
    const metrics = this._metricTiles(attrs).slice(0, 4);
    const maxItems = this._config.max_items || 6;
    const primaryInsight = insights[0] || stateObj.state;
    const seen = new Set();
    const actionStrings = [attrs?.top_action?.title, attrs?.top_action?.summary]
      .filter(Boolean)
      .map((item) => String(item).trim().toLowerCase());
    const morningCoverage = this._morningCoverage(attrs);
    const filteredInsights = insights.filter((item, index) => {
      const normalized = String(item || '').trim().toLowerCase();
      if (!normalized || index === 0) return false;
      if (seen.has(normalized)) return false;
      if (attrs.household_chores_summary && normalized === String(attrs.household_chores_summary).trim().toLowerCase()) return false;
      if (attrs.nikolaj_chores_summary && normalized === String(attrs.nikolaj_chores_summary).trim().toLowerCase()) return false;
      if (attrs.waste_pickup_summary && normalized === String(attrs.waste_pickup_summary).trim().toLowerCase()) return false;
      if (actionStrings.includes(normalized)) return false;
      if (morningCoverage.has(normalized)) return false;
      if (normalized.startsWith('best move now:') || normalized.startsWith('suggested move:')) return false;
      seen.add(normalized);
      return true;
    }).slice(0, Math.min(2, Math.max(0, maxItems - 2)));

    root.innerHTML = `
      <div class="content tone-${tone}">
        <div class="hero-shell minimal">
          <div class="hero-copy">
            <div class="eyebrow-row">
              <div class="eyebrow">Home Brief</div>
              <div class="live-dot tone-${tone}"></div>
            </div>
            <div class="summary">${this._escapeHtml(primaryInsight)}</div>
          </div>
        </div>

        ${this._config.show_chips && metrics.length ? `
          <section class="metrics-strip clean" aria-label="Key metrics">
            ${metrics.map((item) => `
              <div class="metric-tile tone-${item.tone}">
                <div class="metric-label">${this._escapeHtml(item.label)}</div>
                <div class="metric-value">${this._escapeHtml(item.value)}${item.unit ? `<span class="metric-unit">${this._escapeHtml(item.unit)}</span>` : ''}</div>
              </div>
            `).join('')}
          </section>
        ` : ''}

        ${this._morningBriefPanel(attrs)}

        <div class="brief-grid">
          <div class="brief-main">
            ${this._focusPanel(attrs)}
            ${this._actionPanel(attrs)}
          </div>
          <div class="brief-side">
            ${this._slotPanel(attrs)}
          </div>
        </div>

        ${filteredInsights.length && this._config.show_secondary ? this._signalRows(filteredInsights) : ''}

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
      .tone-danger {
        box-shadow: inset 0 3px 0 var(--error-color);
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
      .hero-shell.minimal {
        grid-template-columns: minmax(0, 1fr);
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
      .live-dot.tone-danger {
        background: var(--error-color);
        box-shadow: 0 0 0 4px color-mix(in srgb, var(--error-color) 18%, transparent);
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
      .metrics-strip.clean {
        margin-top: 18px;
        gap: 8px;
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
      .metric-tile.tone-danger {
        background: color-mix(in srgb, var(--error-color) 10%, var(--card-background-color));
        border-color: color-mix(in srgb, var(--error-color) 22%, transparent);
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
      .action-panel {
        margin-top: 16px;
        padding: 14px;
        border-radius: 22px;
        background: color-mix(in srgb, var(--primary-color) 8%, var(--card-background-color));
        border: 1px solid color-mix(in srgb, var(--primary-color) 18%, transparent);
      }
      .action-panel.compact {
        padding: 12px 14px;
        border-radius: 18px;
      }
      .action-panel-header {
        display: flex;
        align-items: start;
        justify-content: space-between;
        gap: 12px;
      }
      .action-eyebrow {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--secondary-text-color);
        font-weight: 700;
        margin-bottom: 6px;
      }
      .action-title {
        font-size: 20px;
        line-height: 1.2;
        font-weight: 700;
        letter-spacing: -0.02em;
      }
      .action-inline {
        font-size: 15px;
        line-height: 1.35;
        font-weight: 700;
      }
      .action-summary {
        margin-top: 6px;
        font-size: 13px;
        line-height: 1.45;
        color: var(--secondary-text-color);
      }
      .action-why {
        margin-top: 8px;
        font-size: 12px;
        line-height: 1.45;
        color: var(--secondary-text-color);
      }
      .action-score {
        flex: 0 0 auto;
        padding: 7px 10px;
        border-radius: 999px;
        background: color-mix(in srgb, var(--card-background-color) 76%, transparent);
        border: 1px solid color-mix(in srgb, var(--divider-color) 42%, transparent);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
        color: var(--secondary-text-color);
      }
      .action-list {
        display: grid;
        gap: 8px;
        margin-top: 12px;
      }
      .action-item {
        display: grid;
        grid-template-columns: auto minmax(0, 1fr);
        gap: 10px;
        align-items: start;
        padding: 10px 12px;
        border-radius: 16px;
        background: color-mix(in srgb, var(--card-background-color) 78%, transparent);
        border: 1px solid color-mix(in srgb, var(--divider-color) 38%, transparent);
      }
      .action-item-primary {
        background: color-mix(in srgb, var(--card-background-color) 88%, transparent);
      }
      .action-rank {
        width: 24px;
        height: 24px;
        border-radius: 999px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: color-mix(in srgb, var(--primary-color) 12%, var(--card-background-color));
        font-size: 11px;
        font-weight: 700;
        color: var(--secondary-text-color);
      }
      .action-item-title {
        font-size: 14px;
        line-height: 1.35;
        font-weight: 640;
      }
      .action-item-summary {
        margin-top: 3px;
        font-size: 12px;
        line-height: 1.4;
        color: var(--secondary-text-color);
      }
      .action-item-meta {
        margin-top: 5px;
        font-size: 11px;
        line-height: 1.4;
        color: var(--secondary-text-color);
      }
      .focus-panel {
        margin-top: 16px;
      }
      .focus-title {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--secondary-text-color);
        font-weight: 700;
        margin-bottom: 10px;
      }
      .brief-grid {
        display: grid;
        gap: 14px;
        margin-top: 16px;
      }
      .brief-main,
      .brief-side {
        display: grid;
        gap: 14px;
      }
      .focus-list {
        display: grid;
        gap: 8px;
      }
      .focus-list.compact {
        gap: 6px;
      }
      .focus-item {
        padding: 12px 14px;
        border-radius: 18px;
        background: color-mix(in srgb, var(--secondary-background-color) 62%, transparent);
        border: 1px solid color-mix(in srgb, var(--divider-color) 42%, transparent);
      }
      .focus-primary {
        background: color-mix(in srgb, var(--primary-color) 8%, var(--card-background-color));
        border-color: color-mix(in srgb, var(--primary-color) 18%, transparent);
      }
      .focus-warning {
        background: color-mix(in srgb, var(--warning-color) 8%, var(--card-background-color));
        border-color: color-mix(in srgb, var(--warning-color) 18%, transparent);
      }
      .focus-headline {
        font-size: 15px;
        line-height: 1.35;
        font-weight: 620;
      }
      .focus-meta {
        margin-top: 4px;
        color: var(--secondary-text-color);
        font-size: 12px;
        line-height: 1.35;
      }
      .slot-panel {
        margin-top: 16px;
      }
      .slot-list {
        display: grid;
        gap: 8px;
      }
      .slot-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 10px 12px;
        border-radius: 16px;
        background: color-mix(in srgb, var(--secondary-background-color) 62%, transparent);
        border: 1px solid color-mix(in srgb, var(--divider-color) 42%, transparent);
      }
      .slot-row-busy {
        background: color-mix(in srgb, var(--warning-color) 8%, var(--card-background-color));
        border-color: color-mix(in srgb, var(--warning-color) 18%, transparent);
      }
      .slot-name {
        font-size: 13px;
        text-transform: capitalize;
        font-weight: 620;
      }
      .slot-count {
        color: var(--secondary-text-color);
        font-size: 12px;
      }
      .slot-people {
        margin-top: 3px;
        color: var(--secondary-text-color);
        font-size: 11px;
      }
      .slot-task-list {
        margin-top: 4px;
        color: var(--primary-text-color);
        font-size: 12px;
        line-height: 1.45;
      }
      .morning-brief-panel {
        margin-top: 18px;
        padding: 18px;
        border-radius: 24px;
        border: 1px solid color-mix(in srgb, var(--primary-color) 16%, transparent);
        background:
          linear-gradient(180deg, color-mix(in srgb, var(--primary-color) 7%, var(--card-background-color)), color-mix(in srgb, var(--primary-color) 3%, var(--card-background-color)));
        box-shadow: inset 0 1px 0 color-mix(in srgb, white 28%, transparent);
      }
      .morning-brief-header {
        display: grid;
        gap: 14px;
      }
      .morning-brief-eyebrow {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--secondary-text-color);
        font-weight: 700;
        margin-bottom: 8px;
      }
      .morning-brief-summary {
        margin-bottom: 10px;
        font-size: 13px;
        line-height: 1.5;
        color: var(--secondary-text-color);
      }
      .morning-brief-synopsis {
        margin-bottom: 12px;
        font-size: 13px;
        line-height: 1.6;
        color: var(--primary-text-color);
        opacity: 0.92;
      }
      .morning-brief-lead {
        font-size: 19px;
        line-height: 1.32;
        font-weight: 700;
        letter-spacing: -0.02em;
      }
      .morning-brief-meta {
        margin-top: 8px;
        color: var(--secondary-text-color);
        font-size: 12px;
        line-height: 1.5;
      }
      .morning-brief-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }
      .morning-brief-chip {
        display: inline-flex;
        align-items: center;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 11px;
        line-height: 1;
        font-weight: 700;
        color: var(--secondary-text-color);
        background: color-mix(in srgb, var(--card-background-color) 86%, transparent);
        border: 1px solid color-mix(in srgb, var(--divider-color) 44%, transparent);
      }
      .morning-brief-list {
        display: grid;
        gap: 12px;
        margin-top: 18px;
        padding-top: 14px;
        border-top: 1px solid color-mix(in srgb, var(--divider-color) 34%, transparent);
      }
      .brief-sections {
        display: grid;
        gap: 14px;
        margin-top: 18px;
        padding-top: 14px;
        border-top: 1px solid color-mix(in srgb, var(--divider-color) 34%, transparent);
      }
      .brief-sections-fallback {
        gap: 0;
      }
      .brief-section {
        display: grid;
        gap: 10px;
        padding: 12px;
        border-radius: 16px;
        background: color-mix(in srgb, var(--card-background-color) 82%, transparent);
        border: 1px solid color-mix(in srgb, var(--divider-color) 28%, transparent);
      }
      .brief-section-head {
        display: grid;
        grid-template-columns: 24px 1fr;
        gap: 10px;
        align-items: center;
        margin-bottom: 2px;
      }
      .brief-section-badge {
        width: 24px;
        height: 24px;
        border-radius: 999px;
        display: grid;
        place-items: center;
        font-size: 12px;
        font-weight: 800;
        color: white;
        background: var(--primary-color);
        box-shadow: 0 0 0 4px color-mix(in srgb, var(--primary-color) 14%, transparent);
      }
      .brief-section-title {
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--secondary-text-color);
      }
      .brief-section-body {
        display: grid;
        gap: 10px;
        border-left: 1px solid color-mix(in srgb, var(--divider-color) 24%, transparent);
        margin-left: 11px;
        padding-bottom: 2px;
        padding-left: 22px;
      }
      .brief-section-copy {
        font-size: 13px;
        line-height: 1.68;
        color: color-mix(in srgb, var(--primary-text-color) 92%, var(--secondary-text-color));
        max-width: 58ch;
      }
      .brief-section-copy-bullets {
        display: grid;
        gap: 8px;
      }
      .brief-bullet-row {
        display: grid;
        grid-template-columns: 8px 1fr;
        gap: 10px;
        align-items: start;
      }
      .brief-bullet-dot {
        width: 8px;
        height: 8px;
        margin-top: 6px;
        border-radius: 999px;
        background: color-mix(in srgb, var(--primary-color) 78%, white 22%);
      }
      .brief-bullet-text {
        font-size: 13px;
        line-height: 1.55;
        color: var(--primary-text-color);
      }
      .morning-brief-package {
        display: grid;
        gap: 10px;
        margin-top: 18px;
        padding-top: 14px;
        border-top: 1px solid color-mix(in srgb, var(--divider-color) 34%, transparent);
      }
      .morning-brief-package-row {
        display: grid;
        gap: 4px;
      }
      .morning-brief-package-title {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--secondary-text-color);
        font-weight: 700;
      }
      .morning-brief-package-value {
        font-size: 13px;
        line-height: 1.45;
        color: var(--primary-text-color);
      }
      .morning-brief-item {
        display: grid;
        grid-template-columns: 20px 1fr;
        gap: 10px;
        align-items: start;
      }
      .morning-brief-rank {
        width: 20px;
        height: 20px;
        border-radius: 999px;
        display: grid;
        place-items: center;
        font-size: 11px;
        font-weight: 700;
        color: var(--secondary-text-color);
        background: color-mix(in srgb, var(--divider-color) 72%, transparent);
      }
      .morning-brief-text {
        font-size: 13px;
        line-height: 1.45;
        color: var(--primary-text-color);
      }
      .signal-stack {
        display: grid;
        gap: 8px;
        margin-top: 14px;
      }
      .signal-row {
        display: grid;
        grid-template-columns: auto minmax(0, 1fr);
        gap: 10px;
        align-items: start;
        padding: 10px 0;
        border-top: 1px solid color-mix(in srgb, var(--divider-color) 32%, transparent);
      }
      .signal-row:first-child {
        border-top: 0;
      }
      .signal-dot {
        width: 8px;
        height: 8px;
        margin-top: 6px;
        border-radius: 999px;
        background: color-mix(in srgb, var(--primary-color) 50%, transparent);
      }
      .signal-text {
        line-height: 1.45;
        font-size: 13px;
      }
      .debug-panel {
        margin-top: 16px;
        padding-top: 12px;
        border-top: 1px dashed color-mix(in srgb, var(--divider-color) 46%, transparent);
      }
      .debug-title-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 8px;
      }
      .debug-title {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--secondary-text-color);
        font-weight: 700;
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
      @media (min-width: 900px) {
        .brief-grid {
          grid-template-columns: minmax(0, 1.1fr) minmax(280px, 0.9fr);
          align-items: start;
        }
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
