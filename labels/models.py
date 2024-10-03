from django.db import models


class CardLabel(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    series = models.CharField(max_length=100)
    series_set = models.CharField(max_length=100)
    variant = models.CharField(max_length=100)
    rarity = models.CharField(max_length=100)
    image = models.ImageField(upload_to="images/")

    def __str__(self):
        return (
            f"{self.number} - {self.name} - {self.series} -"
            f"{self.series_set} - {self.variant} - {self.rarity}"
        )


class Collection(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    labels = models.ManyToManyField(CardLabel)

    def __str__(self):
        return str(self.name)
