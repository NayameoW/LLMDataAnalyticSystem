from summarize import Summarizer
from visualize import VizGenerator
from chartChosen import ChooseChart
from executor import ChartExecutor
from taskSeperator import TaskSeperator
from dataFilter import DataFilter
from explain import Explainer
from modify import Modify
import pandas as pd
import plotly.express as px
from typing import Union, List
import time

class Viz:
    def __init__(self):
        self.summarize = Summarizer()
        self.vizgenerator = VizGenerator()
        self.choosechart = ChooseChart()
        self.chartexecutor = ChartExecutor()
        self.taskseperator = TaskSeperator()
        self.datafilter = DataFilter()
        self.explainer = Explainer()
        self.modify = Modify()

    def seperateTask(self,question:str,dataset:Union[pd.DataFrame,str],library="pyecharts"):
        data_summary = self.summarize.summarize(dataset,summary_method="default")
        start = time.time()
        questions = self.taskseperator.seperate(question,data_summary)
        end = time.time()
        print("task seperator: "+str(end-start))
        return questions


    def generateViz(self, questions: List[str], dataset:Union[pd.DataFrame,str], library="pyecharts"):
        data_summary = self.summarize.summarize(dataset, summary_method="default")
        chart_type = []
        lib = []
        chart = []
        print("len of questions(list):",len(questions))
        start = time.time()
        for q in questions:
            c,l = self.choosechart.chart_confidence(q,data_summary,library)
            chart_type.append(c)
            lib.append(l)
        end = time.time()
        print(f"choose chart time:{end-start}")
        if lib.count("altair") >= 2:
            combined_question = f"Use {len(questions)} charts to visualize the following questions:\n"
            for i in range(len(questions)):
                combined_question += f"Use {chart_type[i]} for question '{questions[i]}'"
            start = time.time()
            pycode = [self.vizgenerator.generateWithAssistant(dataset,"Refer to the question",combined_question,"altair")]
            end = time.time()
            print(f"generate code time:{end-start}")
            chart.append(self.chartexecutor.execute(pycode,dataset,data_summary))
        else:
            pycode = []
            start = time.time()
            for i in range(len(questions)):
                code = self.vizgenerator.generateWithAssistant(dataset, chart_type[i],questions[i],lib[i])
                pycode.append(code)
                chart.append(self.chartexecutor.execute([code],dataset,data_summary,lib[i]))
            end = time.time()
            print(f"generate code time:{end-start}")
        return chart


    def generateExplaination(self,pycode,dataset,question):
        pass








        # for q in questions:
        #     start = time.time()
        #     chartType,library = self.choosechart.chart_confidence(q,data_summary,library)
        #     end = time.time()
        #     print("choose chart type: " + str(end - start))
        #     start = time.time()
        #     pycode = self.vizgenerator.generate(data_summary,chartType,q,library)
        #     end = time.time()
        #     print("generate code: " + str(end - start))
        #     print(pycode)
        #     chart = self.chartexecutor.execute([pycode],dataset,data_summary,library)
        #     explaination = ""
        #     # explaination = self.explainer.explainWithoutAssistant(chart[0],q)
        #     # try:
        #     #     explaination = self.explainer.explain(q,pycode,dataset)
        #     # except:
        #     #     explaination = ""
        #
        #     code_specs.append(pycode)
        #     msg_specs.append(str(explaination))
        # chart = self.chartexecutor.execute(code_specs,dataset,data_summary,library)
        # print("--------------------------------------")
        # print(chart,msg_specs)
        # return chart,msg_specs

    def getExplaination(self,code,dataset):
        pass

    def modifyViz(self,msglist:list,question:str):
        response = self.modify.modify(msglist,str)
        return response


