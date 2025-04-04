from django.db import models


class DiningPlace(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    photo_link = models.URLField(blank=True)
    address = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=255)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "dining_places"
        managed = False
