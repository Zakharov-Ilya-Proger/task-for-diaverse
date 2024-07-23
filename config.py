import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

connection = create_engine(os.getenv("URL").replace("%40", "@"))

