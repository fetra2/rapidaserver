from django.db import models

# Create your models here.
class Envoi(models.Model):
    num_envoi = models.CharField(max_length=50, primary_key=True, db_column='numEnvoi')
    bureau_ori = models.CharField(max_length=50, db_column='bureauOri')
    bureau_exp = models.CharField(max_length=50, db_column='bureauExp')
    bureau_dest = models.CharField(max_length=50, db_column='bureauDest')
    bureau_pass = models.CharField(max_length=50, db_column='bureauPass')
    poids = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True, db_column='poids')

class User(models.Model):
    email = models.CharField(max_length=255, blank=True , null = True)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    roles = models.CharField(max_length=255, blank=True , null = True)

class TblBureau(models.Model):
    ncodique = models.IntegerField(primary_key=True, db_column='NCODIQUE')
    bureau = models.CharField(max_length=50, db_column='Nombureau')