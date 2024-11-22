from flask import Flask, jsonify, render_template
import pandas as pd
from summarize import Summarizer
from taskSeperator import TaskSeperator
from chartChosen import ChooseChart
from dataFilter import DataFilter
import json
from visualize import VizGenerator
from executor import ChartExecutor

summary=None
question1,question2,question3=None,None,None
chartType1,chartType2,chartType3=None,None,None
score1,score2,score3=None,None,None
# data1,data2,data3=None,None,None
html1,html2,html3=None,None,None
answer1,answer2,answer3=None,None,None

data = pd.read_csv("./data/HollywoodsMostProfitableStories.csv")

def process_b(data):
    s = Summarizer()
    ts = TaskSeperator()
    summary = s.summarize(data)
    tmp_summary = s.summarize(data, summary_method="default")
    question1, question2, question3 = ts.seperate("What are the changing trends in cinema from 2005 to 2011?",tmp_summary)
    return summary, question1, question2, question3

summary, question1, question2, question3=process_b(data)
print(question1,'\n')
print(question2,'\n')
print(question3,'\n')


chartchooser = ChooseChart()
chartType1,score1,library=chartchooser.chart_confidence(question1, summary, "seaborn")
# chartType2,score2,library=chartchooser.chart_confidence(question2, summary, "seaborn")
# chartType3,score3,library=chartchooser.chart_confidence(question3, summary, "seaborn")


# print(chartType1,score1)
# question1 = "How many Hollywood commedies released before 2010 are rated above 50 on Rotten Tomatoes?"
# summary={ "dataset_name": "Hollywood's Most Profitable Stories", "dataset_description": "This dataset contains information about some of the most profitable Hollywood movies, including various factors such as profit, genre, and other related data.", "fields": [ { "field_name": "Film", "field_description": "This field represents the film of the movie or related data point.", "semantic_type": "category" }, { "field_name": "Genre", "field_description": "This field represents the genre of the movie or related data point.", "semantic_type": "category" }, { "field_name": "Lead Studio", "field_description": "This field represents the lead studio of the movie or related data point.", "semantic_type": "category" }, { "field_name": "Audience score %", "field_description": "This field represents the audience score % of the movie or related data point.", "semantic_type": "number" }, { "field_name": "Profitability", "field_description": "This field represents the profitability of the movie or related data point.", "semantic_type": "number" }, { "field_name": "Rotten Tomatoes %", "field_description": "This field represents the rotten tomatoes % of the movie or related data point.", "semantic_type": "number" }, { "field_name": "Worldwide Gross", "field_description": "This field represents the worldwide gross of the movie or related data point.", "semantic_type": "number" }, { "field_name": "Year", "field_description": "This field represents the year of the movie or related data point.", "semantic_type": "number" } ] }
# data_filter=DataFilter()
# data1= data_filter.filterCodeGen(summary, question1, data)
# print("result_data\n",type(data1))
# print("result_data\n",data1)



vizgenerator = VizGenerator()
chartexecutor = ChartExecutor()
code1 = vizgenerator.generate(summary,chartType1,question1,library="seaborn")
# code2 = vizgenerator.generate(summary,chartType2,question2,library="seaborn")
# code3 = vizgenerator.generate(summary,chartType3,question3,library="seaborn")
code_specs1 = [code1]
# code_specs2 = [code2]
# code_specs3 = [code3]
html1=chartexecutor.execute(code_specs1,data,summary,library="seaborn")
# html2=chartexecutor.execute(code_specs2,data,summary,library="seaborn")
# html3=chartexecutor.execute(code_specs3,data,summary,library="seaborn")
print(html1)



