"""Test the Automate Pulse Hub v2 config flow."""
from unittest.mock import Mock, patch

from homeassistant import config_entries, setup
from homeassistant.components.automate.const import DOMAIN


def mock_hub(testfunc=None):
    """Mock aiopulse2.Hub."""
    Hub = Mock()
    Hub.name = "Name of the device"

    async def hub_test():
        if testfunc:
            testfunc()

    Hub.test = hub_test

    return Hub


async def test_form(hass):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] is None

    with patch("aiopulse2.Hub", return_value=mock_hub()), patch(
        "homeassistant.components.automate.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.1.1.1",
            },
        )

    assert result2["type"] == "create_entry"
    assert result2["title"] == "Name of the device"
    assert result2["data"] == {
        "host": "1.1.1.1",
    }
    await hass.async_block_till_done()
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_cannot_connect(hass):
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    def raise_error():
        raise ConnectionRefusedError

    with patch("aiopulse2.Hub", return_value=mock_hub(raise_error)):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.1.1.1",
            },
        )

    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "cannot_connect"}
