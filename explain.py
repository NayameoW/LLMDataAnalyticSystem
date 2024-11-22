import pandas as pd
from openai import OpenAI
import os
from time import sleep
os.environ["http_proxy"] = "http://127.0.0.1:7078"
os.environ["https_proxy"] = "http://127.0.0.1:7078"
from llm import LLM
llm = LLM()
class Explainer:
    def __init__(self):
        pass

    def llmAssistant(self,messages,file_path,system_prompt):
        print(1)
        client = OpenAI()
        file = client.files.create(
            file=open(file_path, "rb"),
            purpose='assistants'
        )
        assistant = client.beta.assistants.create(
            name="Code Explainer",
            instructions= system_prompt,
            tools=[{"type": "code_interpreter"}],
            model="gpt-4-1106-preview",
            file_ids=[file.id]
        )
        thread = client.beta.threads.create(
            messages=messages
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            # instructions="Please address the user as Jane Doe. The user has a premium account."
        )

        while run.status == "queued" or run.status == "in_progress":
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            sleep(5)
        messages = client.beta.threads.messages.list(
            thread_id=thread.id

        )
        return messages.data[0].content[0].text.value

    def explain(self,question:str,code:str,data:pd.DataFrame):
        system_prompt="""
        Now I want you to provide something that the visualization doesn't show based on the data and code.
        You should draw your conclusion based on ALL THE chart instead of just one chart.
        Your conclusion should be HARD TO BE NOTICED from the chart.
        First, answer the question according to the data and the question.
        Second, Use 1.2. ... to make an organized list of noteworthy points in the chart.
        Return MessageContent and do not contain any ImageFile.
        Your answer should be NO MORE THAN 100 WORDS and use Chinese to answer the quesiton.
        """
        prompt=f"""
The question is :{question}
The code is :{code}
        """
        data.to_csv("data/tempdata.csv")
        messages = [{"role":"user","content":prompt}]
        result = self.llmAssistant(messages,"data/tempdata.csv",system_prompt)
        print(result)
        return result

    def explainWithoutAssistant(self,code,question):
        system_prompt = """
You are an excellent data analyst and story teller. Now I want you to answer the question and describe the chart using about 150 words.
In your description, you should first include the answer to the question.
And then, you should include important data, trend and may guess the reason behind the data.
Your description should be NO MORE THAN 200 WORDS.
        """
        messages = []
        messages.append({"role":"system","content":system_prompt})
        messages.append({"role":"system","content":f"the html code of the chart is as follows:{code}"})
        messages.append({"role":"user","contnet":f"the question you should answer is as follows:{question}"})
        response = llm.chat(messages)
        return response

    def explainWithHTMLFile(self,htmlfile,question):
        system_prompt = """
        First, answer the question according to the html file.
        Second, Use 1.2. ... to make an organized list of noteworthy trends in the chart.
        Your answer should be NO MORE THAN 200 WORDS.
                """
        user_prompt = f"""
        The question is: {question}
        Answer the question first and list some noteworthy points.
        """
        messages = [{"role":"user","content":user_prompt}]
        result = self.llmAssistant(messages,htmlfile,system_prompt)
        print(result)
        return result

if __name__ == '__main__':
    import plotly.express as px
    data = pd.read_csv("./data/IEEE VIS papers 1990-2022.csv")
    html_file = "./trytrytry/render.html"
    explainer = Explainer()
    with open("./trytrytry/多视图联动.py") as f:
        code = f.read()
    # explainer.explainWithHTMLFile(html_file,"每年论文的数量和引用数量有什么变化趋势？")
    explainer.explain("请帮我分析最受欢迎的20篇文章",code,data)