import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    Permission,
)
from django.db import models


# lets us explicitly set upload path and filename
def upload_to(instance, filename):
    return "users/{filename}".format(filename=filename)

# profil manger ,is have two function
class ProfilUserManager(BaseUserManager):
    # this function ,who can create simple user
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email address is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    # this function,who can create super user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# user model
class ProfilUser(AbstractBaseUser):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    adresse = models.CharField(max_length=50, null=True, blank=True)
    code_postal = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    status = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    objects = ProfilUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    # image relations
    image = models.ImageField(
        upload_to=upload_to,
        blank=True,
        null=True,
        default="user.jpg",
    )

    user_permissions = models.ManyToManyField(Permission, blank=True)
    groups = models.ManyToManyField(Group, blank=True)

    def get_group_permissions(self, obj=None):
        permissions = Permission.objects.filter(group__profiluser=self)
        return permissions.values_list("codename", flat=True).order_by()

    def get_all_permissions(self, obj=None):
        return self.user_permissions.all() | self.get_group_permissions(obj)

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def __str__(self):
        return self.email
    

class UserToken(models.Model):
    user = models.OneToOneField(ProfilUser, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=500)
    refresh_token = models.CharField(max_length=500)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
