from django.db import models
from django.contrib.auth.models import User, AbstractUser

# Create your models here.
class Envoi(models.Model):
    num_envoi = models.CharField(max_length=50, primary_key=True, db_column='numEnvoi')
    bureau_ori = models.CharField(max_length=50, db_column='bureauOri')
    bureau_exp = models.CharField(max_length=50, db_column='bureauExp')
    bureau_dest = models.CharField(max_length=50, db_column='bureauDest')
    bureau_pass = models.CharField(max_length=50, db_column='bureauPass')
    poids = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True, db_column='poids')

class TblBureau(models.Model):
    ncodique = models.IntegerField(primary_key=True, db_column='NCODIQUE')
    bureau = models.CharField(max_length=50, db_column='Nombureau')

class Personne(models.Model):
    idPers = models.IntegerField(primary_key=True, db_column='idPers')
    mail = models.CharField(max_length=50, db_column='mail')

#link user to company
class Company(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username
