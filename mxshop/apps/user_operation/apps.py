from django.apps import AppConfig


class UserOperationConfig(AppConfig):
    name = 'user_operation'
    verbose_name = '用户操作管理'

    # 重载 ready方法，用来使用django的signals
    def ready(self):
        import user_operation.signals