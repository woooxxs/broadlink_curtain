"""博联窗帘自定义组件."""
import asyncio
import logging
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import BroadlinkCurtainCoordinator
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.COVER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """设置博联窗帘配置条目."""
    _LOGGER.info("正在设置博联窗帘组件")
    
    # 创建协调器
    coordinator = BroadlinkCurtainCoordinator(hass, entry)
    
    # 测试连接
    if not await coordinator.async_test_connection():
        _LOGGER.error("无法连接到博联设备")
        return False
    
    # 存储协调器
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    
    # 启动平台
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # 设置服务
    await async_setup_services(hass)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载博联窗帘配置条目."""
    _LOGGER.info("正在卸载博联窗帘组件")
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
