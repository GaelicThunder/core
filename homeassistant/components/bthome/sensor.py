"""Support for BTHome sensors."""
from __future__ import annotations

from typing import Optional, Union

from bthome_ble import SensorDeviceClass as BTHomeSensorDeviceClass, SensorUpdate, Units

from homeassistant import config_entries
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
    PassiveBluetoothDataUpdate,
    PassiveBluetoothProcessorCoordinator,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    ELECTRIC_POTENTIAL_VOLT,
    ENERGY_KILO_WATT_HOUR,
    LIGHT_LUX,
    MASS_KILOGRAMS,
    MASS_POUNDS,
    PERCENTAGE,
    POWER_WATT,
    PRESSURE_MBAR,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device import device_key_to_bluetooth_entity_key, sensor_device_info_to_hass

SENSOR_DESCRIPTIONS = {
    (BTHomeSensorDeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.TEMPERATURE}_{Units.TEMP_CELSIUS}",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (BTHomeSensorDeviceClass.HUMIDITY, Units.PERCENTAGE): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.HUMIDITY}_{Units.PERCENTAGE}",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (BTHomeSensorDeviceClass.ILLUMINANCE, Units.LIGHT_LUX): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.ILLUMINANCE}_{Units.LIGHT_LUX}",
        device_class=SensorDeviceClass.ILLUMINANCE,
        native_unit_of_measurement=LIGHT_LUX,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (BTHomeSensorDeviceClass.PRESSURE, Units.PRESSURE_MBAR): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.PRESSURE}_{Units.PRESSURE_MBAR}",
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=PRESSURE_MBAR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (BTHomeSensorDeviceClass.BATTERY, Units.PERCENTAGE): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.BATTERY}_{Units.PERCENTAGE}",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    (
        BTHomeSensorDeviceClass.VOLTAGE,
        Units.ELECTRIC_POTENTIAL_VOLT,
    ): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.VOLTAGE}_{Units.ELECTRIC_POTENTIAL_VOLT}",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (
        BTHomeSensorDeviceClass.ENERGY,
        Units.ENERGY_KILO_WATT_HOUR,
    ): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.ENERGY}_{Units.ENERGY_KILO_WATT_HOUR}",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    (BTHomeSensorDeviceClass.POWER, Units.POWER_WATT): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.POWER}_{Units.POWER_WATT}",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=POWER_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (
        BTHomeSensorDeviceClass.PM10,
        Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    ): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.PM10}_{Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER}",
        device_class=SensorDeviceClass.PM10,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (
        BTHomeSensorDeviceClass.PM25,
        Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    ): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.PM25}_{Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER}",
        device_class=SensorDeviceClass.PM25,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (
        BTHomeSensorDeviceClass.CO2,
        Units.CONCENTRATION_PARTS_PER_MILLION,
    ): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.CO2}_{Units.CONCENTRATION_PARTS_PER_MILLION}",
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (
        BTHomeSensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
        Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    ): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS}_{Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER}",
        device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (
        BTHomeSensorDeviceClass.SIGNAL_STRENGTH,
        Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    ): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.SIGNAL_STRENGTH}_{Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT}",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    # Used for mass sensor with kg unit
    (BTHomeSensorDeviceClass.MASS, Units.MASS_KILOGRAMS): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.MASS}_{Units.MASS_KILOGRAMS}",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=MASS_KILOGRAMS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Used for mass sensor with lb unit
    (BTHomeSensorDeviceClass.MASS, Units.MASS_POUNDS): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.MASS}_{Units.MASS_POUNDS}",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=MASS_POUNDS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Used for moisture sensor
    (BTHomeSensorDeviceClass.MOISTURE, Units.PERCENTAGE): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.MOISTURE}_{Units.PERCENTAGE}",
        device_class=SensorDeviceClass.MOISTURE,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Used for dew point sensor
    (BTHomeSensorDeviceClass.DEW_POINT, Units.TEMP_CELSIUS): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.DEW_POINT}_{Units.TEMP_CELSIUS}",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Used for count sensor
    (BTHomeSensorDeviceClass.COUNT, None): SensorEntityDescription(
        key=f"{BTHomeSensorDeviceClass.COUNT}",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
}


def sensor_update_to_bluetooth_data_update(
    sensor_update: SensorUpdate,
) -> PassiveBluetoothDataUpdate:
    """Convert a sensor update to a bluetooth data update."""
    return PassiveBluetoothDataUpdate(
        devices={
            device_id: sensor_device_info_to_hass(device_info)
            for device_id, device_info in sensor_update.devices.items()
        },
        entity_descriptions={
            device_key_to_bluetooth_entity_key(device_key): SENSOR_DESCRIPTIONS[
                (description.device_class, description.native_unit_of_measurement)
            ]
            for device_key, description in sensor_update.entity_descriptions.items()
            if description.device_class
        },
        entity_data={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.native_value
            for device_key, sensor_values in sensor_update.entity_values.items()
        },
        entity_names={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.name
            for device_key, sensor_values in sensor_update.entity_values.items()
        },
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BTHome BLE sensors."""
    coordinator: PassiveBluetoothProcessorCoordinator = hass.data[DOMAIN][
        entry.entry_id
    ]
    processor = PassiveBluetoothDataProcessor(sensor_update_to_bluetooth_data_update)
    entry.async_on_unload(
        processor.async_add_entities_listener(
            BTHomeBluetoothSensorEntity, async_add_entities
        )
    )
    entry.async_on_unload(coordinator.async_register_processor(processor))


class BTHomeBluetoothSensorEntity(
    PassiveBluetoothProcessorEntity[
        PassiveBluetoothDataProcessor[Optional[Union[float, int]]]
    ],
    SensorEntity,
):
    """Representation of a BTHome BLE sensor."""

    @property
    def native_value(self) -> int | float | None:
        """Return the native value."""
        return self.processor.entity_data.get(self.entity_key)
