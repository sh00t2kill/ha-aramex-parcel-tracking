from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AramexCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AramexCoordinator = hass.data[DOMAIN][entry.entry_id]
    label = coordinator.label_number
    async_add_entities(
        [
            AramexServiceSensor(coordinator, label),
            AramexPickupSensor(coordinator, label),
            AramexDeliverySensor(coordinator, label),
            AramexETASensor(coordinator, label),
            AramexScansSensor(coordinator, label),
        ]
    )


class _AramexBaseSensor(CoordinatorEntity[AramexCoordinator], SensorEntity):
    """Base class shared by all Aramex sensors."""

    def __init__(
        self,
        coordinator: AramexCoordinator,
        label: str,
        key: str,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        self._label = label
        self._attr_name = f"Aramex {label} {name}"
        self._attr_unique_id = f"aramex_{label.lower()}_{key}"


class AramexServiceSensor(_AramexBaseSensor):
    """Delivery service type."""

    def __init__(self, coordinator: AramexCoordinator, label: str) -> None:
        super().__init__(coordinator, label, "service", "Service")
        self._attr_icon = "mdi:truck-delivery"

    @property
    def native_value(self) -> str | None:
        return (self.coordinator.data.get("DeliveryServiceType") or {}).get(
            "Description"
        )


class AramexPickupSensor(_AramexBaseSensor):
    """Pickup franchise location."""

    def __init__(self, coordinator: AramexCoordinator, label: str) -> None:
        super().__init__(coordinator, label, "pickup", "Pickup")
        self._attr_icon = "mdi:map-marker-up"

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.get("PickupFranchise")

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "franchise_code": self.coordinator.data.get("PickupFranchiseCode"),
        }


class AramexDeliverySensor(_AramexBaseSensor):
    """Delivery franchise location."""

    def __init__(self, coordinator: AramexCoordinator, label: str) -> None:
        super().__init__(coordinator, label, "delivery", "Delivery")
        self._attr_icon = "mdi:map-marker-check"

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.get("DeliveryFranchise")

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "franchise_code": self.coordinator.data.get("DeliveryFranchiseCode"),
        }


class AramexETASensor(_AramexBaseSensor):
    """Estimated delivery date."""

    def __init__(self, coordinator: AramexCoordinator, label: str) -> None:
        super().__init__(coordinator, label, "eta", "ETA")
        self._attr_icon = "mdi:calendar-clock"

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.get("DeliveryETADate")

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "transit_days": self.coordinator.data.get("TSSDeliveryDays"),
            "is_delayed": (self.coordinator.data.get("ServiceDelay") or {}).get(
                "IsDelayed"
            ),
            "delay_message": (self.coordinator.data.get("ServiceDelay") or {}).get(
                "Message"
            ),
        }


class AramexScansSensor(_AramexBaseSensor):
    """Most recent scan, with full scan history as attributes."""

    def __init__(self, coordinator: AramexCoordinator, label: str) -> None:
        super().__init__(coordinator, label, "scans", "Scans")
        self._attr_icon = "mdi:barcode-scan"

    @property
    def native_value(self) -> str | None:
        scans = self.coordinator.data.get("Scans") or []
        if not scans:
            return None
        return scans[-1].get("Description")

    @property
    def extra_state_attributes(self) -> dict:
        scans = self.coordinator.data.get("Scans") or []
        return {
            "last_scan_date": self.coordinator.data.get("LastScanDate"),
            "scans": [
                {
                    "date": s.get("Date"),
                    "location": f"{s.get('Name')} ({s.get('Franchise')})",
                    "description": s.get("Description"),
                    "status": s.get("StatusDescription"),
                }
                for s in scans
            ],
        }
