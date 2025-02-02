from django.db import models

# Create your models here.
class game_db(models.Model):
    user_name = models.CharField(max_length=100)
    user_score = models.IntegerField(default=0)
    bot_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.user_score} vs {self.bot_score}"