broker_url='redis://127.0.0.1:6379/1'
result_backend='redis://127.0.0.1:6379/2'
timezone='Asia/Shanghai'
endable_utc = True
imports = (
    'app.api.auth.tasks',
    'app.api.book.tasks'
)
