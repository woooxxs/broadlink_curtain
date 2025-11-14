class BroadlinkCurtainCard extends HTMLElement {
  constructor() {
    super();
    this._hass = null;
    this._expanded = false; // 添加展开状态
  }

  set hass(hass) {
    this._hass = hass;

    if (!this.content) {
      const card = document.createElement('ha-card');
      this.content = document.createElement('div');
      card.appendChild(this.content);
      this.appendChild(card);
    }

    const entityId = this.config.entity;
    const state = hass.states[entityId];

    if (!state) {
      this.content.innerHTML = `
        <div style="color: red; padding: 16px;">找不到实体: ${entityId}</div>
      `;
      return;
    }

    const currentPosition = state.attributes.current_position || 0;
    const currentState = state.attributes.current_state || 'stopped';

    // 根据展开状态渲染不同的视图
    if (this._expanded) {
      this.renderExpanded(currentPosition, currentState, entityId);
    } else {
      this.renderCompact(currentPosition, currentState, entityId);
    }
  }

  renderCompact(currentPosition, currentState, entityId) {
    // 根据位置判断窗帘状态，选择图标
    const isOpen = currentPosition > 50;
    // mdi:curtains (打开) 和 mdi:curtains-closed (关闭)
    const iconPath = isOpen
      ? 'M3 3v2h18V3M3 19v2h18v19M13 6v11h8V6M4 6v11h8V6m-1 1v9H5V7m8 0v9h6V7Z' // mdi:curtains
      : 'M15.5 6.5A1.5 1.5 0 0 1 17 8v8a1.5 1.5 0 0 1-1.5 1.5h-7A1.5 1.5 0 0 1 7 16V8a1.5 1.5 0 0 1 1.5-1.5M3 3v2h18V3M3 19v2h18v-2Z'; // mdi:curtains-closed

    this.content.innerHTML = `
      <style>
        .compact-view {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 12px 16px;
        }
        .compact-icon-wrapper {
          position: relative;
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
        }
        .compact-icon {
          width: 24px;
          height: 24px;
          fill: var(--state-icon-color);
          transition: fill 0.2s;
        }
        .compact-icon-wrapper:hover .compact-icon {
          fill: var(--state-icon-active-color);
        }
        .compact-info {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          min-width: 0;
        }
        .compact-name {
          font-weight: 400;
          font-size: 14px;
          color: var(--primary-text-color);
          white-space: nowrap;
        }
        .compact-right {
          display: flex;
          align-items: center;
          gap: 12px;
          flex: 1;
          justify-content: flex-end;
          min-width: 0;
        }
        .compact-slider-container {
          position: relative;
          flex: 1;
          max-width: 200px;
          height: 4px;
          background: var(--disabled-text-color);
          border-radius: 2px;
          cursor: pointer;
        }
        .compact-position {
          font-size: 14px;
          color: var(--secondary-text-color);
          white-space: nowrap;
          min-width: 40px;
          text-align: right;
        }
        .compact-slider-fill {
          position: absolute;
          left: 0;
          top: 0;
          height: 100%;
          background: var(--primary-color);
          border-radius: 2px;
          transition: width 0.3s;
        }
        .compact-slider-thumb {
          position: absolute;
          top: 50%;
          transform: translate(-50%, -50%);
          width: 16px;
          height: 16px;
          background: var(--primary-color);
          border-radius: 50%;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
          transition: left 0.3s;
        }
      </style>
      <div class="compact-view">
        <div class="compact-icon-wrapper" id="icon-button">
          <svg class="compact-icon" viewBox="0 0 24 24">
            <path d="${iconPath}"/>
          </svg>
        </div>
        <div class="compact-info">
          <div class="compact-name">窗帘</div>
          <div class="compact-right">
            <div class="compact-slider-container" id="compact-slider">
              <div class="compact-slider-fill" style="width: ${currentPosition}%"></div>
              <div class="compact-slider-thumb" style="left: ${currentPosition}%"></div>
            </div>
            <div class="compact-position">${currentPosition}%</div>
          </div>
        </div>
      </div>
    `;

    // 点击图标展开详细视图
    const iconButton = this.content.querySelector('#icon-button');
    iconButton.addEventListener('click', (e) => {
      e.stopPropagation();
      this._expanded = true;
      this.hass = this._hass;
    });

    // 点击进度条设置位置
    const sliderContainer = this.content.querySelector('#compact-slider');
    sliderContainer.addEventListener('click', (e) => {
      const rect = sliderContainer.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const percentage = Math.round((x / rect.width) * 100);
      const position = Math.max(0, Math.min(100, percentage));
      this.setPosition(this._hass, entityId, position);
    });
  }

  renderExpanded(currentPosition, currentState, entityId) {
    this.content.innerHTML = `
      <style>
        .curtain-control {
          display: flex;
          flex-direction: column;
          gap: 12px;
          padding: 16px;
        }
        .header-bar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 4px;
        }
        .back-button {
          background: none;
          border: none;
          font-size: 20px;
          cursor: pointer;
          padding: 4px 8px;
          color: var(--primary-text-color);
          display: flex;
          align-items: center;
        }
        .back-button:hover {
          opacity: 0.7;
        }
        .header-title {
          font-size: 16px;
          font-weight: 500;
        }
        .position-display {
          text-align: center;
          font-size: 32px;
          font-weight: bold;
          color: var(--primary-color);
          padding: 12px;
          background: var(--card-background-color);
          border-radius: 8px;
        }
        .control-buttons {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 8px;
          margin-bottom: 8px;
        }
        .control-button {
          padding: 12px 8px;
          font-size: 14px;
          font-weight: 500;
          border: 2px solid var(--primary-color);
          border-radius: 8px;
          cursor: pointer;
          background: transparent;
          color: var(--primary-color);
          transition: all 0.2s;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 4px;
        }
        .control-button:hover {
          background: var(--primary-color);
          color: white;
        }
        .control-button:active {
          transform: scale(0.95);
        }
        .control-button.stop {
          border-color: var(--error-color);
          color: var(--error-color);
        }
        .control-button.stop:hover {
          background: var(--error-color);
          color: white;
        }
        .position-buttons {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 8px;
        }
        .position-button {
          padding: 12px 8px;
          font-size: 14px;
          font-weight: 500;
          border: 2px solid var(--primary-color);
          border-radius: 8px;
          cursor: pointer;
          background: transparent;
          color: var(--primary-color);
          transition: all 0.2s;
        }
        .position-button:hover {
          background: var(--primary-color);
          color: white;
        }
        .position-button:active {
          transform: scale(0.95);
        }
        .position-button.current {
          background: var(--primary-color);
          color: white;
        }
        .state-info {
          text-align: center;
          padding: 8px;
          background: var(--secondary-background-color);
          border-radius: 8px;
          font-size: 13px;
          color: var(--secondary-text-color);
        }
        .slider-container {
          padding: 16px 12px;
          background: var(--card-background-color);
          border-radius: 8px;
        }
        .slider {
          width: 100%;
          height: 6px;
          -webkit-appearance: none;
          appearance: none;
          background: var(--disabled-text-color);
          outline: none;
          border-radius: 3px;
          cursor: pointer;
        }
        .slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 20px;
          height: 20px;
          background: var(--primary-color);
          border-radius: 50%;
          cursor: pointer;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .slider::-moz-range-thumb {
          width: 20px;
          height: 20px;
          background: var(--primary-color);
          border-radius: 50%;
          cursor: pointer;
          border: none;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .slider::-webkit-slider-thumb:hover {
          transform: scale(1.15);
        }
        .slider::-moz-range-thumb:hover {
          transform: scale(1.15);
        }
        .slider-label {
          display: flex;
          justify-content: space-between;
          margin-top: 8px;
          font-size: 11px;
          color: var(--secondary-text-color);
        }
      </style>
      <div class="curtain-control">
        <div class="header-bar">
          <button class="back-button" id="back-button">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z"/>
            </svg>
          </button>
          <div class="header-title">窗帘控制</div>
          <div style="width: 28px;"></div>
        </div>
        <div class="position-display">
          ${currentPosition}%
        </div>
        <div class="state-info">
          ${this.getStateText(currentState)}
        </div>
        <div class="slider-container">
          <input type="range" min="0" max="100" value="${currentPosition}"
                 class="slider" id="position-slider">
          <div class="slider-label">
            <span>关闭</span>
            <span>打开</span>
          </div>
        </div>
        <div class="control-buttons">
          <button class="control-button" id="open-button">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 3v2h18V3M3 19v2h18v19M13 6v11h8V6M4 6v11h8V6m-1 1v9H5V7m8 0v9h6V7Z"/>
            </svg>
            全开
          </button>
          <button class="control-button stop" id="stop-button">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18,18H6V6H18V18Z"/>
            </svg>
            暂停
          </button>
          <button class="control-button" id="close-button">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M15.5 6.5A1.5 1.5 0 0 1 17 8v8a1.5 1.5 0 0 1-1.5 1.5h-7A1.5 1.5 0 0 1 7 16V8a1.5 1.5 0 0 1 1.5-1.5M3 3v2h18V3M3 19v2h18v-2Z"/>
            </svg>
            全关
          </button>
        </div>
        <div class="position-buttons">
          <button class="position-button ${currentPosition === 25 ? 'current' : ''}"
                  data-position="25">25%</button>
          <button class="position-button ${currentPosition === 50 ? 'current' : ''}"
                  data-position="50">50%</button>
          <button class="position-button ${currentPosition === 75 ? 'current' : ''}"
                  data-position="75">75%</button>
        </div>
      </div>
    `;

    // 添加返回按钮事件
    const backButton = this.content.querySelector('#back-button');
    backButton.addEventListener('click', (e) => {
      e.stopPropagation();
      this._expanded = false;
      this.hass = this._hass; // 重新渲染
    });

    // 添加全开按钮事件
    const openButton = this.content.querySelector('#open-button');
    openButton.addEventListener('click', () => {
      this._hass.callService('cover', 'open_cover', {
        entity_id: entityId
      });
    });

    // 添加全关按钮事件
    const closeButton = this.content.querySelector('#close-button');
    closeButton.addEventListener('click', () => {
      this._hass.callService('cover', 'close_cover', {
        entity_id: entityId
      });
    });

    // 添加暂停按钮事件
    const stopButton = this.content.querySelector('#stop-button');
    stopButton.addEventListener('click', () => {
      this._hass.callService('cover', 'stop_cover', {
        entity_id: entityId
      });
    });

    // 添加位置按钮事件监听
    this.content.querySelectorAll('.position-button').forEach(button => {
      button.addEventListener('click', () => {
        const position = parseInt(button.dataset.position);
        this.setPosition(this._hass, entityId, position);
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
      this.setPosition(this._hass, entityId, position);
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
    return this._expanded ? 5 : 1;
  }
}

customElements.define('broadlink-curtain-card', BroadlinkCurtainCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'broadlink-curtain-card',
  name: '博联窗帘控制卡片',
  description: '带快捷位置按钮的窗帘控制卡片'
});

