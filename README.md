# django-admin-platform
django management system 

1、建表

```bash
python ../manage.py makemigrations system  #生成0001_initial.py文件
python ../manage.py sqlmigrate system 0001 #生成SQL
python ../manage.py migrate     #自动建表
```


