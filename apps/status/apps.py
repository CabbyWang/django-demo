from django.apps import AppConfig


class StatusConfig(AppConfig):
    name = 'status'
    verbose_name = "状态"

    def ready(self):
        import status.signals
