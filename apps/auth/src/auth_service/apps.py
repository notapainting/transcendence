from django.apps import AppConfig

class AuthServiceConfig(AppConfig):
    name = 'auth_service'

    def ready(self):
        import auth_service.signals
