"""Freebox Cover entity."""
import logging

from freebox_api import Freepybox
from voluptuous.validators import Number

from homeassistant.components.cover import (
    ATTR_POSITION,
    DEVICE_CLASS_SHUTTER,
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    SUPPORT_SET_POSITION,
    SUPPORT_STOP,
    CoverEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up the home devices."""
    router = hass.data[DOMAIN][entry.unique_id]

    home_devices = list(router.home_devices.values())
    async_add_entities(home_devices, True)


class FreeboxCover(CoverEntity):
    """Cover entity representation for Freebox."""

    label: str
    endpoint_id_position: Number
    endpoint_id_stop: Number
    position: Number
    node_id: Number

    def __init__(self, free_api: Freepybox, id: str) -> None:
        """Construct the freebox cover."""
        self.free_api = free_api
        self.id = id

    @property
    def name(self):
        """Name of the entity."""
        return self.label

    @property
    def unique_id(self) -> str:
        """Return the unique id base on the id returned by Somfy."""
        return self.id

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        supported_features = (
            SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_SET_POSITION | SUPPORT_STOP
        )
        return supported_features

    @property
    def is_opening(self) -> bool:
        """Return if the cover is opening or not."""
        return None

    @property
    def is_closing(self) -> bool:
        """Return if the cover is closing or not."""
        return None

    @property
    def is_closed(self) -> bool:
        """Return if the cover is closed or not."""
        return self.position == 100

    @property
    def device_class(self) -> str:
        """Return the class of the cover."""
        return DEVICE_CLASS_SHUTTER

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return True

    async def async_update(self):
        """Trigger for update entity state."""
        result = await self.free_api.home.get_home_endpoint_value(self.node_id, 4)
        self.position = result["value"]

    def open_cover(self, **kwargs):
        """Open the cover."""
        self.free_api.home.set_home_endpoint_value(
            self.node_id, self.endpoint_id_position, {"value": 0}
        )

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        await self.free_api.home.set_home_endpoint_value(
            self.node_id, self.endpoint_id_position, {"value": 0}
        )

    def close_cover(self, **kwargs):
        """Close cover."""
        self.free_api.home.set_home_endpoint_value(
            self.node_id, self.endpoint_id_position, {"value": 100}
        )

    async def async_close_cover(self, **kwargs):
        """Close cover."""
        await self.free_api.home.set_home_endpoint_value(
            self.node_id, self.endpoint_id_position, {"value": 100}
        )

    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        self.free_api.home.set_home_endpoint_value(
            self.node_id,
            self.endpoint_id_position,
            {"value": 100 - kwargs[ATTR_POSITION]},
        )

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        await self.free_api.home.set_home_endpoint_value(
            self.node_id,
            self.endpoint_id_position,
            {"value": 100 - kwargs[ATTR_POSITION]},
        )

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        self.free_api.home.set_home_endpoint_value(
            self.node_id, self.endpoint_id_stop, {}
        )

    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""
        await self.free_api.home.set_home_endpoint_value(
            self.node_id, self.endpoint_id_stop, {}
        )

    @property
    def current_cover_position(self):
        """Return the current position of cover shutter."""
        return 100 - self.position
