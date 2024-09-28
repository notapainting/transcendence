from django.apps import AppConfig

class AuthServiceConfig(AppConfig):
    name = 'chat'

    def ready(self):
        import chat.signals
