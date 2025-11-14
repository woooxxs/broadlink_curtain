<div align="center">
  <img src="custom_components/broadlink_curtain/logo.svg" alt="Broadlink Curtain Logo" width="200"/>

  # 博联窗帘 Home Assistant 自定义组件

  通过博联射频遥控器控制窗帘，支持精确位置控制和实时进度显示

  [![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.1+-blue.svg)](https://www.home-assistant.io/)
  [![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
</div>

---

## ✨ 核心功能

- 🎯 **精确位置控制** - 0-100%任意位置，基于时间计算
- 🔄 **实时进度显示** - 移动过程中每0.5秒更新位置
- 🎚️ **水平滑块** - 左右拖动，模拟窗帘开合
- 🎨 **快捷按钮** - 25%/50%/75%/100%一键到位
- 💾 **位置持久化** - 重启后自动恢复位置
- 🔍 **自动发现** - 只需IP地址，自动获取MAC

## 🎬 效果预览

### 自定义卡片（推荐）

```
┌─────────────────────────────┐
│    窗帘快捷控制              │
├─────────────────────────────┤
│          50%                 │  ← 大号位置显示
├─────────────────────────────┤
│    状态: 已打开              │
├─────────────────────────────┤
│  ← 关闭  ═══●═══  打开 →    │  ← 水平滑块（实时更新）
├─────────────────────────────┤
│   [25%] [50%] [75%] [100%]   │  ← 快捷按钮
└─────────────────────────────┘
```

**特点**:
- 水平滑块（左右移动）
- 实时进度更新（每0.5秒）
- 四个快捷位置按钮
- 大号位置显示（48px）

## 📦 快速开始

### 1. 安装组件

```bash
# 复制组件到Home Assistant配置目录
cp -r custom_components/broadlink_curtain /config/custom_components/

# 复制前端卡片
cp -r www/broadlink-curtain-card.js /config/www/

# 重启Home Assistant
```

### 2. 配置资源

在 `configuration.yaml` 中添加：

```yaml
lovelace:
  mode: storage
  resources:
    - url: /local/broadlink-curtain-card.js
      type: module
```

### 3. 添加集成

1. 进入 **设置** → **设备与服务** → **添加集成**
2. 搜索 **"博联窗帘"**
3. 输入配置：
   - **IP地址**: 博联设备IP（必填）
   - **MAC地址**: 留空自动获取
   - **窗帘名称**: 自定义名称
   - **移动时间**: 完全开/关所需秒数
   - **射频码**: 开/关/停三个射频码

### 4. 添加自定义卡片

1. 编辑仪表板
2. 添加卡片 → 手动配置
3. 输入：
   ```yaml
   type: custom:broadlink-curtain-card
   entity: cover.你的窗帘名称
   ```
4. 保存

## 🎮 使用说明

### 基本操作

- **打开/关闭**: 点击按钮完全打开或关闭
- **停止**: 移动过程中点击停止
- **滑块**: 拖动到目标位置，松开自动移动
- **快捷按钮**: 点击25%/50%/75%/100%快速到位

### 自动化示例

```yaml
automation:
  - alias: "早上打开窗帘"
    trigger:
      platform: time
      at: "07:00:00"
    action:
      service: cover.set_cover_position
      target:
        entity_id: cover.客厅窗帘
      data:
        position: 80
```

## 🧪 Docker测试环境

```bash
# 启动测试环境
cd docker
docker-compose up -d

# 访问
# Home Assistant: http://localhost:8123
# 模拟设备: http://localhost:9000

# 测试配置
# IP: 172.20.0.30
# 射频码: deadbeef, beefdead, feedface
```

## 🔧 常见问题

**Q: 自定义卡片不显示？**
A: 检查 `configuration.yaml` 中是否配置了资源，清除浏览器缓存后重启HA

**Q: 位置不准确？**
A: 调整"移动时间"配置，使用秒表测量窗帘完全开/关的实际时间

**Q: 状态显示"未知"？**
A: 已修复，确保使用最新版本

**Q: 滑块是垂直的？**
A: 默认卡片是垂直的，使用自定义卡片获得水平滑块

## 📊 调试日志

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.broadlink_curtain: debug
```

## 📝 更新日志

### v2.4 (2025-11-14)
- ✅ 实时进度显示（每0.5秒更新）
- ✅ 水平滑块支持
- ✅ 修复状态显示"未知"问题
- ✅ 所有按钮始终可用
- ✅ 添加logo

### v2.0
- ✅ 位置持久化
- ✅ 快捷按钮（25%/50%/75%/100%）
- ✅ 自动MAC地址发现
- ✅ 统一移动时间配置

---

<div align="center">
  <sub>Built with ❤️ for Home Assistant</sub>
</div>