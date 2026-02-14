/* Minimal frontend stub.
 *
 * This is intentionally tiny. If you ship a real card, consider building it from a
 * separate project and committing the built artifact here.
 */

class HacsTemplateCard extends HTMLElement {
  setConfig(config) {
    this._config = config || {};
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  render() {
    const entryId = this._config?.entry_id || "(missing entry_id)";
    this.innerHTML = `
      <ha-card header="HACS Template Card">
        <div style="padding: 12px">
          <div><b>entry_id:</b> ${entryId}</div>
          <div style="margin-top: 8px; color: var(--secondary-text-color)">
            Replace this stub with your real UI.
          </div>
        </div>
      </ha-card>
    `;
  }

  getCardSize() {
    return 2;
  }
}

customElements.define("hacs-template-card", HacsTemplateCard);

