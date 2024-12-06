import json
import logging
from typing import Union
import pandas as pd
# from lida.utils import clean_code_snippet, read_dataframe
# from lida.datamodel import TextGenerationConfig
# from llmx import TextGenerator
from llm import LLM
import warnings
import re




class Summarizer():
    def __init__(self) -> None:
        self.summary = None

        self.system_prompt = """
        You are an experienced data analyst that can annotate datasets. Your instructions are as follows:
        i) ALWAYS generate the name of the dataset and the dataset_description
        ii) ALWAYS generate a field description.
        iii.) ALWAYS generate a semantic_type (a single word) for each field given its values e.g. company, city, number, supplier, location, gender, longitude, latitude, url, ip address, zip code, email, etc
        You must return an updated JSON dictionary without any preamble or explanation.
        """

        self.logger = logging.getLogger("lida")
    def check_type(self, dtype: str, value):
        """Cast value to right type to ensure it is JSON serializable"""
        if "float" in str(dtype):
            return float(value)
        elif "int" in str(dtype):
            return int(value)
        else:
            return value

    def get_column_properties(self, df: pd.DataFrame, n_samples: int = 3) -> list:
        """Get properties of each column in a pandas DataFrame"""
        properties_list = []
        for column in df.columns:
            dtype = df[column].dtype
            properties = {}
            if dtype in [int, float, complex]:
                properties["dtype"] = "number"
                properties["std"] = self.check_type(dtype, df[column].std())
                properties["min"] = self.check_type(dtype, df[column].min())
                properties["max"] = self.check_type(dtype, df[column].max())

            elif dtype == bool:
                properties["dtype"] = "boolean"
            elif dtype == object:
                # Check if the string column can be cast to a valid datetime
                try:
                    # warnings.simplefilter("ignore")
                    pd.to_datetime(df[column], errors='raise')
                    properties["dtype"] = "date"

                except:
                    # Check if the string column has a limited number of values
                    if df[column].nunique() / len(df[column]) < 0.5:
                        properties["dtype"] = "category"
                    else:
                        properties["dtype"] = "string"
            elif pd.api.types.is_categorical_dtype(df[column]):
                properties["dtype"] = "category"
            elif pd.api.types.is_datetime64_any_dtype(df[column]):
                properties["dtype"] = "date"
            else:
                properties["dtype"] = str(dtype)

            # add min max if dtype is date
            if properties["dtype"] == "date":
                try:
                    properties["min"] = df[column].min()
                    properties["max"] = df[column].max()
                except TypeError:
                    cast_date_col = pd.to_datetime(df[column], errors='coerce')
                    properties["min"] = cast_date_col.min()
                    properties["max"] = cast_date_col.max()
            # Add additional properties to the output dictionary
            nunique = df[column].nunique()
            if "samples" not in properties:
                non_null_values = df[column][df[column].notnull()].unique()
                n_samples = min(n_samples, len(non_null_values))
                samples = pd.Series(non_null_values).sample(n_samples, random_state=42).tolist()
                properties["samples"] = samples
            properties["num_unique_values"] = nunique
            properties["semantic_type"] = ""
            properties["description"] = ""
            properties_list.append({"column": column, "properties": properties})
        # print(properties_list)
        return properties_list


    def modify_json(self,json_string):
        if "```" in json_string:
            pattern = r"```(?:\w+\n)?([\s\S]+?)```"
            matches = re.findall(pattern, json_string)
            if matches:
                json_string = matches[0]

        json_string = json_string.replace("```json","")
        json_string = json_string.replace("```","")
        return json_string


    def enrich(self, base_summary: dict) -> dict:
        """Enrich the data summary with descriptions"""
        self.logger.info(f"Enriching the data summary with descriptions")

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "assistant", "content": f"""
        Annotate the dictionary below. Only return a JSON object.
        {base_summary}
        """},
        ]
        textgen = LLM()
        response = textgen.chat(messages)
        enriched_summary = base_summary
        try:
            json_string = self.modify_json(response)
            # print(json_string)
            enriched_summary = json.loads(json_string)
        except json.decoder.JSONDecodeError:
            error_msg = f"The model did not return a valid JSON object while attempting to generate an enriched data summary. Consider using a default summary or  a larger model with higher max token length. | {response.text[0]['content']}"
            self.logger.info(error_msg)
            # print(response.text[0]["content"])
            raise ValueError(error_msg + "" + response.usage)
        return enriched_summary

    def summarize(
            self, data: Union[pd.DataFrame, str],
            file_name="", n_samples: int = 3,
            summary_method: str = "llm") -> dict:
        """Summarize data from a pandas DataFrame or a file location"""

        # if data is a file path, read it into a pandas DataFrame, set file_name to the file name
        if isinstance(data, str):
            file_name = data.split("/")[-1]
            data = pd.read_csv(data)
        data_properties = self.get_column_properties(data, n_samples)

        # default single stage summary construction
        base_summary = {
            "name": file_name,
            "file_name": file_name,
            "dataset_description": "",
            "fields": data_properties,
        }


        if summary_method == "llm":
            # two stage summarization with llm enrichment
            data_summary = self.enrich(
                base_summary,
                )
        else:
            # no enrichment, only column names
            data_summary = {
                "name": file_name,
                "file_name": file_name,
                "dataset_description": ""
            }

        data_summary["field_names"] = data.columns.tolist()
        data_summary["file_name"] = file_name
        data_summary["row_example"] = data.sample(5,axis=0)
        # print(data_summary)
        return data_summary

if __name__ == '__main__':
    data = pd.read_csv("./HollywoodsMostProfitableStories.csv")
    summarizer = Summarizer()
    data_summary = summarizer.summarize(data)
