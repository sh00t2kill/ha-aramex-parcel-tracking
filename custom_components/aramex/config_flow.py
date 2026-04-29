import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN, CONF_LABEL_NUMBER

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_LABEL_NUMBER): str,
    }
)


class AramexConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the Aramex config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            label = user_input[CONF_LABEL_NUMBER].strip().upper()
            await self.async_set_unique_id(label)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"Aramex {label}",
                data={CONF_LABEL_NUMBER: label},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
        )
