import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP_DIR = ['apps']

# upload
UPLOAD_IMAGE_FOLDER = os.path.join(BASE_DIR, 'media', 'images')
UPLOAD_AUDIO_FOLDER = os.path.join(BASE_DIR, 'media', 'audios')
UPLOAD_VIDEO_FOLDER = os.path.join(BASE_DIR, 'media', 'audios')

# logger
LOGGER_LEVEL = 'DEBUG'
LOGGER_FORMATTER = '%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s'
LOGGER_DIR = os.path.join(BASE_DIR, 'logs')
LOGGER_FILE = os.path.join(LOGGER_DIR, 'server.log')
LOGGER_FILE_WEBSOCKET = os.path.join(LOGGER_DIR, 'websocket.log')
LOGGER_FILE_CELERY = os.path.join(LOGGER_DIR, 'celery.log')

if __name__ == '__main__':
    print(BASE_DIR)