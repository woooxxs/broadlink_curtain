"""博联窗帘控制实体."""
import asyncio
import logging
from typing import Any, Dict, Optional
from datetime import datetime

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    CONF_CURTAIN_CLOSE_CODE,
    CONF_CURTAIN_CLOSE_TIME,
    CONF_CURTAIN_MOVE_TIME,
    CONF_CURTAIN_NAME,
    CONF_CURTAIN_OPEN_CODE,
    CONF_CURTAIN_OPEN_TIME,
    CONF_CURTAIN_STOP_CODE,
    CURTAIN_STATE_CLOSED,
    CURTAIN_STATE_CLOSING,
    CURTAIN_STATE_OPEN,
    CURTAIN_STATE_OPENING,
    CURTAIN_STATE_STOPPED,
    DOMAIN,
)
from .coordinator import BroadlinkCurtainCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置博联窗帘实体."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for curtain_config in coordinator.curtains:
        entity = BroadlinkCurtainEntity(coordinator, curtain_config)
        entities.append(entity)
    
    async_add_entities(entities)


class BroadlinkCurtainEntity(CoordinatorEntity, CoverEntity, RestoreEntity):
    """博联窗帘实体."""

    def __init__(self, coordinator: BroadlinkCurtainCoordinator, config: Dict[str, Any]):
        """初始化窗帘实体."""
        super().__init__(coordinator)

        self._config = config
        self._name = config[CONF_CURTAIN_NAME]
        self._open_code = config[CONF_CURTAIN_OPEN_CODE]
        self._close_code = config[CONF_CURTAIN_CLOSE_CODE]
        self._stop_code = config[CONF_CURTAIN_STOP_CODE]

        # 使用统一的移动时间，如果没有则使用旧的配置
        self._move_time = config.get(CONF_CURTAIN_MOVE_TIME) or config.get(CONF_CURTAIN_OPEN_TIME, 30)
        self._open_time = self._move_time  # 兼容
        self._close_time = self._move_time  # 兼容

        # 状态变量
        self._position = 0  # 0-100，默认关闭
        self._current_state = CURTAIN_STATE_STOPPED
        self._target_position = None
        self._move_task = None
        self._last_manual_update = None  # 记录最后一次手动更新时间

        # 实体属性
        self._attr_name = self._name
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{self._name}"
        self._attr_device_class = CoverDeviceClass.CURTAIN  # 使用CURTAIN保持窗帘图标
        self._attr_icon = "mdi:curtains"  # 明确指定窗帘图标
        # 支持的功能会根据位置动态更新
        self._update_supported_features()

    def _update_supported_features(self) -> None:
        """根据当前位置更新支持的功能."""
        # 始终显示所有按钮：打开、关闭、停止、设置位置
        features = (
            CoverEntityFeature.OPEN |
            CoverEntityFeature.CLOSE |
            CoverEntityFeature.STOP |
            CoverEntityFeature.SET_POSITION
        )

        self._attr_supported_features = features
        _LOGGER.debug("🔧 窗帘 %s - 位置: %d%%, 所有按钮始终可用",
                     self._name, self._position)

    async def async_added_to_hass(self) -> None:
        """实体添加到Home Assistant时调用."""
        await super().async_added_to_hass()

        # 恢复之前的状态
        last_state = await self.async_get_last_state()
        if last_state is not None:
            # 恢复位置
            if last_state.attributes.get(ATTR_POSITION) is not None:
                self._position = last_state.attributes.get(ATTR_POSITION)
                _LOGGER.info("🔄 恢复窗帘 %s 的位置: %d%%", self._name, self._position)

            # 恢复最后更新时间
            if last_state.attributes.get("last_manual_update"):
                self._last_manual_update = last_state.attributes.get("last_manual_update")
                _LOGGER.info("🔄 恢复窗帘 %s 的最后更新时间: %s", self._name, self._last_manual_update)
        else:
            _LOGGER.info("🆕 窗帘 %s 首次初始化，位置设为 0%%", self._name)

        # 更新支持的功能
        self._update_supported_features()

    @property
    def current_cover_position(self) -> Optional[int]:
        """返回当前位置."""
        return self._position

    @property
    def target_cover_position(self) -> Optional[int]:
        """返回目标位置."""
        return self._target_position

    @property
    def is_opening(self) -> bool:
        """返回是否正在打开."""
        return self._current_state == CURTAIN_STATE_OPENING

    @property
    def is_closing(self) -> bool:
        """返回是否正在关闭."""
        return self._current_state == CURTAIN_STATE_CLOSING

    @property
    def is_closed(self) -> bool:
        """返回是否已关闭."""
        # 位置为0时返回True（已关闭）
        # 其他位置返回False（未关闭/部分打开/已打开）
        return self._position == 0

    @property
    def state(self) -> str:
        """返回窗帘状态，用于HomeKit等集成."""
        # HomeKit需要明确的state属性来判断窗帘状态
        # 这样可以避免一直显示loading状态
        if self._current_state == CURTAIN_STATE_OPENING:
            return "opening"
        elif self._current_state == CURTAIN_STATE_CLOSING:
            return "closing"
        elif self._position == 0:
            return "closed"
        elif self._position == 100:
            return "open"
        else:
            # 部分打开状态
            return "open"

    @property
    def available(self) -> bool:
        """返回实体是否可用."""
        # 窗帘实体始终可用
        return True

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """返回额外的状态属性."""
        attrs = {
            "current_position": self._position,
            "target_position": self._target_position,
            "current_state": self._current_state,
            "move_time": self._move_time,
        }

        if self._last_manual_update:
            attrs["last_manual_update"] = self._last_manual_update

        return attrs

    async def async_open_cover(self, **kwargs: Any) -> None:
        """打开窗帘."""
        await self.async_set_cover_position(position=100)

    async def async_close_cover(self, **kwargs: Any) -> None:
        """关闭窗帘."""
        await self.async_set_cover_position(position=0)

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """停止窗帘."""
        if self._move_task and not self._move_task.done():
            self._move_task.cancel()

        # 发送停止指令
        await self.coordinator.async_send_rf_code(self._stop_code)

        self._current_state = CURTAIN_STATE_STOPPED
        self._target_position = None
        self._update_supported_features()
        self.async_write_ha_state()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """设置窗帘位置."""
        position = kwargs.get(ATTR_POSITION)
        if position is None:
            return

        # 取消之前的移动任务
        if self._move_task and not self._move_task.done():
            self._move_task.cancel()

        # 计算移动方向和距离
        current_pos = self._position
        target_pos = position

        if target_pos == current_pos:
            return

        # 特殊处理：0%直接关闭，100%直接打开
        if target_pos == 0:
            _LOGGER.info("🎯 目标位置为0%，直接发送关闭指令")
            await self._async_direct_close()
            return
        elif target_pos == 100:
            _LOGGER.info("🎯 目标位置为100%，直接发送打开指令")
            await self._async_direct_open()
            return

        # 启动移动任务
        self._target_position = target_pos
        self._move_task = asyncio.create_task(
            self._async_move_to_position(target_pos)
        )

    async def _async_move_to_position(self, target_position: int) -> None:
        """移动到指定位置."""
        try:
            current_pos = self._position
            target_pos = target_position
            
            if target_pos > current_pos:
                # 需要打开
                await self._async_move_open(target_pos - current_pos)
            else:
                # 需要关闭
                await self._async_move_close(current_pos - target_pos)
                
        except asyncio.CancelledError:
            _LOGGER.debug("窗帘移动任务被取消")
        except Exception as ex:
            _LOGGER.error("窗帘移动失败: %s", ex)
            self._current_state = CURTAIN_STATE_STOPPED
            self.async_write_ha_state()

    async def _async_move_open(self, percentage: int) -> None:
        """打开指定百分比."""
        if percentage <= 0:
            _LOGGER.warning("窗帘 %s 打开百分比无效: %d%%", self._name, percentage)
            return

        # 计算移动时间，并加1秒补偿启动和停止延迟
        total_time = self._move_time
        move_time = (percentage / 100.0) * total_time + 1.0

        start_position = self._position
        target_position = min(100, self._position + percentage)

        _LOGGER.info("🔄 开始打开窗帘 %s", self._name)
        _LOGGER.info("   - 当前位置: %d%%", start_position)
        _LOGGER.info("   - 目标位置: %d%%", target_position)
        _LOGGER.info("   - 移动距离: %d%%", percentage)
        _LOGGER.info("   - 预计时间: %.1f 秒 (基础时间 + 1秒补偿)", move_time)
        _LOGGER.info("   - 开启射频码: %s", self._open_code)
        _LOGGER.info("   - 停止射频码: %s", self._stop_code)

        # 发送打开指令
        self._current_state = CURTAIN_STATE_OPENING
        self.async_write_ha_state()

        _LOGGER.info("📡 发送开启指令...")
        success = await self.coordinator.async_send_rf_code(self._open_code)
        if not success:
            _LOGGER.error("❌ 开启指令发送失败，停止操作")
            self._current_state = CURTAIN_STATE_STOPPED
            self.async_write_ha_state()
            return

        # 实时更新进度
        _LOGGER.info("⏱️ 开始移动，实时更新进度...")
        update_interval = 0.5  # 每0.5秒更新一次
        elapsed_time = 0.0

        while elapsed_time < move_time:
            await asyncio.sleep(update_interval)
            elapsed_time += update_interval

            # 计算当前预估位置
            progress = min(1.0, elapsed_time / move_time)
            estimated_position = int(start_position + (percentage * progress))
            self._position = min(100, estimated_position)

            # 更新状态
            self.async_write_ha_state()
            _LOGGER.debug("📊 窗帘 %s 打开进度: %d%% (%.1f秒/%.1f秒)",
                         self._name, self._position, elapsed_time, move_time)

        _LOGGER.info("🛑 发送停止指令...")
        # 发送停止指令
        await self.coordinator.async_send_rf_code(self._stop_code)

        # 更新最终位置
        old_position = start_position
        self._position = target_position
        self._current_state = CURTAIN_STATE_STOPPED
        self._target_position = None

        _LOGGER.info("✅ 窗帘 %s 打开完成", self._name)
        _LOGGER.info("   - 原位置: %d%%", old_position)
        _LOGGER.info("   - 新位置: %d%%", self._position)
        _LOGGER.info("   - 实际移动: %d%%", self._position - old_position)

        # 更新支持的功能并强制刷新状态（用于HomeKit同步）
        self._update_supported_features()
        self.async_write_ha_state()
        # 延迟再次更新，确保HomeKit能识别到状态变化
        await asyncio.sleep(0.5)
        self.async_write_ha_state()

    async def _async_move_close(self, percentage: int) -> None:
        """关闭指定百分比."""
        if percentage <= 0:
            _LOGGER.warning("窗帘 %s 关闭百分比无效: %d%%", self._name, percentage)
            return

        # 计算移动时间，并加1秒补偿启动和停止延迟
        total_time = self._move_time
        move_time = (percentage / 100.0) * total_time + 1.0

        start_position = self._position
        target_position = max(0, self._position - percentage)

        _LOGGER.info("🔄 开始关闭窗帘 %s", self._name)
        _LOGGER.info("   - 当前位置: %d%%", start_position)
        _LOGGER.info("   - 目标位置: %d%%", target_position)
        _LOGGER.info("   - 移动距离: %d%%", percentage)
        _LOGGER.info("   - 预计时间: %.1f 秒 (基础时间 + 1秒补偿)", move_time)
        _LOGGER.info("   - 关闭射频码: %s", self._close_code)
        _LOGGER.info("   - 停止射频码: %s", self._stop_code)

        # 发送关闭指令
        self._current_state = CURTAIN_STATE_CLOSING
        self.async_write_ha_state()

        _LOGGER.info("📡 发送关闭指令...")
        success = await self.coordinator.async_send_rf_code(self._close_code)
        if not success:
            _LOGGER.error("❌ 关闭指令发送失败，停止操作")
            self._current_state = CURTAIN_STATE_STOPPED
            self.async_write_ha_state()
            return

        # 实时更新进度
        _LOGGER.info("⏱️ 开始移动，实时更新进度...")
        update_interval = 0.5  # 每0.5秒更新一次
        elapsed_time = 0.0

        while elapsed_time < move_time:
            await asyncio.sleep(update_interval)
            elapsed_time += update_interval

            # 计算当前预估位置
            progress = min(1.0, elapsed_time / move_time)
            estimated_position = int(start_position - (percentage * progress))
            self._position = max(0, estimated_position)

            # 更新状态
            self.async_write_ha_state()
            _LOGGER.debug("📊 窗帘 %s 关闭进度: %d%% (%.1f秒/%.1f秒)",
                         self._name, self._position, elapsed_time, move_time)

        _LOGGER.info("🛑 发送停止指令...")
        # 发送停止指令
        await self.coordinator.async_send_rf_code(self._stop_code)

        # 更新最终位置
        old_position = start_position
        self._position = target_position
        self._current_state = CURTAIN_STATE_STOPPED
        self._target_position = None

        _LOGGER.info("✅ 窗帘 %s 关闭完成", self._name)
        _LOGGER.info("   - 原位置: %d%%", old_position)
        _LOGGER.info("   - 新位置: %d%%", self._position)
        _LOGGER.info("   - 实际移动: %d%%", old_position - self._position)

        # 更新支持的功能并强制刷新状态（用于HomeKit同步）
        self._update_supported_features()
        self.async_write_ha_state()
        # 延迟再次更新，确保HomeKit能识别到状态变化
        await asyncio.sleep(0.5)
        self.async_write_ha_state()

    async def _async_direct_open(self) -> None:
        """直接打开窗帘到100%，不发送停止指令."""
        _LOGGER.info("🔄 直接打开窗帘 %s 到100%", self._name)

        # 发送打开指令
        self._current_state = CURTAIN_STATE_OPENING
        self._target_position = 100
        self.async_write_ha_state()

        _LOGGER.info("📡 发送开启指令...")
        success = await self.coordinator.async_send_rf_code(self._open_code)
        if not success:
            _LOGGER.error("❌ 开启指令发送失败")
            self._current_state = CURTAIN_STATE_STOPPED
            self._target_position = None
            self.async_write_ha_state()
            return

        # 等待窗帘完全打开（使用配置的移动时间 + 1秒补偿）
        wait_time = self._move_time + 1
        _LOGGER.info("⏱️ 等待窗帘完全打开（%d秒 = 配置时间 + 1秒补偿）...", wait_time)
        await asyncio.sleep(wait_time)

        # 更新最终位置
        self._position = 100
        self._current_state = CURTAIN_STATE_STOPPED
        self._target_position = None

        _LOGGER.info("✅ 窗帘 %s 已完全打开", self._name)

        # 更新支持的功能并强制刷新状态（用于HomeKit同步）
        self._update_supported_features()
        self.async_write_ha_state()
        # 延迟再次更新，确保HomeKit能识别到状态变化
        await asyncio.sleep(0.5)
        self.async_write_ha_state()

    async def _async_direct_close(self) -> None:
        """直接关闭窗帘到0%，不发送停止指令."""
        _LOGGER.info("🔄 直接关闭窗帘 %s 到0%", self._name)

        # 发送关闭指令
        self._current_state = CURTAIN_STATE_CLOSING
        self._target_position = 0
        self.async_write_ha_state()

        _LOGGER.info("📡 发送关闭指令...")
        success = await self.coordinator.async_send_rf_code(self._close_code)
        if not success:
            _LOGGER.error("❌ 关闭指令发送失败")
            self._current_state = CURTAIN_STATE_STOPPED
            self._target_position = None
            self.async_write_ha_state()
            return

        # 等待窗帘完全关闭（使用配置的移动时间 + 1秒补偿）
        wait_time = self._move_time + 1
        _LOGGER.info("⏱️ 等待窗帘完全关闭（%d秒 = 配置时间 + 1秒补偿）...", wait_time)
        await asyncio.sleep(wait_time)

        # 更新最终位置
        self._position = 0
        self._current_state = CURTAIN_STATE_STOPPED
        self._target_position = None

        _LOGGER.info("✅ 窗帘 %s 已完全关闭", self._name)

        # 更新支持的功能并强制刷新状态（用于HomeKit同步）
        self._update_supported_features()
        self.async_write_ha_state()
        # 延迟再次更新，确保HomeKit能识别到状态变化
        await asyncio.sleep(0.5)
        self.async_write_ha_state()
