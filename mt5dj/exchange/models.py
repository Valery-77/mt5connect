from django.db import models


class Exchange(models.Model):
    isApiKeyActive = models.BooleanField()
    connectExchange = models.BooleanField()
    commentary = models.CharField(max_length=20)

    def __str__(self):
        return self.commentary


class Quotes(models.Model):
    timestamp = models.DateTimeField(auto_now=True, null=True, blank=True)
    currencies = models.CharField(max_length=7, null=True, blank=True)
    close = models.FloatField(blank=True, null=True)
