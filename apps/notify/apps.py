from django.apps import AppConfig


class NotifyConfig(AppConfig):
    name = 'notify'
    verbose_name = "告警/日志"

    def ready(self):
        import notify.signals
