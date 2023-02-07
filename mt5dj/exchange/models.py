from django.db import models


class Exchange(models.Model):
    isApiKeyActive = models.BooleanField()
    connectExchange = models.BooleanField()
    commentary = models.CharField(max_length=20)

    def __str__(self):
        return self.commentary
