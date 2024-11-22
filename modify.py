from llm import LLM
from template import ChartScaffold

class Modify:
    def __init__(self):
        self.template = ChartScaffold()

    def modify(self,msglist:str,question:str,library,dataset):
        task_prompt = f"""
You are a Python expert. Now I want you to modify the code according to user's feedback.
You should understand the feedback clearly and only modify the function "def plot(data:pd.DataFrame)" in the code.
Your answer should only include the code after correction and DO NOT contain ANY explaination.
Only modify the problems user provide and do not change other components.
        """
        question = f"""
        Please modify the code according to the feedback.
        context:{msglist}\n
        feedback:{question}
        """
        template = self.template.get_template("","",library)
        messages = [{"role":"system","content":task_prompt}]
        messages.append({"role":"system","content":f"template for your feedback:{template}"})
        messages.append({"role":"user","content":question})
        llm = LLM()
        response = llm.chat(messages)
        print(response)
        return response

if __name__ == '__main__':
    with open("./trytrytry/test1.py","r") as f:
        code = f.read()
    question = "第一张图要求支持刷选，并且第二张图只显示刷选选中部分的内容。"
    modify = Modify()
    modify.modify(code,question,"altair")
