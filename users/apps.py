from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    # add this
    def ready(self):
        import users.signals  # noqa


class MapsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "maps"
