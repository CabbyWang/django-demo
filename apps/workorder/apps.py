from django.apps import AppConfig
# from django.db.models.signals import post_save


class WorkorderConfig(AppConfig):
    name = 'workorder'
    verbose_name = "工单/巡检"

    def ready(self):
        import workorder.signals
