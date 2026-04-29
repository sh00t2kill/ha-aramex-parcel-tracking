from __future__ import annotations

from datetime import date

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfTime
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
            AramexETADaysSensor(coordinator, label),
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
        self._attr_device_class = SensorDeviceClass.DATE

    @property
    def native_value(self) -> date | None:
        raw = self.coordinator.data.get("DeliveryETADate")
        if not raw:
            return None
        try:
            return date(int(raw[6:10]), int(raw[3:5]), int(raw[0:2]))
        except (ValueError, IndexError):
            return None

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


class AramexETADaysSensor(_AramexBaseSensor):
    """Number of days until (or since) the ETA. Negative means overdue."""

    def __init__(self, coordinator: AramexCoordinator, label: str) -> None:
        super().__init__(coordinator, label, "eta_days", "ETA Days")
        self._attr_icon = "mdi:calendar-arrow-right"
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTime.DAYS

    @property
    def native_value(self) -> int | None:
        raw = self.coordinator.data.get("DeliveryETADate")
        if not raw:
            return None
        try:
            eta = date(int(raw[6:10]), int(raw[3:5]), int(raw[0:2]))
        except (ValueError, IndexError):
            return None
        return (eta - date.today()).days


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
