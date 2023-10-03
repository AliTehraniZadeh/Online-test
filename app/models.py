from django.db import models
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractBaseUser
from django.core.validators import MaxLengthValidator, MinValueValidator, RegexValidator
from django.conf import settings
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self, phone_number, password=None):# واردکردن فیلدهای مورد نیاز برای ساخت کاربر
        user = self.model(phone_number = phone_number)# مدل منظور UserModel
        user.set_password(password) # هش و ذخیره کردن پسورد
        user.save(using=self._db)
        return user
    
    def create_superuser(self , phone_number , password):
        user = self.create_user(phone_number, password)
        user.is_superuser = True # کاربر ادمین است
        user.is_staff=True  # از کاربران پنل ادمین است
        user.set_password(password) # پسوورد کاربر را هش می کند
        user.save(using=self._db) # ذخیره سازی کاربر در دیتابیس
        return user
    

class UserModel(AbstractBaseUser, PermissionsMixin): #مدل کاربر اصلی جنگو

    first_name = models.CharField('First Name', max_length=30, null=True)
    last_name = models.CharField("Last Name", max_length=150,null=True)
    phone_number = models.CharField(max_length = 11 , unique = True ,validators=
        [RegexValidator(
            regex='^[0][9][0-9]*$',
            message='فرمت شماره موبایل رعایت نشده است',
            code='invalid_phone_number')
        ])
    phone_number_verified_at = models.DateTimeField(null = True) # زمان اعتبار سنجی شماره تلفن
    birthdate = models.DateField(null = True) # تاریخ تولد
    gender = models.BooleanField(default=1, null=True) # جنسیت
    sms_token = models.IntegerField(validators=[MinValueValidator(1000), MaxLengthValidator(4)], null = True) # پیامک تایید
    sms_token_send_time = models.DateTimeField(null = True) # زمان ارسال پیامک تایید
    security_code = models.CharField(max_length = 10, null = True) # کد امنیتی کاربر
    created_at = models.DateTimeField(auto_now_add=True) # زمان ساخته شدن کاربر
    updated_at = models.DateTimeField(auto_now=True) # زمان آپدیت شدن کاربر
    is_staff = models.BooleanField(default=False) # از کاربران پنل ادمین است؟
    is_active = models.BooleanField(default=True) # فعال بودن کاربر

    objects = UserManager() # کلاس منیجر یوزر را مشخص می کند
    
    USERNAME_FIELD = 'phone_number' # فیلد یوزرنیم کاربر را مشخص می کند
    REQUIRED_FIELDS = [] # فیلد های ضروری

    def get_full_name(self):
        return str(self.first_name) + '-' + str(self.last_name)

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return str(self.first_name) + '-' + str(self.last_name)  + ' : ' + str(self.phone_number)
    

class QuestionModel(models.Model):
    title = models.CharField(max_length=150)
    def __str__(self):
        return self.title
    

class AnswersModel(models.Model):
    title = models.CharField(max_length=150)
    question = models.ForeignKey(QuestionModel, related_name='answers', on_delete=models.CASCADE)#چک برای حذف و بهتر
    def __str__(self):
        return self.title