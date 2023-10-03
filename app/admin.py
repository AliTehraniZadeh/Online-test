from django.contrib import admin
from .models import UserModel, QuestionModel, AnswersModel


admin.site.register(UserModel)
admin.site.register(QuestionModel)
admin.site.register(AnswersModel)