# author:hao.lu
# create_date: 9/22/2020 2:16 PM
# file : authentication.py
# IDE: PyCharm

from django.contrib.auth import get_user_model
# ! -*- coding: utf-8 -*-
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from utils.crypto_util import rsa_decode

UserModel = get_user_model()


class CustomBackend(ModelBackend):
    def authenticate(self, request, user_name=None, password=None, **kwargs):
        if user_name is None:
            user_name = kwargs.get(UserModel.USERNAME_FIELD)
        if user_name is None or password is None:
            return
        try:
            user = UserModel._default_manager.get(
                Q(user_name=user_name) | Q(phone=user_name) | Q(email=user_name)
            )
        except UserModel.DoesNotExist:

            return
        else:
            decode_password = rsa_decode(password)
            if user.check_password(decode_password) and self.user_can_authenticate(user):
                return user
