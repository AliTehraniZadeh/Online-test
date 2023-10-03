from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
login_router = DefaultRouter()


router.register('user_api', views.UserView, basename='user_api')
router.register('question_api', views.QuestionView, basename='question_api')
router.register('answer_api', views.AnswersView, basename='answer_api')

login_router.register('send_sms_token_api', views.SendSMSTokenView, basename='send_sms_token_api')
login_router.register('sms_token_verification_api', views.SMSTokenVerificationView, basename='sms_token_verification_api')

urlpatterns = [
    path('api/',include(router.urls)),
    path('login/', include(login_router.urls))
]
