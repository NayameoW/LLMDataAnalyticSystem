from summarize import Summarizer
from visualize import VizGenerator
from chartChosen import ChooseChart
from executor import ChartExecutor
from taskSeperator import TaskSeperator
from dataFilter import DataFilter
import pandas as pd
import plotly.express as px
import sqlite3

def getdata(table,database):
    conn = sqlite3.connect(f"D:\可视化\基于大模型的NLI\\nvBench-main\database\\{database}\\{database}.sqlite")
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table}')
    results = cursor.fetchall()

    columnDes = cursor.description  # 获取连接对象的描述信息
    cursor.close()
    conn.close()
    columnNames = [columnDes[i][0] for i in range(len(columnDes))]
    results = pd.DataFrame([list(i) for i in results], columns=columnNames)
    return results


if __name__ == '__main__':
  # data = pd.read_csv("data/iris.csv")
  # data = px.data.gapminder()   # gapminder data  ['country', 'continent', 'year', 'lifeExp', 'pop', 'gdpPercap', 'iso_alpha', 'iso_num']
  data = getdata("SECTION","college_2")
  print(data)
  summarizer = Summarizer()
  vizgenerator = VizGenerator()
  choosechart = ChooseChart()
  chartexecutor = ChartExecutor()
  taskseperator = TaskSeperator()
  datafilter = DataFilter()

  data_summary = summarizer.summarize(data,summary_method="llm")
  question = "trends in course numbers per year, grouped by semester in descending order."
  questions = eval(taskseperator.seperate(question,data_summary))
  # questions = [question]
  for question in questions:
    chartType = choosechart.chart_confidence(question,data_summary,library="pyecharts")
    code = vizgenerator.generate(data_summary,chartType,question,library="pyecharts")
    print(code)
    code_specs = [code]
    chartexecutor.execute(code_specs,data,data_summary,library="pyecharts")
    print(code)
  