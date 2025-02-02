from constance.signals import config_updated
from django.dispatch import receiver
from main.settings import CONSTANCE_CONFIG

class Constance:
    @staticmethod
    @receiver(config_updated)
    def constance_updated(sender, key, old_value, new_value, **kwargs):
        CONSTANCE_CONFIG[key] = (new_value, str(old_value))