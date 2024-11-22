from time import sleep
from typing import Dict

from openai import OpenAI

# from llmx import TextGenerator, TextGenerationConfig, TextGenerationResponse
from template import ChartScaffold
from llm import LLM

system_prompt = """
You are a helpful assistant highly skilled in writing PERFECT code for visualizations. 
Given some code template, you complete the template to generate a visualization given the dataset and the goal described. 
The code you write MUST FOLLOW VISUALIZATION BEST PRACTICES ie. meet the specified goal, apply the right transformation, use the right visualization type, use the right data encoding, and use the right aesthetics (e.g., ensure axis are legible).
The transformations you apply MUST be correct and the fields you use MUST be correct. 
The visualization CODE MUST BE CORRECT and MUST NOT CONTAIN ANY SYNTAX OR LOGIC ERRORS (e.g., it must consider the field types and use them correctly). 
You MUST first generate a brief plan for how you would solve the task e.g. what transformations you would apply e.g. if you need to construct a new column, what fields you would use, what visualization type you would use, what aesthetics you would use, etc. .
"""


class VizGenerator(object):
    """Generate visualizations from prompt"""

    def __init__(
        self
    ) -> None:

        self.scaffold = ChartScaffold()

    def llmAssistant(self, messages, data, system_prompt):
        client = OpenAI()
        
        assistant = client.beta.assistants.create(
            name="Code Generator",
            instructions=system_prompt,
            tools=[{"type": "code_interpreter"}],
            model="gpt-4-0125-preview"
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


    def generate(self, summary,visualization:str,question:str,library='altair'):
#         """You are a helpful assistant highly skilled in writing PERFECT code for visualizations. 
# Given some code template, you complete the template to generate a visualization given the dataset and the goal described. 
# The code you write MUST FOLLOW VISUALIZATION BEST PRACTICES ie. meet the specified goal, apply the right transformation, use the right visualization type, use the right data encoding, and use the right aesthetics (e.g., ensure axis are legible).
# The transformations you apply MUST be correct and the fields you use MUST be correct. 
# The visualization CODE MUST BE CORRECT and MUST NOT CONTAIN ANY SYNTAX OR LOGIC ERRORS (e.g., it must consider the field types and use them correctly). 
# You MUST first generate a brief plan for how you would solve the task e.g. what transformations you would apply e.g. if you need to construct a new column, what fields you would use, what visualization type you would use, what aesthetics you would use, etc.
# Generate visualization code given a summary and a goal"""
#         """You are a highly skilled assistant in writing PERFECT code for visualizations.
# Given a code template, you complete it to generate a visualization based on the dataset summary and the specified goal.
# The code you write MUST FOLLOW VISUALIZATION BEST PRACTICES, i.e., meet the specified goal, apply the right transformation, use the right visualization type, use the right data encoding, and use appropriate aesthetics (e.g., ensure axes are legible).
# The transformations MUST be correct, and the fields you use MUST exist in the dataset. If a specified field doesn't exist, handle it by providing a relevant error message or selecting an available field as an alternative.
# The visualization CODE MUST BE CORRECT and MUST NOT CONTAIN SYNTAX OR LOGIC ERRORS (e.g., it should consider the field types and use them correctly).
# You MUST first generate a brief plan for how you would solve the task (e.g., what transformations and aesthetics you would apply). Verify field names against the dataset summary to ensure they exist.

# Generate visualization code given a summary and a goal."""
        """"You are a highly skilled assistant specializing in writing flawless visualization code. Given a code template, complete it to generate a visualization based on the dataset summary and the specified goal.

Your code must follow these guidelines:

Function Naming: Ensure the plot function is consistently defined and referenced as plot in both the function definition and where it’s called at the end.

Code Structure: Return the completed code as a full Python script. Use triple backticks (```) around the entire code to ensure clarity.

Imports: Include all required imports at the start, specifically for seaborn, pandas, matplotlib.pyplot, and numpy.

Field Check: Before generating the plot, check if each required field (like "Audience score %", "Year", and "Lead Studio") exists in the dataset. If any field is missing, raise a ValueError with an error message listing the missing fields and do not generate any code with undefined fields.

Legend and Labels: Add a legend with distinct colors where appropriate, and rotate x-axis labels for readability.

Mean Calculations: Use numpy.mean() for all mean calculations to avoid standalone calls to mean.

Median Calculations: Use numpy.median() for all median calculations to avoid standalone calls to median.

Return Statement: The script should end with chart = plot(data), which calls the plot function without any additional code beyond this line.

Generate a full Python script based on the above template, with no extraneous explanations or placeholders."
"""

        library_template, library_instructions = self.scaffold.get_template(visualization,question, library)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"The dataset summary is : {summary} \n\n"},
            library_instructions,
            {"role": "user",
            #  "content":
            #  f"Always add a legend with various colors where appropriate. The visualization code MUST only use data fields that exist in the dataset (field_names) or fields that are transformations based on existing field_names). Only use variables that have been defined in the code or are in the dataset summary. You MUST return a FULL PYTHON PROGRAM ENCLOSED IN BACKTICKS ``` that starts with an import statement. DO NOT add any explanation. \n\n THE GENERATED CODE SOLUTION SHOULD BE CREATED BY MODIFYING THE SPECIFIED PARTS OF THE TEMPLATE BELOW \n\n {library_template} \n\n.The FINAL COMPLETED CODE BASED ON THE TEMPLATE above is ... \n\n"}]
             "content":
             f"Always add a legend with various colors where appropriate. The visualization code MUST only use data fields that exist in the dataset (field_names) or fields that are transformations based on existing field_names). Only use variables that have been defined in the code or are in the dataset summary. You MUST return a FULL PYTHON PROGRAM ENCLOSED IN BACKTICKS ``` that starts with an import statement. DO NOT add any explanation. \n\n THE GENERATED CODE SOLUTION SHOULD BE CREATED BY MODIFYING THE SPECIFIED PARTS OF THE TEMPLATE BELOW \n\n {library_template} \n\n.The FINAL COMPLETED CODE BASED ON THE TEMPLATE above is ... \n\n"}]

        llm = LLM()
        response = llm.chat(messages)

        try:
            with open("history/generateViz.txt","r") as f:
                history = eval(f.read())
        except:
            history = []
        history.append({"question":question,"library":library,"response":response})
        with open("history/generateViz.txt","w") as f:
            f.write(f"{history}")

        return response

    def generateWithAssistant(self,data,visualization:str,question:str,library):
        library_template, library_instructions = self.scaffold.get_template(visualization, question, library)
        user_prompt = f"""
                Always add a legend with various colors where appropriate. 
                The visualization code MUST only use data fields that exist in the dataset (field_names) or fields that are transformations based on existing field_names). 
                Only use variables that have been defined in the code or are in the dataset summary. 
                Be careful when handling time. Refer to the dataset to see how to handle and THINK TWICE before writing the code. Not all the data needs preprocessing!!!
                When filtering the data, THINK TWICE whether the string after "==" appears in the dataset or column names because what user says may not be consistent with the dataset.
                For example, for question "How many cities receive 'BEST CITY' each year", the data includes ["BC","WC"]. You should use "BC" instead of "BEST CITY"
                You MUST return a FULL PYTHON PROGRAM ENCLOSED IN BACKTICKS ``` that starts with an import statement. DO NOT add any explanation. \n\n THE GENERATED CODE SOLUTION SHOULD BE CREATED BY MODIFYING THE SPECIFIED PARTS OF THE TEMPLATE BELOW \n\n {library_template} \n\n.The FINAL COMPLETED CODE BASED ON THE TEMPLATE above is ... \n\n"""
        # data.to_csv("./data/visualizedata.csv")
        # data = "./data/visualizedata.csv"
        messages = [
            library_instructions,
            {"role":"user","content":user_prompt}
        ]
        response = self.llmAssistant(messages,data,system_prompt)
        print(response)
        return response



if __name__ == '__main__':
    import pandas as pd
    data = pd.read_csv("./data/IEEE VIS papers 1990-2022.csv")
    visualization = "bar"
    questions = ["How many papers received the 'Award' of 'Best Paper'  each year?", "How many papers received the 'Award' of 'Honorable Mention'  each year?"]
    question = f"Please use two charts to answer these two questions: {questions}"
    library = "altair"
    g = VizGenerator()
    g.generateWithAssistant(data,visualization,question,library)