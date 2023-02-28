
bind = "127.0.0.1:5001"

workers = 2

worker_class = 'uvicorn.workers.UvicornWorker'

loglevel = 'debug'

accesslog = '/srv/fastapi-demo-url-shortener/access_log'

errorlog =  '/srv/fastapi-demo-url-shortener/error_log'

