"""博联窗帘组件常量定义."""

DOMAIN = "broadlink_curtain"

# 配置键
CONF_HOST = "host"
CONF_MAC = "mac"
CONF_TIMEOUT = "timeout"
CONF_CURTAINS = "curtains"

# 窗帘配置键
CONF_CURTAIN_NAME = "name"
CONF_CURTAIN_MOVE_TIME = "move_time"  # 统一的移动时间
CONF_CURTAIN_OPEN_TIME = "open_time"  # 保留用于兼容
CONF_CURTAIN_CLOSE_TIME = "close_time"  # 保留用于兼容
CONF_CURTAIN_OPEN_CODE = "open_code"
CONF_CURTAIN_CLOSE_CODE = "close_code"
CONF_CURTAIN_STOP_CODE = "stop_code"

# 默认值
DEFAULT_TIMEOUT = 5
DEFAULT_MOVE_TIME = 30  # 默认移动时间
DEFAULT_OPEN_TIME = 30  # 保留用于兼容
DEFAULT_CLOSE_TIME = 30  # 保留用于兼容

# 设备状态
DEVICE_STATUS_ONLINE = "online"
DEVICE_STATUS_OFFLINE = "offline"
DEVICE_STATUS_ERROR = "error"

# 窗帘状态
CURTAIN_STATE_OPENING = "opening"
CURTAIN_STATE_CLOSING = "closing"
CURTAIN_STATE_STOPPED = "stopped"
CURTAIN_STATE_OPEN = "open"
CURTAIN_STATE_CLOSED = "closed"

# 射频码类型
RF_CODE_OPEN = "open"
RF_CODE_CLOSE = "close"
RF_CODE_STOP = "stop"
