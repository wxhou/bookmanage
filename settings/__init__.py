import os

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UPLOAD_IMAGE_FOLDER = os.path.join(basedir, 'media', 'images')
UPLOAD_AUDIO_FOLDER = os.path.join(basedir, 'media', 'audios')
UPLOAD_VIDEO_FOLDER = os.path.join(basedir, 'media', 'audios')

if __name__ == '__main__':
    print(basedir)