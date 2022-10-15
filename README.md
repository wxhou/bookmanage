# Flask图书管理系统开发示例


### 初始化数据库


首次初始化运行
```shell
flask db init -d app/migration
```

生成版本迁移脚本
```shell
flask db migrate -d app/migration
```

更新到数据库

```shell
flask db migrate -d app/migration
```

### 启动项目

```shell
python server.py
```

### 访问接口文档



### celery

启动celery

```shell
celery -A app.core.celery_app.celery worker -l info -P eventlet -c 1000
```
-C  并发量

### supervisorctl管理

```shell
[program:bookmanage]
command=/home/ubuntu/Documents/bookmanage/env/bin/gunicorn -w 1 -k eventlet -b 127.0.0.1:28100 server:app
directory=/home/ubuntu/Documents/bookmanage/
user=ubuntu
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
environment=BOOK_FLASK_ENV=development


[program:bookmanage_celery]
command=/home/ubuntu/Documents/bookmanage/env/bin/celery -A app.core.celery_app.celery worker -l info -P eventlet
directory=/home/ubuntu/Documents/bookmanage/
user=ubuntu
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
log_stdout=true
log_stderr=true
redirect_stderr=true
stdout_logfile_maxbytes=20MB ; stdout 日志文件大小，默认 50MB
stdout_logfile_backups=8 ; stdout 日志文件备份数
stdout_logfile=/home/ubuntu/Documents/bookmanage/logs/celery.log
```

### FlaskBabel文档

首先你必须进入到你的应用所在的文件夹中并且创建一个映射文件夹。对于典型的 Flask 应用，这是你要的:
```cfg
[python: **.py]
[jinja2: **/templates/**.html]
extensions=jinja2.ext.autoescape,jinja2.ext.with_
```
在你的应用中把它保存成 babel.cfg 或者其它类似的东东。接着是时候运行来自 Babel 中的 pybabel 命令来提取你的字符串:
```shell
$ pybabel extract -F babel.cfg -o messages.pot .
```
如果你使用了 lazy_gettext() 函数，你应该告诉 pybabel，这时候需要这样运行 pybabel:
```shell
$ pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .
```
这会使用 babel.cfg 文件中的映射并且在 messages.pot 里存储生成的模板。现在可以创建第一个翻译。例如使用这个命令可以翻译成中文:
```shell
$ pybabel init -i messages.pot -d app/translations -l zh_CN
```
-d translations 告诉 pybabel 存储翻译在这个文件夹中。这是 Flask-Babel 寻找翻译的地方。可以把它放在你的模板文件夹旁边。

现在如有必要编辑 translations/de/LC_MESSAGES/messages.po 文件。如果你感到困惑的话请参阅一些 gettext 教程。

为了能用需要编译翻译，pybabel 再次大显神通:
```shell
$ pybabel compile -d app/translations
```
如果字符串变化了怎么办？像上面一样创建一个新的 messages.pot 接着让 pybabel 整合这些变化:

```shell
$ pybabel update -i messages.pot -d app/translations
```
之后有些字符串可能会被标记成含糊不清。如果有含糊不清的字符串的时候，务必在编译之前手动地检查他们并且移除含糊不清的标志。