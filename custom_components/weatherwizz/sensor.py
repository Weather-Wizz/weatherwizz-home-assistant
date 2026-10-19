"""WeatherWizz sensor entities."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WeatherWizzCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up WeatherWizz sensors."""
    coordinator: WeatherWizzCoordinator = hass.data[DOMAIN][entry.entry_id]
    known_entities: set[str] = set()

    def add_new_entities() -> None:
        entities = []
        stationdata = coordinator.data.get("stationdata", {}) if coordinator.data else {}
        for station_id, station in stationdata.items():
            data = station.get("data", {}) if isinstance(station, dict) else {}
            for sensor_key in data:
                unique_key = f"{station_id}:{sensor_key}"
                if unique_key in known_entities:
                    continue
                known_entities.add(unique_key)
                entities.append(
                    WeatherWizzSensor(coordinator, str(station_id), str(sensor_key))
                )
        if entities:
            async_add_entities(entities)

    add_new_entities()
    entry.async_on_unload(coordinator.async_add_listener(add_new_entities))


class WeatherWizzSensor(CoordinatorEntity[WeatherWizzCoordinator], SensorEntity):
    """A sensor reading supplied by WeatherWizz."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WeatherWizzCoordinator,
        station_id: str,
        sensor_key: str,
    ) -> None:
        super().__init__(coordinator)
        self._station_id = station_id
        self._sensor_key = sensor_key
        self._attr_unique_id = f"weatherwizz_{station_id}_{sensor_key}"

    @property
    def _station(self) -> dict[str, Any]:
        return (self.coordinator.data or {}).get("stationdata", {}).get(
            self._station_id, {}
        )

    @property
    def _metadata(self) -> dict[str, Any]:
        return self._station.get("sensor_metadata", {}).get(self._sensor_key, {})

    @property
    def name(self) -> str:
        return self._metadata.get("name", self._sensor_key.replace("_", " ").title())

    @property
    def native_value(self):
        return self._station.get("data", {}).get(self._sensor_key)

    @property
    def native_unit_of_measurement(self) -> str | None:
        return self._metadata.get("unit")

    @property
    def device_class(self) -> SensorDeviceClass | None:
        value = self._metadata.get("device_class")
        try:
            return SensorDeviceClass(value) if value else None
        except ValueError:
            return None

    @property
    def state_class(self) -> SensorStateClass | None:
        value = self._metadata.get("state_class")
        try:
            return SensorStateClass(value) if value else None
        except ValueError:
            return None

    @property
    def icon(self) -> str | None:
        return self._metadata.get("icon")

    @property
    def available(self) -> bool:
        return super().available and bool(self._station.get("available", False))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "station_id": self._station_id,
            "sensor_key": self._sensor_key,
            "last_updated": self._station.get("last_updated"),
        }

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._station_id)},
            name=self._station.get("stationname", self._station_id),
            manufacturer="WeatherWizz",
            model=self._station.get("stationtype", "Weather Station"),
        )
