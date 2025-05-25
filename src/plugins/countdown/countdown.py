from utils.app_utils import resolve_path, get_font
from plugins.base_plugin.base_plugin import BasePlugin
import logging
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)
DEFAULT_TIMEZONE = "US/Eastern"


class Countdown(BasePlugin):
    def generate_settings_template(self):
        template_params = super().generate_settings_template()
        return template_params

    def generate_image(self, settings, device_config):
        target_date_setting = settings.get('targetDate')
        target_date = datetime.fromisoformat(target_date_setting)

        timezone_name = device_config.get_config("timezone") or DEFAULT_TIMEZONE
        tz = pytz.timezone(timezone_name)
        current_time = datetime.now(tz)

        difference = str(target_date - current_time)

        image_template_params = {
            "content": difference,
            "plugin_settings": settings
        }

        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]
        
        image = self.render_image(dimensions, "countdown_text.html", "countdown_text.css", image_template_params)

        return image
    
  