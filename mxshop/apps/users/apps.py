from django.apps import AppConfig



class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = '用户管理'
    
    # 重载 ready方法，用来使用django的signals
    def ready(self):
        import users.signals
