from django.db import models

from unixtimestampfield.fields import UnixTimeStampField


class Block(models.Model):
    height = models.IntegerField(primary_key=True, verbose_name='Высота блока')
    hash = models.CharField(max_length=64, verbose_name='Хэш блока', unique=True)
    timestamp = UnixTimeStampField(verbose_name='Время блока')
    miner = models.CharField(max_length=64, verbose_name='Адрес майнера')
    transaction_count = models.IntegerField(verbose_name='Количество транзакций')

    def __str__(self):
        return self.hash

    class Meta:
        ordering = ('-height',)
