from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    CAT = (('Mobile', 1), ('Shoes',2), ('Clothes', 3))
    name = models.CharField(max_length = 50, verbose_name = 'Product Name')
    price = models.FloatField()
    pdetails = models.CharField(max_length = 50, verbose_name = "Product Details")
    cat = models.CharField(max_length = 50, verbose_name = "Category", choices = CAT)
    is_active = models.BooleanField(default = True)
    image = models.ImageField(upload_to = 'static/images')

    # def _str_(self):
    #     return self.name

class Cart(models.Model):
    user_id = models.ForeignKey('auth.User', on_delete = models.CASCADE, db_column = 'user_id')
    pid = models.ForeignKey('Product', on_delete = models.CASCADE, db_column = 'pid')
    qty = models.IntegerField(default = 1)

class Order(models.Model):
    order_id = models.CharField(max_length = 50)
    user_id = models.ForeignKey('auth.User', on_delete = models.CASCADE, db_column = 'user_id')
    pid = models.ForeignKey('Product', on_delete = models.CASCADE, db_column = 'pid')
    qty = models.IntegerField(default = 1)
    amt = models.FloatField()

class MyOrder(models.Model):
    order_id = models.CharField(max_length = 50)
    user_id = models.ForeignKey('auth.User', on_delete = models.CASCADE, db_column = 'user_id')
    pid = models.ForeignKey('Product', on_delete = models.CASCADE, db_column = 'pid')
    qty = models.IntegerField(default = 1)
    amt = models.FloatField()