import os


BOT_TOKEN = os.getenv("TOKEN", 'default')

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", 'default')
REDIS_HOST = 'redis-10498.c55.eu-central-1-1.ec2.cloud.redislabs.com'
REDIS_PORT = 10498