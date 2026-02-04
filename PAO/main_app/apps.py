from django.apps import AppConfig


class MainAppConfig(AppConfig):
    name = 'main_app'

class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    # add this
    def ready(self):
        import users.signals  
