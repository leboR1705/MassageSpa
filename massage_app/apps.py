from django.apps import AppConfig


class MassageAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'massage_app'

    def ready(self):
        # register signal handlers
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
