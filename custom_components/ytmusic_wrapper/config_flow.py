"""Config flow for the Youtube Music Wrapper integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from ytmusic_wrapper import ytmusic_wrapper  # type: ignore[import]

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

logger = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT): str,
        vol.Required(CONF_NAME): str,
    }
)


async def validate_input(data: dict[str, Any]) -> dict[str, str]:
    """Validate the user input allows us to connect."""
    ytmusic_wrapper_api = ytmusic_wrapper(data[CONF_HOST], int(data[CONF_PORT]))
    # If the connection is successful, you can proceed with further API calls.
    try:
        await ytmusic_wrapper_api.async_setup()
        await ytmusic_wrapper_api.api_calls.get_song()
        await ytmusic_wrapper_api.async_close()
    except ConnectionError as exc:
        logger.error("Cannot connect to Youtube Music API: %s", exc)
        raise CannotConnect from exc
    except Exception as exc:
        logger.error("Invalid authentication or other error: %s", exc)
        raise InvalidAuth from exc
    # Return info that you want to store in the config entry.
    return {"host": data[CONF_HOST], "port": data[CONF_PORT], "name": data[CONF_NAME]}


class YoutubeMusicWrapperConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Youtube Music Wrapper."""

    VERSION = 1
    MINOR_VERSION = 1

    host: str
    port: str
    name: str

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            # If the user has provided an invalid port, show an error.
            if not user_input[CONF_PORT].isdigit():
                return self.async_show_form(
                    step_id="user",
                    data_schema=STEP_USER_DATA_SCHEMA,
                    errors={"port": "Port must be a number"},
                )

            self.host = user_input[CONF_HOST]
            self.port = user_input[CONF_PORT]
            self.name = user_input[CONF_NAME]
            try:
                info = await validate_input(user_input)
            except CannotConnect:
                return self.async_show_form(
                    step_id="user",
                    data_schema=STEP_USER_DATA_SCHEMA,
                    errors={"base": "cannot_connect"},
                )
            except InvalidAuth as exc:
                logger.error("Invalid authentication: %s", exc)
                return self.async_show_form(
                    step_id="user",
                    data_schema=STEP_USER_DATA_SCHEMA,
                    errors={"base": "invalid_auth"},
                )

            return self.async_create_entry(
                title=info["name"],
                data={
                    CONF_HOST: info["host"],
                    CONF_PORT: info["port"],
                    CONF_NAME: info["name"],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("host"): str,
                    vol.Required("port"): str,
                    vol.Required("name"): str,
                }
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate we cannot connect."""
