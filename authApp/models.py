from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        PermissionsMixin,
                                        BaseUserManager)


class MyUserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, is_active,
                     **extra_fields):
        if not email:
            raise ValueError('email id must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_active=is_active,
                          is_superuser=is_superuser,
                          is_staff=is_staff,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=256, unique=True)
    userName = models.CharField(max_length=256, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    createdTime = models.DateTimeField(blank=True, null=True)
    updatedTime = models.DateTimeField(blank=True,null=True, auto_now=True)
    profilePicture = models.ImageField(blank=True, null=True)
    phoneNumber = models.CharField(max_length=10, null=True, blank=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = ('user')
        verbose_name_plural = ('users')

    def __str__(self):
        return self.email
