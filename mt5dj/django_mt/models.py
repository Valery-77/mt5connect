from django.db import models


class LiederModel(models.Model):
    magic_number = models.IntegerField(default=7777777)
    email = models.CharField(max_length=255)
    login = models.IntegerField()
    password = models.CharField(max_length=255)
    server = models.CharField(max_length=255)
    terminal_path = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Лидер'
        verbose_name_plural = 'Лидер'

    def __str__(self):
        return str(self.email)


class InvestorModel(models.Model):
    lieder = models.ForeignKey(LiederModel, verbose_name='Лидер', on_delete=models.CASCADE, default=None)
    email = models.CharField(max_length=255)
    login = models.IntegerField()
    password = models.CharField(max_length=255)
    server = models.CharField(max_length=255)
    terminal_path = models.CharField(max_length=255)

    active_action = models.BooleanField(default=True)

    INIT_CHOICES = [
        ('Инвестор', 'Инвестор'),
        ('Админ', 'Админ'),
        ('Система', 'Система'),
    ]
    BOOL_CHOICES = [
        ('Да', 'Да'),
        ('Нет', 'Нет'),
    ]

    CALC_STOP_CHOICES = [
        ('Средства', 'Средства'),
        ('Проценты', 'Проценты'),
    ]

    CALC_MULT_CHOICES = [
        ('Средства', 'Средства'),
        ('Баланс', 'Баланс'),
    ]

    AFTER_STOP_CHOICES = [
        ('Закрыть', 'Закрыть'),
        ('Закрыть и отключить', 'Закрыть и отключить'),
    ]

    W_POSITION_CHOICES = [
        ('Закрыть', 'Закрыть'),
        ('Оставить', 'Оставить'),
    ]

    TRANSACTION_TYPE_CHOICES = [
        ('Все', 'Все'),
        ('Плюс', 'Плюс'),
        ('Минус', 'Минус'),
    ]

    investment_size = models.FloatField(verbose_name='Стартовый капитал', default=10000.0)

    transaction_plus = models.FloatField(verbose_name='Сделка в +', default=0.1)
    transaction_minus = models.FloatField(verbose_name='Сделка в -', default=-0.1)
    transaction_timeout = models.IntegerField(verbose_name='Время ожидания', default=1)   # ------------
    transaction_type = models.CharField(verbose_name='Спросить у инвестора',   # ------------
                                        max_length=100, default='Все', choices=TRANSACTION_TYPE_CHOICES)
    transaction_action = models.CharField(verbose_name='Возврат цены',   # ------------
                                          max_length=100, default='Да', choices=BOOL_CHOICES)

    initiator = models.CharField(verbose_name='Инициатор',   # ------------
                                 max_length=100, default='Инвестор', choices=INIT_CHOICES)
    disconnect = models.CharField(verbose_name='Отключиться',
                                  max_length=100, default='Да', choices=BOOL_CHOICES)
    w_positions = models.CharField(verbose_name='Открытые сделки',
                                   max_length=100, default='Закрыть', choices=W_POSITION_CHOICES)
    notify = models.CharField(verbose_name='Уведомления',   # ------------
                              max_length=100, default='Да', choices=BOOL_CHOICES)
    in_blacklist = models.CharField(verbose_name='Блеклист',
                                    max_length=100, default='Нет', choices=BOOL_CHOICES)
    after = models.CharField(verbose_name='Сопровождать сделки',
                             max_length=100, default='Да', choices=BOOL_CHOICES)

    multiplier_type = models.CharField(verbose_name='Множитель', max_length=100,
                                       default='Баланс', choices=CALC_MULT_CHOICES)
    volume_multiplier = models.FloatField(verbose_name='Значение множителя', default=1.0)
    change_multiplier = models.CharField(verbose_name='Изменение множителя',
                                         max_length=100, default='Да', choices=BOOL_CHOICES)

    stop_limit_type = models.CharField(verbose_name='Стоп-лосс', max_length=100,
                                       default='Проценты', choices=CALC_STOP_CHOICES)
    volume_stop_limit = models.FloatField(verbose_name='Значение стопа', default=20.0)
    stop_limit_after = models.CharField(verbose_name='Открытые сделки', max_length=100,
                                        default='Закрыть', choices=AFTER_STOP_CHOICES)

    class Meta:
        verbose_name = 'Инвестор'
        verbose_name_plural = 'Инвестор'

    def __str__(self):
        return str(self.email)
