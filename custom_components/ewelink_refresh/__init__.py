"""
eWeLink Power Meter Refresh Integration for Home Assistant.

Automatically refreshes eWeLink power meter devices by simulating the eWeLink app behavior.
"""
import logging
import asyncio
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.const import (
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
)

from .const import (
    DOMAIN,
    CONF_REGION,
    CONF_AUTO_DISCOVER,
    CONF_DEVICES,
    DEFAULT_SCAN_INTERVAL,
)
from .ewelink_api import EWeLinkRefreshAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS = []  # No platforms, solo servicio de actualización


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the eWeLink Refresh component from YAML (not supported)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up eWeLink Refresh from a config entry."""
    _LOGGER.info("Setting up eWeLink Refresh integration")
    
    hass.data.setdefault(DOMAIN, {})
    
    # Crear instancia de la API
    api = EWeLinkRefreshAPI(
        email=entry.data[CONF_EMAIL],
        password=entry.data[CONF_PASSWORD],
        region=entry.data.get(CONF_REGION, "eu"),
        hass=hass,
    )
    
    # Autenticar
    if not await hass.async_add_executor_job(api.login):
        _LOGGER.error("Failed to authenticate with eWeLink")
        return False
    
    # Auto-descubrir dispositivos si está habilitado
    devices = entry.data.get(CONF_DEVICES, [])
    if entry.data.get(CONF_AUTO_DISCOVER, False) and not devices:
        _LOGGER.info("Auto-discovering power meter devices...")
        devices = await hass.async_add_executor_job(api.detect_power_meters)
        _LOGGER.info(f"Found {len(devices)} power meter device(s)")
    
    api.devices = devices
    
    # Guardar en hass.data
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "devices": devices,
    }
    
    # Configurar actualización periódica
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    
    async def async_refresh(now=None):
        """Refresh all devices."""
        _LOGGER.debug("Refreshing eWeLink power meters")
        for device in devices:
            if not device.get("enabled", True):
                continue
            device_id = device.get("id")
            if not device_id:
                _LOGGER.warning("Skipping device without id: %s", device)
                continue
            await hass.async_add_executor_job(api.refresh_device, device_id)
    
    # Ejecutar al inicio
    await async_refresh()
    
    # Programar actualizaciones periódicas
    entry.async_on_unload(
        async_track_time_interval(
            hass,
            async_refresh,
            timedelta(seconds=scan_interval),
        )
    )
    
    # Registrar servicios
    async def handle_refresh_service(call):
        """Handle the refresh service call."""
        device_ids = call.data.get("device_ids", [])
        if not device_ids:
            # Refrescar todos
            await async_refresh()
        else:
            # Refrescar específicos
            for device_id in device_ids:
                if not device_id:
                    _LOGGER.warning("Skipping empty device id in service call")
                    continue
                await hass.async_add_executor_job(api.refresh_device, device_id)
    
    hass.services.async_register(
        DOMAIN,
        "refresh",
        handle_refresh_service,
    )
    
    _LOGGER.info(f"eWeLink Refresh integration setup complete. Monitoring {len(devices)} device(s)")
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading eWeLink Refresh integration")
    
    # Eliminar servicios
    hass.services.async_remove(DOMAIN, "refresh")
    
    # Limpiar datos
    hass.data[DOMAIN].pop(entry.entry_id)
    
    return True
