# 博联窗帘 Broadlink Curtain

通过博联射频遥控器控制窗帘，支持精确位置控制和实时进度显示。

## 功能特点

- 🎯 **精确位置控制** - 0-100%任意位置，基于时间计算
- 🔄 **实时进度显示** - 移动过程中每0.5秒更新位置
- 🎚️ **水平滑块** - 左右拖动，模拟窗帘开合
- 🎨 **快捷按钮** - 25%/50%/75%/100%一键到位
- 💾 **位置持久化** - 重启后自动恢复位置
- 🔍 **自动发现** - 只需IP地址，自动获取MAC

## 安装方法

### 通过HACS安装（推荐）

1. 打开HACS
2. 点击"集成"
3. 点击右上角菜单，选择"自定义存储库"
4. 输入仓库地址：`https://github.com/woooxxs/broadlink_curtain`
5. 类别选择"Integration"
6. 点击"添加"
7. 搜索"博联窗帘"并安装
8. 重启Home Assistant

### 手动安装

1. 下载最新版本
2. 解压到 `config/custom_components/broadlink_curtain/`
3. 复制 `www/broadlink-curtain-card.js` 到 `config/www/`
4. 重启Home Assistant

## 配置

### 1. 添加集成

1. 进入 **设置** → **设备与服务** → **添加集成**
2. 搜索 **"博联窗帘"**
3. 输入配置：
   - IP地址：博联设备IP
   - MAC地址：留空自动获取
   - 窗帘名称：自定义名称
   - 移动时间：完全开/关所需秒数
   - 射频码：开/关/停三个射频码

### 2. 配置前端资源

在 `configuration.yaml` 中添加：

```yaml
lovelace:
  mode: storage
  resources:
    - url: /local/broadlink-curtain-card.js
      type: module
```

### 3. 添加自定义卡片

编辑仪表板 → 添加卡片 → 手动配置：

```yaml
type: custom:broadlink-curtain-card
entity: cover.你的窗帘名称
```

## 使用说明

- **拖动滑块**：左右拖动到目标位置，松开自动移动
- **快捷按钮**：点击25%/50%/75%/100%快速到位
- **实时进度**：移动时位置每0.5秒更新
- **停止功能**：移动过程中可随时停止

## 支持

如有问题或建议，请访问：
https://github.com/woooxxs/broadlink_curtain/issues

