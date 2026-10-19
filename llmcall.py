from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

client = OpenAI()

response = client.chat.completions.create(
model="gpt-5-mini",
messages=[
{"role": "system", "content": "You are a helpful assistant."},
{"role": "user", "content": "What is the capital of France?"}
]
)
print(response.choices[0].message.content)