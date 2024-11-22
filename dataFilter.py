import importlib
from typing import re
import re
import pandas as pd
from llm import LLM
import ast

class DataFilter:
    def __init__(self):
        self.llm = LLM()
        self.error_counter = 0

    def filterCodeGen(self,summary:dict,question:str,data:pd.DataFrame):
        sys_prompt = f"""
You are an experienced computer engineer and now your task is to generate the code which can filter the data according to the question and summary.
The original data contains many unuseful information and you just need to leave the line and column which will be used in the chart.
If the question needs the count, sum, average etc. the data, ALWAYS include these functions.
The dataset is stored in a variable whose type is pd.DataFrame and you should return a variable whose type is pd.DataFrame.
Just return the code and DO NOT include ANY explaination.
        """
        template = f"""
import pandas as pd
def filter(data:pd.DataFrame):
    <stub>  # only modify this section
    return data

data = filter(data)  # data already contains the data to be plotted. Always include this line. No additional code beyond this line.
# NO ADDITIONAL CODE IN THIS AREA
        """
        messages = []
        messages.append({"role":"system","content":sys_prompt})
        messages.append({"role":"system","content":f"The dataset summary is:{summary}"})
        messages.append({"role":"system","content":f"The template is given and you should modify the code according to the tip:\n{template}\n\nONLY modify the <stub> area!!"})
        messages.append({"role":"user","content":question})
        messages_copy = messages.copy()
        self.error_counter = 0
        while self.error_counter < 5 and self.error_counter >= 0:
            try:
                llm = LLM()
                response = llm.chat(messages)
                data1=self.executor(response,data)
                print("data1:\n",data1)
                return data1
            except:
                # print(self.error_counter)
                messages = messages_copy.copy()
                continue
            finally:
                return data1

    def executor(self,code:str,data):
        code_copy = code
        code = self.preprocess_code(code)
        # print("code",code)
        globals_dict = self.get_globals_dict(code,data)
        exec(code,globals_dict)
        data = globals_dict["data"]
        # print("data:",data)
        return data

    def preprocess_code(self,code: str) -> str:
        """Preprocess code to remove any preamble and explanation text"""

        code = code.replace("<imports>", "")
        code = code.replace("<stub>", "")
        code = code.replace("<transforms>", "")

        # remove all text after data = filter(data)
        if "data = filter(data)" in code:
            # print(code)
            index = code.find("data = filter(data)")
            if index != -1:
                code = code[: index + len("data = filter(data)")]

        if "```" in code:
            pattern = r"```(?:\w+\n)?([\s\S]+?)```"
            matches = re.findall(pattern, code)
            if matches:
                code = matches[0]
            # code = code.replace("```", "")
            # return code

        if "import" in code:
            # return only text after the first import statement
            index = code.find("import")
            if index != -1:
                code = code[index:]

        code = code.replace("```", "")
        return code
    def get_globals_dict(self,code_string, data):
        # Parse the code string into an AST
        tree = ast.parse(code_string)
        # Extract the names of the imported modules and their aliases
        imported_modules = []
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = importlib.import_module(alias.name)
                    imported_modules.append((alias.name, alias.asname, module))
            elif isinstance(node, ast.ImportFrom):
                module = importlib.import_module(node.module)
                for alias in node.names:
                    obj = getattr(module, alias.name)
                    imported_modules.append(
                        (f"{node.module}.{alias.name}", alias.asname, obj)
                    )

        # Import the required modules into a dictionary
        globals_dict = {}
        for module_name, alias, obj in imported_modules:
            if alias:
                globals_dict[alias] = obj
            else:
                globals_dict[module_name.split(".")[-1]] = obj

        ex_dicts = {"pd":pd,"data": data}
        globals_dict.update(ex_dicts)
        return globals_dict

if __name__ == '__main__':
    file_path = 'data/HollywoodsMostProfitableStories.csv'  # 根据你的文件路径调整
    data = pd.read_csv(file_path)
    datafilter = DataFilter()
    summary = { "dataset_name": "Hollywood's Most Profitable Stories", "dataset_description": "This dataset contains information about some of the most profitable Hollywood movies, including various factors such as profit, genre, and other related data.", "fields": [ { "field_name": "Film", "field_description": "This field represents the film of the movie or related data point.", "semantic_type": "category" }, { "field_name": "Genre", "field_description": "This field represents the genre of the movie or related data point.", "semantic_type": "category" }, { "field_name": "Lead Studio", "field_description": "This field represents the lead studio of the movie or related data point.", "semantic_type": "category" }, { "field_name": "Audience score %", "field_description": "This field represents the audience score % of the movie or related data point.", "semantic_type": "number" }, { "field_name": "Profitability", "field_description": "This field represents the profitability of the movie or related data point.", "semantic_type": "number" }, { "field_name": "Rotten Tomatoes %", "field_description": "This field represents the rotten tomatoes % of the movie or related data point.", "semantic_type": "number" }, { "field_name": "Worldwide Gross", "field_description": "This field represents the worldwide gross of the movie or related data point.", "semantic_type": "number" }, { "field_name": "Year", "field_description": "This field represents the year of the movie or related data point.", "semantic_type": "number" } ] }
    datafilter.filterCodeGen(summary,"Which year produced the highest grossing film?",data)