from django.db    import models

class Purchase(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = 'purchases'


class MainCategory(models.Model):
    name        = models.URLField(max_length=45)
    purchase    = models.ForeignKey('Purchase', on_delete=models.CASCADE)

    class Meta:
        db_table = 'main_categories'


class SubCategory(models.Model):
    name          = models.URLField(max_length=45)
    main_category = models.ForeignKey('MainCategory', on_delete=models.CASCADE)

    class Meta:
        db_table = 'sub_categories'


class Product(models.Model):
    name         = models.CharField(max_length=50)
    price        = models.DecimalField(decimal_places=2, max_digits=8)
    description  = models.TextField() 
    thumbnail    = models.URLField(max_length=1000)
    sub_category = models.ForeignKey('SubCategory', on_delete=models.CASCADE)
    options      = models.ManyToManyField('Option', through='ProductOption')

    class Meta:
        db_table = 'products'


class ProductImage(models.Model):
    image_url = models.URLField(max_length=1000)
    product   = models.ForeignKey('Product', on_delete=models.CASCADE)

    class Meta:
        db_table = 'product_images'


class Option(models.Model):
    name  = models.CharField(max_length=50)
    price = models.DecimalField(decimal_places=2, max_digits=8)

    class Meta:
        db_table = 'options'


class ProductOption(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    option  = models.ForeignKey('Option',  on_delete=models.CASCADE)

    class Meta:
        db_table = 'product_options'