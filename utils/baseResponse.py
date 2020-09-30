"""
https://github.com/caoqianming/django-vue-admin
"""
from rest_framework.renderers import JSONRenderer


class BaseResponse(object):
    """
    封装的返回信息类
    """

    def __init__(self):
        self.code = 200
        self.data = None
        self.msg = None

    @property
    def dict(self):
        return self.__dict__


class FitJSONRenderer(JSONRenderer):
    """
    自行封装的渲染器
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        如果使用这个render，
        普通的response将会被包装成：
            {"code":200,"data":"X","msg":"X"}
        这样的结果
        使用方法：
            - 全局
                REST_FRAMEWORK = {
                'DEFAULT_RENDERER_CLASSES': ('utils.response.FitJSONRenderer', ),
                }
            - 局部
                class UserCountView(APIView):
                    renderer_classes = [FitJSONRenderer]

        :param data: {"msg":"X"}
        :param accepted_media_type:
        :param renderer_context:
        :return: {"code":200,"data":"X","msg":"X"}
        """
        response_body = BaseResponse()
        response = renderer_context.get("response")
        response_body.code = response.status_code
        if response_body.code >= 400:  # 响应异常
            msg = data["detail"] if "detail" in data else data
            if isinstance(msg, dict):
                msg_list = []
                msg_dict ={}
                for k, v in msg.items():
                    if isinstance(v, list):
                        us_key_list = ["US"] * len(v)
                        cn_key_list = ["CN"] * len(v)
                        jp_key_list = ["JP"] * len(v)
                        temp = dict(zip(us_key_list, v))
                        temp = dict(zip(cn_key_list, v), **temp)
                        temp = dict(zip(jp_key_list, v), **temp)
                        msg_list.append(temp)
                    elif k in ["US","CN","JP"]:
                        msg_dict[k] = v
                    else:
                        msg_list.append(v)
                if len(msg_dict) > 0:
                    msg_list.append(msg_dict)
                response_body.msg = msg_list
            else:
                response_body.msg = [msg]
        else:
            response_body.data = data
        # renderer_context.get("response").status_code = 200  # 统一成200响应,用code区分
        return super(FitJSONRenderer, self).render(
            response_body.dict, accepted_media_type, renderer_context
        )
