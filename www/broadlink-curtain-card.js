class BroadlinkCurtainCard extends HTMLElement {
  constructor() {
    super();
    this._hass = null;
  }

  set hass(hass) {
    this._hass = hass;

    if (!this.content) {
      const card = document.createElement('ha-card');
      card.header = '窗帘快捷控制';
      this.content = document.createElement('div');
      this.content.style.padding = '16px';
      card.appendChild(this.content);
      this.appendChild(card);
    }

    const entityId = this.config.entity;
    const state = hass.states[entityId];

    if (!state) {
      this.content.innerHTML = `
        <div style="color: red;">找不到实体: ${entityId}</div>
      `;
      return;
    }

    const currentPosition = state.attributes.current_position || 0;
    const currentState = state.attributes.current_state || 'stopped';

    this.content.innerHTML = `
      <style>
        .curtain-control {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .position-display {
          text-align: center;
          font-size: 48px;
          font-weight: bold;
          color: var(--primary-color);
          padding: 20px;
          background: var(--card-background-color);
          border-radius: 8px;
        }
        .position-buttons {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 12px;
        }
        .position-button {
          padding: 20px;
          font-size: 18px;
          font-weight: bold;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          background: var(--primary-color);
          color: white;
          transition: all 0.3s;
        }
        .position-button:hover {
          opacity: 0.8;
          transform: scale(1.05);
        }
        .position-button:active {
          transform: scale(0.95);
        }
        .position-button.current {
          background: var(--success-color);
        }
        .state-info {
          text-align: center;
          padding: 12px;
          background: var(--secondary-background-color);
          border-radius: 8px;
          font-size: 14px;
        }
        .slider-container {
          padding: 20px 12px;
          background: var(--card-background-color);
          border-radius: 8px;
        }
        .slider {
          width: 100%;
          height: 8px;
          -webkit-appearance: none;
          appearance: none;
          background: var(--secondary-background-color);
          outline: none;
          border-radius: 4px;
          cursor: pointer;
        }
        .slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 24px;
          height: 24px;
          background: var(--primary-color);
          border-radius: 50%;
          cursor: pointer;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .slider::-moz-range-thumb {
          width: 24px;
          height: 24px;
          background: var(--primary-color);
          border-radius: 50%;
          cursor: pointer;
          border: none;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .slider::-webkit-slider-thumb:hover {
          transform: scale(1.2);
        }
        .slider::-moz-range-thumb:hover {
          transform: scale(1.2);
        }
        .slider-label {
          display: flex;
          justify-content: space-between;
          margin-top: 8px;
          font-size: 12px;
          color: var(--secondary-text-color);
        }
      </style>
      <div class="curtain-control">
        <div class="position-display">
          ${currentPosition}%
        </div>
        <div class="state-info">
          状态: ${this.getStateText(currentState)}
        </div>
        <div class="slider-container">
          <input type="range" min="0" max="100" value="${currentPosition}"
                 class="slider" id="position-slider">
          <div class="slider-label">
            <span>← 关闭</span>
            <span>打开 →</span>
          </div>
        </div>
        <div class="position-buttons">
          <button class="position-button ${currentPosition === 25 ? 'current' : ''}" 
                  data-position="25">25%</button>
          <button class="position-button ${currentPosition === 50 ? 'current' : ''}" 
                  data-position="50">50%</button>
          <button class="position-button ${currentPosition === 75 ? 'current' : ''}" 
                  data-position="75">75%</button>
          <button class="position-button ${currentPosition === 100 ? 'current' : ''}" 
                  data-position="100">100%</button>
        </div>
      </div>
    `;

    // 添加按钮事件监听
    this.content.querySelectorAll('.position-button').forEach(button => {
      button.addEventListener('click', () => {
        const position = parseInt(button.dataset.position);
        this.setPosition(hass, entityId, position);
      });
    });

    // 添加滑块事件监听
    const slider = this.content.querySelector('#position-slider');

    // 实时更新滑块显示（拖动时）
    slider.addEventListener('input', () => {
      const position = parseInt(slider.value);
      const display = this.content.querySelector('.position-display');
      if (display) {
        display.textContent = `${position}%`;
      }
    });

    // 松开滑块时设置位置
    slider.addEventListener('change', () => {
      const position = parseInt(slider.value);
      this.setPosition(hass, entityId, position);
    });
  }

  getStateText(state) {
    const stateMap = {
      'opening': '正在打开',
      'closing': '正在关闭',
      'stopped': '已停止',
      'open': '已打开',
      'closed': '已关闭'
    };
    return stateMap[state] || state;
  }

  setPosition(hass, entityId, position) {
    hass.callService('cover', 'set_cover_position', {
      entity_id: entityId,
      position: position
    });
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('请指定entity');
    }
    this.config = config;
  }

  getCardSize() {
    return 5;
  }
}

customElements.define('broadlink-curtain-card', BroadlinkCurtainCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'broadlink-curtain-card',
  name: '博联窗帘控制卡片',
  description: '带快捷位置按钮的窗帘控制卡片'
});

