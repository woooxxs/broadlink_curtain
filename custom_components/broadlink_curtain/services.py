"""博联窗帘服务."""
import logging
from typing import Any, Dict
from datetime import datetime

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.components.cover import DOMAIN as COVER_DOMAIN
import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SET_CURTAIN_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required("open_time"): cv.positive_int,
        vol.Required("close_time"): cv.positive_int,
        vol.Required("open_code"): cv.string,
        vol.Required("close_code"): cv.string,
        vol.Required("stop_code"): cv.string,
    }
)

TEST_RF_CODE_SCHEMA = vol.Schema(
    {
        vol.Required("code"): cv.string,
        vol.Required("code_type"): vol.In(["open", "close", "stop"]),
    }
)

SET_POSITION_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Required("position"): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
    }
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """设置服务."""

    async def set_curtain_config(call: ServiceCall) -> None:
        """设置窗帘配置."""
        entity_id = call.data["entity_id"]
        open_time = call.data["open_time"]
        close_time = call.data["close_time"]
        open_code = call.data["open_code"]
        close_code = call.data["close_code"]
        stop_code = call.data["stop_code"]

        # 获取实体
        entity = hass.states.get(entity_id)
        if not entity:
            _LOGGER.error("找不到实体: %s", entity_id)
            return

        # 获取协调器
        coordinator = None
        for entry_id, coord in hass.data[DOMAIN].items():
            if hasattr(coord, 'curtains'):
                for curtain in coord.curtains:
                    if curtain.get("name") == entity.attributes.get("friendly_name"):
                        coordinator = coord
                        break
                if coordinator:
                    break

        if not coordinator:
            _LOGGER.error("找不到对应的协调器")
            return

        # 更新配置
        for curtain in coordinator.curtains:
            if curtain.get("name") == entity.attributes.get("friendly_name"):
                curtain.update({
                    "open_time": open_time,
                    "close_time": close_time,
                    "open_code": open_code,
                    "close_code": close_code,
                    "stop_code": stop_code,
                })
                break

        _LOGGER.info("已更新窗帘配置: %s", entity_id)

    async def test_rf_code(call: ServiceCall) -> None:
        """测试射频码."""
        entity_id = call.data["entity_id"]
        code = call.data["code"]
        code_type = call.data["code_type"]

        # 获取实体
        entity = hass.states.get(entity_id)
        if not entity:
            _LOGGER.error("找不到实体: %s", entity_id)
            return

        # 获取协调器
        coordinator = None
        for entry_id, coord in hass.data[DOMAIN].items():
            if hasattr(coord, 'curtains'):
                for curtain in coord.curtains:
                    if curtain.get("name") == entity.attributes.get("friendly_name"):
                        coordinator = coord
                        break
                if coordinator:
                    break

        if not coordinator:
            _LOGGER.error("找不到对应的协调器")
            return

        # 发送射频码
        success = await coordinator.async_send_rf_code(code)
        if success:
            _LOGGER.info("射频码发送成功: %s (%s)", code, code_type)
        else:
            _LOGGER.error("射频码发送失败: %s (%s)", code, code_type)

    async def set_position_manually(call: ServiceCall) -> None:
        """手动设置窗帘位置（用于手动操作后同步状态）."""
        entity_id = call.data["entity_id"]
        position = call.data["position"]

        _LOGGER.info("🔧 手动设置窗帘位置: %s -> %d%%", entity_id, position)

        # 获取实体对象
        component = hass.data.get(COVER_DOMAIN)
        if not component:
            _LOGGER.error("找不到cover组件")
            return

        entity = component.get_entity(entity_id)
        if not entity:
            _LOGGER.error("找不到实体: %s", entity_id)
            return

        # 更新位置
        if hasattr(entity, '_position'):
            old_position = entity._position
            entity._position = position
            entity._last_manual_update = datetime.now().isoformat()

            # 更新支持的功能
            if hasattr(entity, '_update_supported_features'):
                entity._update_supported_features()

            entity.async_write_ha_state()
            _LOGGER.info("✅ 已更新窗帘 %s 位置: %d%% -> %d%%", entity_id, old_position, position)
        else:
            _LOGGER.error("实体 %s 不支持位置设置", entity_id)

    # 注册服务
    hass.services.async_register(
        DOMAIN, "set_curtain_config", set_curtain_config, schema=SET_CURTAIN_CONFIG_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "test_rf_code", test_rf_code, schema=TEST_RF_CODE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "set_position_manually", set_position_manually, schema=SET_POSITION_SCHEMA
    )
