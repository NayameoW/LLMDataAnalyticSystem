from llm import LLM
import random

class TaskSeperator:

    def seperate(self,question:str,summary:dict):
        task_prompt = f"""
        You are an experienced data analyst. Now I want you to seperate a complex visualization question into three (must be 3!) visualization questions.(pay attention to VISUALIZATION QUESTION)
        Attention that the question in the list should be VISUALIZATION QUESTION, that means the question should be able to use visualization method to solve it.
        In the seperated question, you should explain the question clearly and NEVER use unclear word like this, these.
        Here I will give you an example.
        If I give you a complex question "In the months in which the temperatures are over 20, how much orders are there per month?", you can seperate the question into ["What months does the temperature rise above 20 degrees?","In the months in which the temperatures are over 20, how much orders are there per month?","..."]
        Only return a list like the one given in the example. DO NOT give ANY explanation.
        """
        question = f"""
        Please seperate the question into three (must be 3!) simple visualization question
        Try your best to use the same nouns as the column names in the data summary. 
        question:{question}
        """
        messages = [{"role":"system","content":task_prompt}]
        messages.append({"role":"system","content":f"the data summary is:{summary}\n\n"})
        messages.append({"role":"system","content":question})
        llm = LLM()
        responselist = []
        for _ in range(20):
            response = llm.chat(messages)
            count = 0
            try:
                if self.merge(response,summary) == "YES":
                    response = eval(response)[1]
                    response = [response]
                else:
                    response = eval(response)
                responselist.append(response)
                count += 1
            except:
                pass
            if count > 3:
                break
        # print(responselist)
        response = self.vote(responselist,question,summary)
        chosen = 0
        max_length = 0
        for i in range(len(response)):
            length = sum([len(sub_question) for sub_question in response[i]])
            if length > max_length:
                max_length = length
                chosen = i

        return response[chosen]

    def vote(self,responselist,question,summary):
        system_prompt = """
Here are a few ways to break down a visualization problem, so help me pick the best Three.
When you select the best question break down, follow these rules:
1. Use a voting mechanism to select the best question, which should have the same meaning as at least two questions in the question list.
2. You can change the questions in the question list, but the questions that are selected have different meanings.
3. In the question you pick, the nouns that appear in the question should be the same as the COLUMN NAMES or SAMPLES in the data.
For example: for question "How does the GDP change each year?", the column name is gdpPercap. You should change the question to: "How does the gdpPercap change each year?"
Another example: for question "How many cities receive 'BEST CITY' each year", the sample includes ["BC","WC"]. You should change the question to: "How many cities receive 'BC' each year"
Please return a list like the message user input. DO NOT contain ANY explaination.
        """
        messages = []
        messages.append({"role":"system","content":system_prompt})
        messages.append({"role":"system","content":f"The dataset summary is: {summary}"})
        messages.append({"role":"system","content":f"The original visulization question is :{question}"})
        messages.append({"role":"user","content":f"{responselist}"})
        llm = LLM()
        response = llm.chat(messages)
        return eval(response)


    def merge(self,questions,summary:dict):
        sys_prompt = f"""
Now I want you to judge if the two question have the same meaning or will generate similar chart based on the question list and data summary.
You should ONLY answer YES or NO and DO NOT GIVE ANY OTHER EXPLANATION!!
        """
        messages = []
        messages.append({"role":"system","content":sys_prompt})
        messages.append({"role":"system","content":f"The data summary is:{summary}"})
        messages.append({"role":"user","content":f"Please judge the questions:{questions}"})
        llm = LLM()
        response = llm.chat(messages)
        if response not in ["YES","NO"]:
            messages.append({"role":"user","content":"Please only answer YES or NO, do not contain any explanation."})
        response = llm.chat(messages)
        if response not in ["YES","NO"]:
            response = "NO"
        return response


if __name__ == '__main__':
    from summarize import Summarizer
    s = Summarizer()
    ts = TaskSeperator()
    import pandas as pd
    data = pd.read_csv("./HollywoodsMostProfitableStories.csv")
    summary = s.summarize(data,summary_method="default")
    breakdown = ts.seperate("How many Hollywood comedies released before 2010 are rated above 50 percent on Rotten Tomatoes or have an audience score larger than 60%?",summary)