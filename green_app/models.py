from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from PIL import Image as PILImage
import io
from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, MaxValueValidator

# ========================= Categories & SubCategories =====================
class Category(models.Model):
    image = models.ImageField(upload_to='categories/')
    name = models.CharField(unique=True, blank=False, max_length=30)

    def save(self, *args, **kwargs):
        if self.image:
            img = PILImage.open(self.image)
            fixed_width = 120
            fixed_height = 120
            img = img.resize((fixed_width, fixed_height), PILImage.LANCZOS)

            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                img = img.convert("RGB")
                
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG', quality=85)
            img_file = ContentFile(img_io.getvalue(), name=self.image.name)

            self.image.save(self.image.name, img_file, save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class SelectedCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.category.name if self.category else 'No Category Selected'

class Subcategory(models.Model):
    #image = models.ImageField(upload_to='subcategories/', null=True, blank=True)
    name = models.CharField(blank=False, max_length=30)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")

    def __str__(self):
        return self.name

# ==================== PRODUCTS =======================
class Color(models.Model):
    name = models.CharField(max_length=30)
    hex_code = ColorField()

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(unique=True, blank=False, max_length=30)
    width = models.SmallIntegerField(blank=False,null=True)
    height = models.SmallIntegerField(blank=False,null=True)
    description = models.CharField(blank=False, max_length=150)
    drainage=models.CharField( null=True,max_length=4,choices=[ ('Both', 'both'),('Yes', 'yes'),('No', 'no')])
    rating = models.FloatField(blank=True,null=True, default=5.0)
    
    def __str__(self):
        return self.name

# Linkage between Color, Price, and ProductInfo

class ProductInfo(models.Model):
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name="product_infos", null=True, blank=False)
    product = models.ForeignKey(Product, related_name='product_infos', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    price = models.PositiveBigIntegerField(blank=False)
    image = models.ImageField(upload_to='products/', null=True, blank=True, max_length=255)
    gloss = models.CharField(blank=False, null=True, max_length=20, choices=[('High', 'high'), ('Low', 'low')])
    inventory = models.PositiveIntegerField(blank=False, null=True, default=0)

    def save(self, *args, **kwargs):
        if self.image and not self.image._committed:
            img = PILImage.open(self.image)

            # Preserve original format
            original_format = img.format

            # Set the target size (width x height) to fit within these dimensions
            target_size = (400, 400)  # Adjust these dimensions as needed

            # Resize the image while maintaining the aspect ratio
            img.thumbnail(target_size, PILImage.LANCZOS)

            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                img = img.convert("RGB")

            img_io = io.BytesIO()
            img.save(img_io, format=original_format, quality=100)
            img_file = ContentFile(img_io.getvalue(), name=self.image.name)

            self.image.save(self.image.name, img_file, save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.color.name} (${self.price})"
#====================NEWEST ARRIVALS

class NewestArrivals(models.Model):
    product = models.ForeignKey(ProductInfo, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        if self.product:
            return self.product.product.name
        return "No product"
    
#=============================WISHLIST===================
class Items(models.Model):
    
    prodInfo=models.ForeignKey(ProductInfo,null=True,on_delete=models.CASCADE)
    color=models.CharField( max_length=30)
    drainage=models.CharField( null=True,max_length=3,choices=[ ('Yes', 'yes'),('No', 'no')])
    gloss=models.CharField(blank=False,null=True,max_length=20,choices=[ ('High', 'high'),('Low', 'low')])
    quantity=models.IntegerField(blank=True,null=True)
    def price(self):
        return self.prodInfo.price
    def __str__(self):
        return f"{self.prodInfo.product.name} - Color: {self.color}, Gloss: {self.gloss}, Drainage: {self.drainage}, Quantity: {self.quantity},Price: {self.prodInfo.price}"

class WishList(models.Model):
    items=models.ManyToManyField(Items)
    name = models.CharField(unique=False, blank=True, max_length=30)
    def __str__(self):
        return self.name
    

class Cart(models.Model):
    items=models.ManyToManyField(Items)
    name = models.CharField(unique=False, blank=False, max_length=30)
    def __str__(self):
        return self.name

# ==================== ACCOUNTS ============================
class Profile(models.Model):
    wishlist=models.ForeignKey(WishList,null=True,blank=True,on_delete=models.SET_NULL)
    cart=models.ForeignKey(Cart,null=True,blank=True,on_delete=models.SET_NULL)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=30, blank=False)
    address = models.CharField(max_length=90, blank=False)
    contact = models.CharField(max_length=11, help_text="03XXXXXXXXX", blank=False)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class orderDetails( models.Model):
    placedAt = models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20,choices=[ ('delivered', 'Delivered'),('inprogress', 'In Progress'),('incomplete','Incomplete')])
    gift=models.CharField(max_length=20,choices=[ ('yes','Yes'),('no','No')])
    profile=models.ForeignKey(Profile,on_delete=models.CASCADE,blank=True,null=True)
    grandTotal=models.PositiveIntegerField(null=True,default=0)
    paymentProof=models.ImageField(upload_to='payment/', null=True, blank=True,max_length=255)
    paymentMethod=models.CharField(null=True,max_length=6,choices=[('online','Online'),('COD','cod')])
    paymentStatus=models.CharField(null=True,max_length=7,choices=[("paid","Paid"),("Pending",'pending'),("COD","cod")])
    #this represents all items of this order
    orderItems=models.ForeignKey(Cart,on_delete=models.SET_NULL,null=True)
    def __str__(self):
        return self.profile.full_name
    
#===================REVIEWS========================

class Reviews(models.Model):
    ratings = models.FloatField(
        blank=False,null=False,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rate between 1 (lowest) to 5 (highest)"
    )
    description = models.CharField(max_length=300)
    products = models.ForeignKey('Product', on_delete=models.CASCADE)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='reviewimg/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.image:
            img = PILImage.open(self.image)

            # Preserve original format
            original_format = img.format or 'JPEG'

            # Set the target size (width x height) to fit within these dimensions
            target_size = (300, 300)  # Adjust these dimensions as needed

            # Resize the image while maintaining the aspect ratio
            img.thumbnail(target_size, PILImage.LANCZOS)

            # Convert to RGB if necessary
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                img = img.convert("RGB")

            img_io = io.BytesIO()
            img.save(img_io, format=original_format, quality=100)
            img_file = ContentFile(img_io.getvalue(), name=self.image.name)

            # Update the image field with the resized image
            self.image.save(self.image.name, img_file, save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.profile.full_name}'s review of {self.products.name}"
#================HOMEPAGE (EMAIL GIFT)=====================
class Subscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
class FishNChips(models.Model):
    shipping=models.PositiveIntegerField(null=True,default=500)
    giftwrap=models.PositiveIntegerField(null=True,default=100)
    paymentNumber = models.CharField(max_length=11, help_text="03XXXXXXXXX", blank=False,null=True)
    paymentName = models.CharField(max_length=40,  blank=False,null=True)
    
    accountNumber=  models.CharField(max_length=24, blank=False,null=True)
    accountName=  models.CharField(max_length=24, blank=False,null=True)