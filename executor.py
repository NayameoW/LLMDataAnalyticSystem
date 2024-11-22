import ast
import importlib
import os
import re
import traceback
from typing import Any, List

import matplotlib.pyplot as plt
import mpld3
import pandas as pd
import seaborn as sns
from lida.datamodel import ChartExecutorResponse, Summary
from llm import LLM

def preprocess_code(code: str) -> str:
    """Preprocess code to remove unnecessary parts and ensure it can generate a chart."""
    # Remove unnecessary parts
    code = re.sub(r"<imports>|<stub>|<transforms>", "", code)

    # Trim code to ensure it creates a chart
    if "chart = plot(data)" not in code:
        code += "\nchart = plot(data)"

    # Extract code within triple backticks
    # if "```" in code:
    #     matches = re.findall(r"```(?:\w+\n)?([\s\S]+?)```", code)
    #     if matches:
    #         code = matches[0]
    
    if match := re.search(r"```(?:python\s)?(.*?)```", code, re.DOTALL):
        return match.group(1).strip()
    
    return code.strip()

def get_globals_dict(code_string: str, data: Any) -> dict:
    """Extracts and returns a dictionary of global variables from the provided code string."""
    tree = ast.parse(code_string)
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
                imported_modules.append((f"{node.module}.{alias.name}", alias.asname, obj))

    globals_dict = {alias or module_name.split(".")[-1]: obj for module_name, alias, obj in imported_modules}
    globals_dict.update({"pd": pd, "data": data, "plt": plt})
    
    return globals_dict

class ChartExecutor:
    """Executes code and returns the generated chart object."""

    def __init__(self) -> None:
        self.max_retries = 5

    def execute(
        self,
        code_specs: List[str],
        data: Any,
        summary: dict,
        library="seaborn",
        return_error: bool = False,
    ) -> Any:
        """Execute the provided code specifications and return the generated chart."""
        if isinstance(summary, dict):
            summary = Summary(**summary)

        charts = []
        code_specs = [preprocess_code(code) for code in code_specs]

        # Data type conversion
        # for column in data.columns:
        #     data[column] = pd.to_numeric(data[column], errors='coerce')
        # data = data.dropna()  # Drop rows with NaN values after conversion
        
        # save the data to a csv file
        # data.to_csv("example_data.csv", index=False)

        for index, code in enumerate(code_specs):
            success = False
            error_counter = 0
            
            while error_counter < self.max_retries and not success:
                try:
                    local_vars = {'data': data}
                    exec(code, get_globals_dict(code, data), local_vars)
                    chart = local_vars.get("chart")

                    if chart is not None:
                        html_output = mpld3.fig_to_html(chart.gcf())
                        filename = f"chart_output_{index}.html"
                        with open(filename, "w") as file:
                            file.write(html_output)
                        print(f"HTML file saved as '{filename}'")
                        charts.append(chart)
                        success = True
                        return html_output
                    else:
                        print("Chart was not created.")
                        charts.append(None)

                except Exception as exception_error:
                    print("Code that caused the error:\n", code)
                    print("Error message:\n", str(exception_error))
                    error_counter += 1
                    if error_counter >= self.max_retries:
                        print("Maximum retries reached.")
                        if return_error:
                            charts.append(
                                ChartExecutorResponse(
                                    spec=None,
                                    status=False,
                                    raster=None,
                                    code=code,
                                    library=library,
                                    error={
                                        "message": str(exception_error),
                                        "traceback": traceback.format_exc(),
                                    },
                                )
                            )
                        break
        
    def get_corrected_code(self, prompt: str) -> str:
        """Use LLM to get a corrected version of the code that raised an exception."""
        llm = LLM()
        response = llm.chat(messages=[{"role": "user", "content": prompt}])
        return response['choices'][0]['message']['content']
