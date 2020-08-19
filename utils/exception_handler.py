# author:hao.lu
# create_date: 10/8/2019 1:33 PM
# file : exception_handler.py
# IDE: PyCharm

from rest_framework import status
from rest_framework.response import Response
# ! -*- coding: utf-8 -*-
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Call REST framework's default exception handler first,to get the standard error response.
    :param exc: exception message
    :param context:
    :return: json format example:{"code": "001", "message": "exception message"}
    """
    response = exception_handler(exc, context)
    fail_json = {"code": "001", "message": str(exc)}
    if response is not None:
        response.data = fail_json
    else:
        response = Response(fail_json, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return response
