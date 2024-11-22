import pandas as pd
from pyecharts.charts import Bar
from pyecharts import options as opts


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
data1,data2,data3=None,None,None
answer1,answer2,answer3=None,None,None

data = pd.read_csv("./data/HollywoodsMostProfitableStories.csv")

def process_b(data):
    s = Summarizer()
    ts = TaskSeperator()
    summary = s.summarize(data)
    tmp_summary = s.summarize(data, summary_method="default")
    question1, question2, question3 = ts.seperate("How many Hollywood commedies released before 2010 are rated above 50 on Rotten Tomatoes?",tmp_summary)
    return summary, question1, question2, question3

summary, question1, question2, question3=process_b(data)

chartchooser = ChooseChart()
chartType1,score1,library=chartchooser.chart_confidence(question1, summary, "pyecharts")
print(chartType1,score1)

# question1 = "How many Hollywood commedies released before 2010 are rated above 50 on Rotten Tomatoes?"
# summary={ "dataset_name": "Hollywood's Most Profitable Stories", "dataset_description": "This dataset contains information about some of the most profitable Hollywood movies, including various factors such as profit, genre, and other related data.", "fields": [ { "field_name": "Film", "field_description": "This field represents the film of the movie or related data point.", "semantic_type": "category" }, { "field_name": "Genre", "field_description": "This field represents the genre of the movie or related data point.", "semantic_type": "category" }, { "field_name": "Lead Studio", "field_description": "This field represents the lead studio of the movie or related data point.", "semantic_type": "category" }, { "field_name": "Audience score %", "field_description": "This field represents the audience score % of the movie or related data point.", "semantic_type": "number" }, { "field_name": "Profitability", "field_description": "This field represents the profitability of the movie or related data point.", "semantic_type": "number" }, { "field_name": "Rotten Tomatoes %", "field_description": "This field represents the rotten tomatoes % of the movie or related data point.", "semantic_type": "number" }, { "field_name": "Worldwide Gross", "field_description": "This field represents the worldwide gross of the movie or related data point.", "semantic_type": "number" }, { "field_name": "Year", "field_description": "This field represents the year of the movie or related data point.", "semantic_type": "number" } ] }
data_filter=DataFilter()
data1= data_filter.filterCodeGen(summary, question1, data)

def plot(data:pd.DataFrame):
    # Filter the data for Comedy films released before 2010 with Rotten Tomatoes % above 50
    filtered_data = data[(data['Genre'] == 'Comedy') & (data['Year'] < 2010) & (data['Rotten Tomatoes %'] > 50)]

    # Count the number of films
    film_count = filtered_data.shape[0]

    # Prepare the bar chart
    chart = (
        Bar()
        .add_xaxis([f"Comedy Films (Count: {film_count})"])
        .add_yaxis("Number of Films", [film_count], itemstyle_opts=opts.ItemStyleOpts(color="blue"))
        .set_global_opts(title_opts=opts.TitleOpts(title="Comedy Films Released Before 2010 with Rotten Tomatoes % Above 50"),
                         legend_opts=opts.LegendOpts(is_show=True, pos_left="right"))
    )

    return chart.render_embed()  # return chart.render_embed() here to return html code

chart = plot(data)
print(chart)