# 配置示例

本目录包含博联窗帘集成的各种配置示例。

## 📁 文件说明

### [lovelace-card-config.yaml](lovelace-card-config.yaml)
Lovelace仪表板卡片配置示例，包括：
- ✅ 单个窗帘卡片（推荐）
- ✅ 多个窗帘垂直堆叠
- ✅ 网格布局（2列）
- ✅ 带标题的卡片组
- ✅ 条件卡片（根据时间显示）
- ❌ 错误示例对比

### [configuration.yaml](configuration.yaml)
完整的Home Assistant配置示例，包括：
- 前端资源配置
- 日志配置
- 自动化示例（早晨/晚上/日落/离家）
- 脚本示例（半开/通风/同步）
- 场景示例（早晨/观影/午休）
- 输入选择器

## 🚀 快速使用

### 1. 添加自定义卡片

**步骤**:
1. 打开Home Assistant仪表板
2. 点击右上角 **⋮** → **编辑仪表板**
3. 点击 **+ 添加卡片**
4. 向下滚动，点击 **手动** 或 **按代码配置**
5. 复制 [lovelace-card-config.yaml](lovelace-card-config.yaml) 中的配置
6. 修改 `entity` 为你的实际窗帘实体ID
7. 点击 **保存** → **完成**

**最简单的配置**:
```yaml
type: custom:broadlink-curtain-card
entity: cover.你的窗帘名称
```

### 2. 配置自动化

**步骤**:
1. 打开 `configuration.yaml`
2. 复制 [configuration.yaml](configuration.yaml) 中的自动化配置
3. 修改实体ID和时间
4. 重启Home Assistant

**最简单的自动化**:
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

## 📝 重要提示

### ✅ 正确的卡片配置
```yaml
type: custom:broadlink-curtain-card  # ← 必须是这个
entity: cover.你的窗帘名称
```

**效果**:
- ✅ 水平滑块（左右拖动）
- ✅ 快捷按钮（25%/50%/75%/100%）
- ✅ 大号位置显示
- ✅ 实时进度更新

### ❌ 错误的卡片配置
```yaml
type: cover  # ← 这是默认卡片
entity: cover.你的窗帘名称
```

**效果**:
- ❌ 垂直滑块（上下移动）
- ❌ 没有快捷按钮
- ❌ 小号位置显示
- ❌ 不是实时更新

## 🎨 布局示例

### 单个窗帘
```yaml
type: custom:broadlink-curtain-card
entity: cover.客厅窗帘
```

### 多个窗帘（垂直）
```yaml
type: vertical-stack
cards:
  - type: custom:broadlink-curtain-card
    entity: cover.客厅窗帘
  - type: custom:broadlink-curtain-card
    entity: cover.卧室窗帘
```

### 多个窗帘（网格）
```yaml
type: grid
columns: 2
cards:
  - type: custom:broadlink-curtain-card
    entity: cover.客厅窗帘
  - type: custom:broadlink-curtain-card
    entity: cover.卧室窗帘
```

## 🔧 常见问题

**Q: 提示"没有可视化编辑器"？**
A: 这是正常的！自定义卡片只能用代码配置，不是错误。继续在代码编辑框中输入配置即可。

**Q: 卡片不显示快捷按钮？**
A: 确保使用 `type: custom:broadlink-curtain-card`，不是 `type: cover`

**Q: 提示找不到自定义卡片？**
A: 检查 `configuration.yaml` 中是否配置了资源：
```yaml
lovelace:
  resources:
    - url: /local/broadlink-curtain-card.js
      type: module
```

**Q: 如何查看我的窗帘实体ID？**
A: 进入 **设置** → **设备与服务** → **博联窗帘** → 查看实体列表

## 📚 更多资源

- [主README](../README.md) - 完整文档
- [GitHub仓库](https://github.com/woooxxs/broadlink_curtain) - 源代码和问题反馈

