from django.db import models
from main.accounts.models import User
from main.places.models import DiningPlace


class FavouriteCarousel(models.Model):
    """Model for tracking user's favorite places"""
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    place_id = models.ForeignKey(
        DiningPlace,
        on_delete=models.CASCADE,
        to_field='id',
        db_column='place_id'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "favourite_carousel"
        unique_together = ('user_id', 'place_id')

    def __str__(self):
        return f"User {self.user_id} favorited place {self.place_id}"


class ShownCarousel(models.Model):
    """Model for tracking places shown to users and their interest level"""
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    place_id = models.ForeignKey(
        DiningPlace,
        on_delete=models.CASCADE,
        to_field='id',
        db_column='place_id'
    )
    is_interested = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "shown_carousel"
        unique_together = ('user_id', 'place_id')

    def __str__(self):
        interest = "interested in" if self.is_interested else "not interested in"
        return f"User {self.user_id} is {interest} place {self.place_id}"


class BlacklistCarousel(models.Model):
    """Model for tracking places that users have blacklisted (disliked)"""
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    place_id = models.ForeignKey(
        DiningPlace,
        on_delete=models.CASCADE,
        db_column='place_id'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "blacklist_carousel"
        unique_together = ('user_id', 'place_id')

    def __str__(self):
        return f"User {self.user_id} blacklisted place {self.place_id}"