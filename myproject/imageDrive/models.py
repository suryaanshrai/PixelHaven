from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="imageDrive/static/imageDrive/images")

    def delete(self, *args, **kwargs):
       self.image.delete()
       super().delete(*args, **kwargs)