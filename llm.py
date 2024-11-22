from openai import OpenAI
import os

available_models = {"ChatGPT-4": "gpt-4-1106-preview", "ChatGPT-3.5": "gpt-3.5-turbo-1106", "GPT-3": "text-davinci-003", }
my_key = ""

# openai.api_key = my_key
# os.environ["http_proxy"] = "http://127.0.0.1:7078"
# os.environ["https_proxy"] = "http://127.0.0.1:7078"
class LLM:
  def __init__(self):
    pass

  def chat(self,messages:list):
    client = OpenAI(api_key=my_key)
    response = client.chat.completions.create(
      # model=available_models["ChatGPT-4"],
      model="gpt-4o-mini",
      messages=messages)
    return response.choices[0].message.content

