import inspect

import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

print(openai.__version__)

#print(inspect.getsource(client.responses.parse))