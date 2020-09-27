from django.apps import apps


def get_child_queryset_u(check_queryset, obj, has_parent=True):
    """
    获取所有子集
    查的范围checkQueryset
    父obj
    是否包含父默认True
    """
    cls = type(obj)
    queryset = cls.objects.none()
    father_queryset = cls.objects.filter(pk=obj.id, is_deleted=False)
    if has_parent:
        queryset = queryset | father_queryset
    child_queryset = check_queryset.filter(pid=obj, is_deleted=False)
    while child_queryset:
        queryset = queryset | child_queryset
        child_queryset = check_queryset.filter(pid__in=child_queryset, is_deleted=False)
    return queryset


def get_child_queryset(name, pk, has_parent=True):
    """
    获取所有子集
    app.model名称
    Id
    是否包含父默认True
    """
    app, model = name.split(".")
    cls = apps.get_model(app, model)
    queryset = cls.objects.none()
    father_queryset = cls.objects.filter(pk=pk, is_deleted=False)
    if father_queryset.exists():
        if has_parent:
            queryset = queryset | father_queryset
        child_queryset = cls.objects.filter(
            pid=father_queryset.first(), is_deleted=False
        )
        while child_queryset:
            queryset = queryset | child_queryset
            child_queryset = cls.objects.filter(
                pid__in=child_queryset, is_deleted=False
            )
    return queryset


def get_child_queryset2(obj, has_parent=True):
    """
    获取所有子集
    obj实例
    数据表需包含parent字段
    是否包含父默认True
    """
    cls = type(obj)
    queryset = cls.objects.none()
    father_query_set = cls.objects.filter(pk=obj.dept_id, is_deleted=False)
    if has_parent:
        queryset = queryset | father_query_set
    child_queryset = cls.objects.filter(pid=obj.dept_id, is_deleted=False)
    while child_queryset:
        queryset = queryset | child_queryset
        child_queryset = cls.objects.filter(pid__in=child_queryset, is_deleted=False)
    return queryset
