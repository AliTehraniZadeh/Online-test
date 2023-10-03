# from django.shortcuts import render
from rest_framework import viewsets, status
from . import serializers, models
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.utils import timezone
import random, string
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.response import Response


sms_api_key = ''

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return{
        'refresh' : str(refresh),
        'access' : str(refresh.access_token)
    }


class UserView(viewsets.ModelViewSet):
    queryset = models.UserModel.objects.all()
    serializer_class = serializers.UserSerializer


class QuestionView(viewsets.ModelViewSet):
    queryset = models.QuestionModel.objects.all()
    serializer_class = serializers.QuestionSerializer


class AnswersView(viewsets.ModelViewSet):
    queryset = models.AnswersModel.objects.all()
    serializer_class = serializers.AnswersSerializer


class SendSMSTokenView(viewsets.ViewSet): #ارسال کد تایید API
    serializer_class = serializers.SendSMSTokenSerializer # کلاس سریالایزری که روی آن عمل میکند
    permission_classes = [AllowAny]  # ایجاد سطح دسترسی

    def create(self, request):
        # سریالایز کردن داده های ورودی
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, created = models.UserModel.objects.get_or_create(phone_number = serializer.validated_data['phone_number']) # گرفتن یا ساختن آبجکت کاربر با توجه به شماره موبایل

        if created:
            user.firstname = 'کاربر'
            user.lastname = 'تست آنلاین '

        if user.sms_token_send_time != None :

            # اختلاف زمان بین زمان ساخت کد تایید و زمان الان
            time_diff = (timezone.localtime() - user.sms_token_send_time).total_seconds()

            # بررسی زمان ارسال پیامک قبلی که از  
            if (time_diff <= 120):
                # کد تایید پیامکی قبلی هنوز معتبر است و مجددا ساخته نخواهد شد
                return Response({'details': 'verification code is still valid', 'waiting_time': int(120-time_diff)}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # ساخت کد تایید 4 رقمی برای ارسال پیامک
        sms_token = str(random.randint(10000,99999))
        #  ساخت کد امنیتی برای کاربر که همزمان روی دوتا دیوایس کار نکند
        security_code = str(''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(10)))

        # try: #کد کاوه نگار پنل sms
        #     # پارامتر های ارسالی برای شرکت خدمات پیام
        #     PARAMS = {
        #         'receptor':user.phone_number, # شماره تلفن گیرنده
        #         'template':'talent-verify', # اسم تمپلیت ساخته شده در سایت
        #         'token':sms_token # کد تایید
        #         }
            
        #     # ارسال درخواست ارسال پیامک با پارامتر های بالا
        #     req = requests.post(url = f'https://api.kavenegar.com/v1/{sms_api_key}/verify/lookup.json', params = PARAMS)

        #     # بررسی ارسال شدن پیامک
        #     if req.status_code != 200:
        #         return Response({'details':'پیامک ارسال نشد. مشکل از سامانه ارسال پیامک است'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        # except :
        #     return Response({'details':'مشکلی در ارسال پیامک پیش آمده'}, status = status.HTTP_408_REQUEST_TIMEOUT)

        user.sms_token = sms_token # آپدیت کد تایید در آبجکت کاربر
        user.security_code = security_code # آپدیت کد امنیتی در آبجکت کاربر
        user.sms_token_send_time = timezone.localtime() # آپدیت زمان ارسال کد تایید در آبجکت کاربر
        user.phone_number_verified_at = timezone.localtime() # آپدیت زمان اعتبارسنجی شماره همراه در آبجکت کاربر

        user.save()


        return Response({'details':{'message':'کد تایید ارسال شد', 'security_code':security_code}}, status = status.HTTP_200_OK)

class SMSTokenVerificationView(viewsets.ViewSet):#        اعتبار سنجی کد تایید پیامکی
    serializer_class = serializers.SMSTokenVerificationSerializer # کلاس سریالایزری که روی آن عمل میکند
    permission_classes = [AllowAny]  # ایجاد سطح دسترسی

    def create(self, request):

        # سریالایز کردن داده های ورودی
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # گرفتن آبجکت کاربر با توجه به شماره موبایل و کد تایید پیامکی
        user = get_object_or_404(models.UserModel, phone_number = serializer.validated_data['phone_number'], sms_token = serializer.validated_data['sms_token'] , security_code = serializer.validated_data['security_code'])

        # بررسی منقضی شدن کد تایید بعد از 2 دقیقه
        if (timezone.localtime() - user.sms_token_send_time).total_seconds() > 120:
            # کد پیامکی دیگر معتبر نیست و باید پاک شود
            user.sms_token = None
            user.save()

            return Response({'details': 'sms token has expired. Please Login again'}, status=status.HTTP_400_BAD_REQUEST)

        user.last_login = timezone.localtime() # آپدیت مقدار آخرین لاگین
        user.phone_number_verified_at = timezone.localtime() # آپدیت مقدار زمان تایید شماره تلفن

        user.save()

        # ساخت پاسخ سرور
        response = Response()

        # ست کردن توکن jwt در کوکی
        data = get_tokens_for_user(user)


        response.data = {"details":{"message":"لاگین با موفقیت انجام شد", "user":serializers.SafeUserSerializer(user).data, "access_token":data["access"]}}
        
        return response