"""修复的博联窗帘配置流程."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_CURTAINS,
    CONF_CURTAIN_CLOSE_CODE,
    CONF_CURTAIN_CLOSE_TIME,
    CONF_CURTAIN_MOVE_TIME,
    CONF_CURTAIN_NAME,
    CONF_CURTAIN_OPEN_CODE,
    CONF_CURTAIN_OPEN_TIME,
    CONF_CURTAIN_STOP_CODE,
    CONF_HOST,
    CONF_MAC,
    CONF_TIMEOUT,
    DEFAULT_MOVE_TIME,
    DEFAULT_TIMEOUT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# 一步完成所有配置（MAC地址可选，会自动获取）
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_MAC): str,  # 改为可选
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=60)
        ),
        vol.Required(CONF_CURTAIN_NAME): str,
        vol.Required(CONF_CURTAIN_OPEN_CODE): str,
        vol.Required(CONF_CURTAIN_CLOSE_CODE): str,
        vol.Required(CONF_CURTAIN_STOP_CODE): str,
        vol.Optional(CONF_CURTAIN_MOVE_TIME, default=DEFAULT_MOVE_TIME): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=300)
        ),
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """修复的配置流程."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """处理用户步骤 - 一步完成所有配置."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            # 验证输入格式
            host = user_input[CONF_HOST].strip()
            mac = user_input.get(CONF_MAC, "").strip()
            open_code = user_input[CONF_CURTAIN_OPEN_CODE].strip()
            close_code = user_input[CONF_CURTAIN_CLOSE_CODE].strip()
            stop_code = user_input[CONF_CURTAIN_STOP_CODE].strip()

            # 验证IP地址格式
            if not self._is_valid_ip(host):
                errors[CONF_HOST] = "IP地址格式不正确，请使用IPv4格式，如: 192.168.1.100"

            # 如果没有提供MAC地址，尝试自动发现
            if not mac and not errors:
                _LOGGER.info("未提供MAC地址，尝试自动发现设备...")
                discovered_mac = await self._discover_device(host, user_input[CONF_TIMEOUT])
                if discovered_mac:
                    mac = discovered_mac
                    _LOGGER.info("✅ 自动发现设备MAC地址: %s", mac)
                else:
                    errors[CONF_MAC] = "无法自动获取MAC地址，请手动输入"

            # 验证MAC地址格式（如果有）
            if mac and not self._is_valid_mac(mac):
                errors[CONF_MAC] = "MAC地址格式不正确，请使用格式如: aa:bb:cc:dd:ee:ff"
            
            # 验证射频码格式
            if not self._is_valid_rf_code(open_code):
                errors[CONF_CURTAIN_OPEN_CODE] = "射频码格式不正确，请使用十六进制格式，如: deadbeef"
            if not self._is_valid_rf_code(close_code):
                errors[CONF_CURTAIN_CLOSE_CODE] = "射频码格式不正确，请使用十六进制格式，如: beefdead"
            if not self._is_valid_rf_code(stop_code):
                errors[CONF_CURTAIN_STOP_CODE] = "射频码格式不正确，请使用十六进制格式，如: feedface"
            
            # 如果没有格式错误，尝试连接设备
            if not errors:
                try:
                    from .coordinator import BroadlinkCurtainCoordinator
                    coordinator = BroadlinkCurtainCoordinator(self.hass, None)
                    coordinator.host = host
                    coordinator.mac = mac
                    coordinator.timeout = user_input[CONF_TIMEOUT]
                    
                    if await coordinator.async_test_connection():
                        # 创建窗帘配置
                        move_time = user_input[CONF_CURTAIN_MOVE_TIME]
                        curtain_config = {
                            CONF_CURTAIN_NAME: user_input[CONF_CURTAIN_NAME],
                            CONF_CURTAIN_OPEN_CODE: open_code,
                            CONF_CURTAIN_CLOSE_CODE: close_code,
                            CONF_CURTAIN_STOP_CODE: stop_code,
                            CONF_CURTAIN_MOVE_TIME: move_time,
                            CONF_CURTAIN_OPEN_TIME: move_time,  # 兼容旧版本
                            CONF_CURTAIN_CLOSE_TIME: move_time,  # 兼容旧版本
                        }

                        # 完成配置
                        config_data = {
                            CONF_HOST: host,
                            CONF_MAC: mac,
                            CONF_TIMEOUT: user_input[CONF_TIMEOUT],
                            CONF_CURTAINS: [curtain_config]
                        }

                        return self.async_create_entry(
                            title=f"博联窗帘 - {user_input[CONF_CURTAIN_NAME]}",
                            data=config_data
                        )
                    else:
                        errors["base"] = "无法连接到博联设备，请检查IP地址和网络连接"
                except Exception as ex:
                    _LOGGER.exception("配置流程错误: %s", ex)
                    errors["base"] = f"配置过程中发生错误: {str(ex)}"

        return self.async_show_form(
            step_id="user", 
            data_schema=STEP_USER_DATA_SCHEMA, 
            errors=errors,
            description_placeholders={
                "help_text": """
                <h3>博联窗帘配置</h3>
                <p><b>设备IP地址:</b> 博联设备的局域网IP地址，如 192.168.1.100（必填）</p>
                <p><b>MAC地址:</b> 博联设备的MAC地址，如 aa:bb:cc:dd:ee:ff（可选，留空自动获取）</p>
                <p><b>超时时间:</b> 设备连接超时时间，默认5秒</p>
                <p><b>窗帘名称:</b> 窗帘的显示名称，如 客厅窗帘</p>
                <p><b>开启射频码:</b> 使用博联App学习的开启射频码，如 deadbeef</p>
                <p><b>关闭射频码:</b> 使用博联App学习的关闭射频码，如 beefdead</p>
                <p><b>停止射频码:</b> 使用博联App学习的停止射频码，如 feedface</p>
                <p><b>移动时间:</b> 窗帘完全开启或关闭所需时间，默认30秒</p>
                <br>
                <p><b>快速配置方法:</b></p>
                <p>1. 打开博联官方App，查看设备IP地址</p>
                <p>2. 学习射频码获取开、关、停三个射频码</p>
                <p>3. 填写IP地址和射频码，MAC地址会自动获取</p>
                <p>4. 如果自动获取失败，可手动填写MAC地址</p>
                """
            }
        )

    def _is_valid_ip(self, ip: str) -> bool:
        """验证IP地址格式."""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not part.isdigit() or int(part) < 0 or int(part) > 255:
                    return False
            return True
        except:
            return False
    
    def _is_valid_mac(self, mac: str) -> bool:
        """验证MAC地址格式."""
        try:
            # 支持多种MAC地址格式
            mac = mac.replace(':', '').replace('-', '').replace(' ', '')
            if len(mac) != 12:
                return False
            int(mac, 16)  # 验证是否为有效的十六进制
            return True
        except:
            return False
    
    def _is_valid_rf_code(self, code: str) -> bool:
        """验证射频码格式."""
        try:
            # 射频码应为十六进制字符串
            if not code:
                return False
            code = code.replace(' ', '').replace('-', '')
            if len(code) % 2 != 0:  # 长度必须为偶数
                return False
            int(code, 16)  # 验证是否为有效的十六进制
            return True
        except:
            return False

    async def _discover_device(self, host: str, timeout: int = 5) -> Optional[str]:
        """通过IP地址自动发现设备并获取MAC地址."""
        try:
            import broadlink

            _LOGGER.info("🔍 开始自动发现设备: %s (超时: %d秒)", host, timeout)

            # 方法1: 尝试直接连接设备获取MAC
            try:
                # 解析IP地址
                ip_parts = host.split('.')
                if len(ip_parts) == 4:
                    # 尝试使用gendevice直接连接
                    _LOGGER.info("🔌 尝试直接连接设备...")
                    device = broadlink.gendevice(0x2712, (host, 80), bytearray([0]*6))
                    await self.hass.async_add_executor_job(device.auth)
                    mac = ':'.join(format(x, '02x') for x in device.mac)
                    _LOGGER.info("✅ 直接连接成功，MAC: %s", mac)
                    return mac
            except Exception as ex:
                _LOGGER.debug("直接连接失败: %s，尝试discover方法", ex)

            # 方法2: 使用discover功能
            _LOGGER.info("🔍 使用discover方法搜索设备...")
            devices = await self.hass.async_add_executor_job(
                broadlink.discover, timeout
            )

            if devices:
                # 查找匹配IP的设备
                for device in devices:
                    device_host = device.host[0]
                    if device_host == host:
                        mac = ':'.join(format(x, '02x') for x in device.mac)
                        _LOGGER.info("✅ 发现设备: %s, MAC: %s", host, mac)
                        return mac

                # 如果没有找到匹配的，返回第一个设备的MAC
                if len(devices) > 0:
                    device = devices[0]
                    mac = ':'.join(format(x, '02x') for x in device.mac)
                    _LOGGER.warning("⚠️ 未找到IP匹配的设备，使用第一个发现的设备 MAC: %s", mac)
                    return mac

            _LOGGER.warning("⚠️ 未发现任何设备")
            return None

        except Exception as ex:
            _LOGGER.error("❌ 自动发现设备失败: %s", ex, exc_info=True)
            return None
