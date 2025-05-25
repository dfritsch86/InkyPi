from utils.app_utils import resolve_path, get_font
from plugins.base_plugin.base_plugin import BasePlugin
import logging
from datetime import datetime
import inflect

logger = logging.getLogger(__name__)
DEFAULT_TIMEZONE = "US/Eastern"


class Countdown(BasePlugin):
    def generate_settings_template(self):
        template_params = super().generate_settings_template()
        template_params['style_settings'] = True
        return template_params

    def generate_image(self, settings, device_config):
        target_date_setting = settings.get('targetDate', '')
        if not target_date_setting.strip():
            raise RuntimeError("Target Date is required")
        logger.info(f"Selected date {target_date_setting}")

        target_time_setting = settings.get('targetTime', '')
        if not target_time_setting.strip():
            raise RuntimeError("Target Date is required")
        logger.info(f"Selected date {target_time_setting}")

        title = settings.get("title")


        current_datetime = datetime.now()
        hour, minute = [int(x) for x in target_time_setting.split(':')]
        target_date = datetime.fromisoformat(target_date_setting).replace(hour=hour, minute=minute)

        # no timezones are ever configures, as we assume both target_date and current_datetime to be in the same timezone,
        # meaning that their offsets would cancel out anyways
        difference = str(target_date - current_datetime)
        pretty_time_difference = Countdown.pretty_time_delta(difference)

        image_template_params = {
            "content": difference,
            "title"  : title,
            "plugin_settings": settings
        }

        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]
        
        image = self.render_image(dimensions, "countdown_text.html", "countdown_text.css", image_template_params)

        return image
    
    @staticmethod
    def pretty_time_delta(timedelta, lang=inflect.engine()):
        if not timedelta:
            return f"0 seconds"
        seconds = int(timedelta.total_seconds())
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        measures = (
            (days, "day"),
            (hours, "hour"),
            (minutes, "minute"),
            (seconds, "second"),
        )
        return lang.join(
            [f"{count} {lang.plural(noun, count)}" for (count, noun) in measures if count]
        )
  