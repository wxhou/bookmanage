import os
from core import create_app
from dotenv import load_dotenv

env_file = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(env_file):
    load_dotenv(env_file)

app = create_app()