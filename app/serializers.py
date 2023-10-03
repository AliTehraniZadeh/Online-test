from rest_framework import serializers
from . import models
import re


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserModel
        fields = '__all__'
        extera_kwargs = {'password':{'read_only': True},'is_staff':{'read_only': True},'is_active':{'read_only': True}} #غیرقابل دسترسی توسط کلاینت 


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QuestionModel
        fields = '__all__'


class AnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AnswersModel
        fields = '__all__'


class SendSMSTokenSerializer(serializers.Serializer):# customized serializers

    phone_number = serializers.CharField(min_length = 11, max_length = 11)

    def validate_phone_number(self, value): # اعتبارسنجی مقدار شماره موبایل validate method
        valide_phone_number = re.search('^09[0-9]{9}$', value)
        if not valide_phone_number:
            raise serializers.ValidationError('فرمت شماره تلفن اشتباه است')
        
        return value


class SMSTokenVerificationSerializer(serializers.Serializer):
    
    phone_number = serializers.CharField(min_length = 11, max_length=11)
    sms_token = serializers.CharField(min_length =5 , max_length =5)
    security_code = serializers.CharField(min_length= 10 , max_length= 10)

    def validate_phone_number(self, value): # اعتبارسنجی مقدار شماره موبایل validate method
        valide_phone_number = re.search('^09[0-9]{9}$', value)
        if not valide_phone_number:
            raise serializers.ValidationError('فرمت شماره تلفن اشتباه است')
        
        return value