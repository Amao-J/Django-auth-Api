from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
import string
from datetime import timedelta
from django.utils.timezone import now

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if password is None:
            raise TypeError('Users must have a password.')
        if email is None:
            raise TypeError('Users must have an email.')

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.create_user(email, password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    email = models.EmailField(db_index=True, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    phone_number = PhoneNumberField(unique=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True) 
    

    USERNAME_FIELD = 'email'
    objects = UserManager()
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def generate_otp(self):
        self.otp = ''.join(random.choices(string.digits, k=6))
        self.otp_expiration = timezone.now() + timedelta(minutes=10)
        self.save()

    def verify_otp(self, otp):
        return self.otp == otp and self.otp_expiration > timezone.now()

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to="uploads", blank=False, null=False, default='/static/images/defaultuserimage.png')
    user_bio = models.CharField(max_length=600, blank=True)
    premium = models.BooleanField(default=False)
   
    def get_user_full_name(self):
        return self.user.get_full_name()

class FuelingStation(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    cooking_gas_price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    diesel_price_per_litre = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    petrol_price_per_litre = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sell_cooking_gas = models.BooleanField(default=False)
    sell_diesel = models.BooleanField(default=False)
    sell_petrol = models.BooleanField(default=False)
    last_updated = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

class Dashboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    station = models.ForeignKey(FuelingStation, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=[('Open', 'Open'), ('Closed', 'Closed')], default='Closed')
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.get_full_name()}'s Dashboard - {self.status} at {self.timestamp}"



@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


