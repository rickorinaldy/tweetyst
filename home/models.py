from django.db import models
import uuid

# Create your models here.
class IsuTweet(models.Model):
    id_ref          = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=50)
    judul           = models.CharField(max_length=100)
    deskripsi       = models.TextField(blank=True)
    tanggal_buat    = models.DateField(auto_now_add=True)
    keyword         = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.judul} at {self.tanggal_buat}'
