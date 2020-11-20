"""
Celery configuration
각 네임스페이스마다 서로 다른 브로커와 백엔드 사용
"""

CELERY_BROKER_URL = 'amqp://root:dkrabbitmqaudio@127.0.0.1:5673'
CELERY_RESULT_BACKEND = 'redis://:dkredisaudio@127.0.0.1'
CELERY_ENABLE_UTC = True
CELERY_TASK_SERIALIZER = ''
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'Asia/Seoul'
CELERY_TASK_ROUTES = {  # 오작동 한 작업을 전용 대기열로 라우팅하는 설정
    'tasks.add': 'low-priority'
}


# PREPROCESS_BACKEND = 'redis://:dkredisaudio@127.0.0.1:6380/2'
PREPROCESS_BROKER_URL = 'amqp://django:dkrabbitmqaudio@127.0.0.1:5673'
PREPROCESS_RESULT_BACKEND = 'redis://:dkredisaudio@localhost:6380/3'
PREPROCESS_ENABLE_UTC = True
PREPROCESS_STORE_ERRORS_EVEN_IF_IGNORED = True
PREPROCESS_TASK_SERIALIZER = 'json'
PREPROCESS_RESULT_SERIALIZER = 'pickle'
PREPROCESS_ACCEPT_CONTENT = ['json', 'pickle']
PREPROCESS_TIMEZONE = 'Asia/Seoul'
PREPROCESS_MAX_CACHED_RESULTS = -1
PREPROCESS_TASK_ROUTES = {
    'tasks.add': 'low-priority'
}


SIMILARITY_BROKER_URL = 'amqp://django:dkrabbitmqaudio@127.0.0.1:5674'
SIMILARITY_RESULT_BACKEND = 'redis://:dkredisaudio@127.0.0.1:6381/1'
SIMILARITY_ENABLE_UTC = True
SIMILARITY_TASK_SERIALIZER = 'json'
SIMILARITY_RESULT_SERIALIZER = 'json'
SIMILARITY_ACCEPT_CONTENT = ['json']
SIMILARITY_TIMEZONE = 'Asia/Seoul'
SIMILARITY_TASK_ROUTES = {
    'tasks.add': 'low-priority'
}


AMPLITUDE_BROKER_URL = 'amqp://django:dkrabbitmqaudio@127.0.0.1:5675'
AMPLITUDE_RESULT_BACKEND = 'redis://:dkredisaudio@127.0.0.1:6381/3'
AMPLITUDE_ENABLE_UTC = True
AMPLITUDE_TASK_SERIALIZER = 'json'
AMPLITUDE_RESULT_SERIALIZER = 'json'
AMPLITUDE_ACCEPT_CONTENT = ['json']
AMPLITUDE_TIMEZONE = 'Asia/Seoul'
AMPLITUDE_TASK_ROUTES = {
    'tasks.add': 'low-priority'
}