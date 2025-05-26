from utils.app_utils import resolve_path, get_font
from plugins.base_plugin.base_plugin import BasePlugin
import logging
from datetime import datetime, timedelta
import inflect

logger = logging.getLogger(__name__)

DEFAULT_PRIMARY_COLOR = "#000000"
DEFAULT_SECONDARY_COLOR = "#FFFFFF"

STYLES = [
    {
        "name": "Bold",
        "primary_color": "#2cb5b9",
        "secondary_color": "#FFFFFF",
        "icon": "styles/bold.png"
    }
]


class Countdown(BasePlugin):
    def generate_settings_template(self):
        template_params = super().generate_settings_template()
        template_params['style_settings'] = True
        template_params['countdown_styles'] = STYLES
        return template_params

    def generate_image(self, settings, device_config):
        primary_color = settings.get('primaryColor') or DEFAULT_PRIMARY_COLOR
        secondary_color = settings.get('secondaryColor') or DEFAULT_SECONDARY_COLOR

        logger.info(f"Primary color {primary_color}")

        target_date_setting = settings.get('targetDate', '')
        if not target_date_setting.strip():
            raise RuntimeError("Target Date is required")
        logger.info(f"Selected date {target_date_setting}")

        target_time_setting = settings.get('targetTime', '')
        if not target_time_setting.strip():
            raise RuntimeError("Target Date is required")
        logger.info(f"Selected date {target_time_setting}")

        title = settings.get("title")
        smallest_unit = int(settings.get("smallestUnit"))

        current_datetime = datetime.now()
        hour, minute = [int(x) for x in target_time_setting.split(':')]
        target_date = datetime.fromisoformat(target_date_setting).replace(hour=hour, minute=minute)

        # no timezones are ever configures, as we assume both target_date and current_datetime to be in the same timezone,
        # meaning that their offsets would cancel out anyways
        difference = target_date - current_datetime
        pretty_time_difference = Countdown.time_delta_in_units(difference, smallest_unit)

        image_template_params = {
            "content": pretty_time_difference['full_text'],
            "title"  : title,
            "plugin_settings": settings,
            "duration" : pretty_time_difference,
            "primary_color" : primary_color,
            "secondary_color": secondary_color
        }

        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]
        
        #image = self.render_image(dimensions, "countdown_text.html", "countdown_text.css", image_template_params)
        image = self.render_image(dimensions, "countdown_bold.html", "countdown_bold.css", image_template_params)

        return image
    
    @staticmethod
    def time_delta_in_units(timedelta, smallest_unit, lang=inflect.engine()):
        if not timedelta:
            timedelta = timedelta()
        seconds = int(timedelta.total_seconds())
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        units = {
                "days": days,
                "hours": hours if smallest_unit <= 1 * 60 * 60  else False,
                "minutes" : minutes if smallest_unit <= 1 * 60 else False,
                "seconds" : seconds if smallest_unit <= 1 else False
            }
        units["full_text"] = lang.join([f"{count} {lang.plural(lang.singular_noun(noun), count)}" for (noun, count) in units.items() if count])
        return units