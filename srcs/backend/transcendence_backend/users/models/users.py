from curses.ascii import US
from typing                     import Any
from django.db                  import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils               import timezone

class UserManager(BaseUserManager):
    def create_user(self, username : str = None,
                    password : str = None,
                    email : str = None,
                    **extra_fields
                    ) -> Any:
        if not username:
            raise ValueError('The Username field must be set')
        if not password:
            raise ValueError('The Password field must be set')
        
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username : str = None,
                    password : str = None,
                    email : str = None,
                    **extra_fields
                    ) -> Any:
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        return self.create_user(username, password,email, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True, blank=False)
    email = models.EmailField(max_length=255, unique=True, blank=True)
    password = models.CharField(max_length=255, blank=False)
    avatar = models.CharField(max_length=255, null=True, blank=True)
    token = models.CharField(max_length=255, null=True, blank=True)
    otp_secret = models.CharField(max_length=255, null=True, blank=True)
    is_2fa_enabled = models.BooleanField(default=False)
    is_user_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    

    friends = models.ManyToManyField('self', related_name='friends', blank=True, symmetrical=True)
    blocked = models.ManyToManyField('self', related_name='blocked_me', blank=True, symmetrical=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_staff
    
    def get_friends(self, skip : int = 0, limit : int = 10) -> list["User"]:
        friends = self.friends.all()[skip:skip+limit]
        return [
            {
                "id": friend.id,
                "username": friend.username,
                "avatar": friend.avatar
            }
            for friend in friends
        ]
    
    def unfriend(self, friend_id : int) -> "User" :
        friend = User.objects.get(id=friend_id)
        if not self.friends.filter(id=friend_id).exists():
            raise Exception("You are not friends with this user")
        self.friends.remove(friend)
        friend.friends.remove(self)
        return friend
    
    def block(self, user_id : int) -> "User":
        user = User.objects.get(id=user_id)
        if not user:
            raise Exception("User not found")
        if user in self.friends.all():
            self.friends.remove(user)
        if user in self.blocked.all():
            raise Exception("User is already blocked")
        if user.blocked.filter(id=self.id).exists():
            raise Exception("User has already blocked you")
        if self.id == user.id:
            raise Exception("You cannot block yourself")
        self.blocked.add(user)
        return user
    
    def unblock(self, user_id : int) -> "User":
        user = User.objects.get(id=user_id)
        if not user:
            raise Exception("User not found")
        if user not in self.blocked.all():
            raise Exception("User is not blocked")
        if self.id == user.id:
            raise Exception("You cannot unblock yourself")
        self.blocked.remove(user)
        return user
    
    def get_blocked_users(self, skip : int = 0, limit : int = 10) -> list["User"]:
        blocked_users = self.blocked.all()[skip:skip+limit]
        return [{
            "id": user.id,
            "username": user.username,
            "avatar": user.avatar
        }
        for user in blocked_users]
        
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

def user_model_to_dict(user : "User") -> dict[str, Any]:
    if not user:
        return {}
    return {
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar
    }