"""博联窗帘协调器."""
import asyncio
import logging
from typing import Any, Dict, List, Optional

import broadlink
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_CURTAINS,
    CONF_HOST,
    CONF_MAC,
    CONF_TIMEOUT,
    DEVICE_STATUS_ERROR,
    DEVICE_STATUS_OFFLINE,
    DEVICE_STATUS_ONLINE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class BroadlinkCurtainCoordinator(DataUpdateCoordinator):
    """博联窗帘协调器."""

    def __init__(self, hass: HomeAssistant, entry: Optional[ConfigEntry]):
        """初始化协调器."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,  # 手动更新
        )
        
        self.hass = hass
        self.entry = entry
        self.device = None
        self.host = None
        self.mac = None
        self.timeout = 5
        
        if entry:
            self.host = entry.data.get(CONF_HOST)
            self.mac = entry.data.get(CONF_MAC)
            self.timeout = entry.data.get(CONF_TIMEOUT, 5)
            self.curtains = entry.data.get(CONF_CURTAINS, [])

    async def async_test_connection(self) -> bool:
        """测试设备连接."""
        try:
            if not self.host or not self.mac:
                _LOGGER.error("设备配置不完整: host=%s, mac=%s", self.host, self.mac)
                return False
            
            _LOGGER.info("🔌 开始连接博联设备")
            _LOGGER.info("   - 设备IP: %s", self.host)
            _LOGGER.info("   - 设备MAC: %s", self.mac)
            _LOGGER.info("   - 设备类型: RM4 Pro (0x520B)")
            _LOGGER.info("   - 超时设置: %d 秒", self.timeout)
                
            # 创建设备对象
            self.device = broadlink.rm4(
                host=(self.host, 80),
                mac=bytearray.fromhex(self.mac.replace(":", "")),
                devtype=0x520B,  # RM4 Pro
                timeout=self.timeout
            )
            
            _LOGGER.info("📡 尝试设备认证...")
            # 测试连接
            await self.hass.async_add_executor_job(self.device.auth)
            
            _LOGGER.info("✅ 成功连接到博联设备: %s", self.host)
            _LOGGER.info("   - 连接时间: %s", asyncio.get_event_loop().time())
            _LOGGER.info("   - 设备状态: 在线")
            return True
            
        except Exception as ex:
            _LOGGER.error("❌ 连接博联设备失败: %s", ex)
            _LOGGER.error("   - 错误类型: %s", type(ex).__name__)
            _LOGGER.error("   - 设备IP: %s", self.host)
            _LOGGER.error("   - 设备MAC: %s", self.mac)
            self.device = None
            return False

    async def async_send_rf_code(self, code: str) -> bool:
        """发送射频码."""
        try:
            if not self.device:
                _LOGGER.warning("设备未连接，尝试重新连接...")
                if not await self.async_test_connection():
                    _LOGGER.error("设备连接失败，无法发送射频码")
                    return False
            
            # 记录发送前的详细信息
            _LOGGER.info("📡 准备发送射频码")
            _LOGGER.info("   - 设备IP: %s", self.host)
            _LOGGER.info("   - 设备MAC: %s", self.mac)
            _LOGGER.info("   - 射频码: %s", code)
            _LOGGER.info("   - 射频码长度: %d 字节", len(code) // 2)
            _LOGGER.info("   - 超时设置: %d 秒", self.timeout)
            
            # 发送射频码
            code_bytes = bytearray.fromhex(code)
            _LOGGER.info("   - 字节数据: %s", code_bytes.hex())
            
            await self.hass.async_add_executor_job(
                self.device.send_data, code_bytes
            )
            
            _LOGGER.info("✅ 射频码发送成功: %s", code)
            _LOGGER.info("   - 发送时间: %s", asyncio.get_event_loop().time())
            return True
            
        except Exception as ex:
            _LOGGER.error("❌ 射频码发送失败: %s", ex)
            _LOGGER.error("   - 错误类型: %s", type(ex).__name__)
            _LOGGER.error("   - 射频码: %s", code)
            _LOGGER.error("   - 设备状态: %s", "已连接" if self.device else "未连接")
            return False

    async def async_get_device_status(self) -> str:
        """获取设备状态."""
        try:
            if not self.device:
                if not await self.async_test_connection():
                    return DEVICE_STATUS_OFFLINE
            
            # 检查设备状态
            await self.hass.async_add_executor_job(self.device.check_temperature)
            return DEVICE_STATUS_ONLINE
            
        except Exception as ex:
            _LOGGER.error("获取设备状态失败: %s", ex)
            return DEVICE_STATUS_ERROR

    async def _async_update_data(self) -> Dict[str, Any]:
        """更新数据."""
        try:
            status = await self.async_get_device_status()
            
            return {
                "device_status": status,
                "curtains": self.curtains if hasattr(self, 'curtains') else []
            }
            
        except Exception as ex:
            _LOGGER.error("更新数据失败: %s", ex)
            raise UpdateFailed(f"更新数据失败: {ex}")

    def get_curtain_config(self, curtain_id: str) -> Optional[Dict[str, Any]]:
        """获取窗帘配置."""
        if not hasattr(self, 'curtains'):
            return None
            
        for curtain in self.curtains:
            if curtain.get("name") == curtain_id:
                return curtain
        return None
