"""Support for Seitron Smart IoT climate devices (Wi-Time Wall, Wi-Time, Hygge)."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from pyseitron.seitron_gateway import SeitronGateway
from pyseitron.seitron_thermostat import SeitronThermostat

from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_TENTHS, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Seitron climate entities from a config entry."""
    coordinator: DataUpdateCoordinator[SeitronGateway] = hass.data[DOMAIN][
        entry.entry_id
    ]
    async_add_entities(
        SeitronClimate(coordinator, thermostat)
        for thermostat in coordinator.data.devices
    )


class SeitronClimate(
    CoordinatorEntity[DataUpdateCoordinator[SeitronGateway]], ClimateEntity
):
    """A Seitron IoT thermostat climate entity."""

    _enable_turn_on_off_backwards_compatibility = False
    _attr_precision = PRECISION_TENTHS
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.AUTO, HVACMode.COOL, HVACMode.OFF]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_max_temp = 35.0
    _attr_min_temp = 5.0
    _attr_target_temperature_high = 35.0
    _attr_target_temperature_low = 5.0
    _attr_target_temperature_step = 0.1
    _attr_icon = "mdi:thermostat-box"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[SeitronGateway],
        thermostat: SeitronThermostat,
    ) -> None:
        """Initialize a Seitron climate device."""
        super().__init__(coordinator)
        self._thermostat = thermostat
        self._attr_has_entity_name = True
        self._attr_name = None
        self._attr_unique_id = thermostat.gmac
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, thermostat.gmac)},
            manufacturer=thermostat.manufacturer,
            model=thermostat.model,
            name=thermostat.name,
            sw_version=thermostat.fw_ver,
        )

    @property
    def temperature_unit(self) -> str:
        """Return the temperature unit."""
        if self._thermostat.farhenheit:
            return UnitOfTemperature.FAHRENHEIT
        return UnitOfTemperature.CELSIUS

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._thermostat.temp_curr

    @property
    def target_temperature(self) -> float | None:
        """Return the setpoint."""
        return self._thermostat.temp_target

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation ie. auto, heat, cool, off."""
        raw_mode = (self._thermostat.mode or "").upper().strip()
        if raw_mode in ("COOL", "COOLING", "ESTATE"):
            return HVACMode.COOL
        if raw_mode in ("HEAT", "HEATING", "MANUAL", "MANUALE"):
            return HVACMode.HEAT
        if raw_mode in ("AUTO", "CRONO", "CRON", "PROGRAM", "PROGRAMMA"):
            return HVACMode.AUTO
        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction:
        """Return the current running hvac operation."""
        action = (self._thermostat.hvac_action or "").upper().strip()
        if action == "HEATING":
            return HVACAction.HEATING
        if action == "COOLING":
            return HVACAction.COOLING
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        return HVACAction.IDLE

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.COOL:
            mode_str = "COOL"
        elif hvac_mode == HVACMode.HEAT:
            mode_str = "HEAT"
        elif hvac_mode == HVACMode.AUTO:
            mode_str = "AUTO"
        else:
            mode_str = "OFF"

        # Optimistic local update to prevent UI flip
        self._thermostat.set_hvac_mode(mode_str)
        self.async_write_ha_state()

        await self.coordinator.data.set_hvac_mode(self._thermostat.gmac, mode_str)
        # Small delay to allow Seitron cloud backend state to synchronize
        await asyncio.sleep(1.0)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn thermostat on (defaults to AUTO schedule mode)."""
        await self.async_set_hvac_mode(HVACMode.AUTO)

    async def async_turn_off(self) -> None:
        """Turn thermostat off (antifreeze/defrost mode)."""
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (hvac_mode := kwargs.get(ATTR_HVAC_MODE)) is not None:
            await self.async_set_hvac_mode(hvac_mode)

        if (raw_temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        temp = round(float(raw_temp), 1)
        # Optimistic local update
        self._thermostat.set_temperature(temp)
        self.async_write_ha_state()

        await self.coordinator.data.set_temperature(self._thermostat.gmac, temp)
        # Small delay to allow Seitron cloud backend state to synchronize
        await asyncio.sleep(1.0)
        await self.coordinator.async_request_refresh()
