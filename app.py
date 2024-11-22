from flask import Flask, render_template, request, jsonify
import pandas as pd
from summarize import Summarizer
from taskSeperator import TaskSeperator
from chartChosen import ChooseChart
from dataFilter import DataFilter
from visualize import VizGenerator
from executor import ChartExecutor
from conclusion import SummaryHandler


app = Flask(__name__)

data = None
data1,data2,data3=None,None, None
question1, question2, question3 = None, None, None
# question1="What are the yearly trends in Audience score % from 2005 to 2011?"
# question2="How does the Profitability of films change from 2005 to 2011?"
# question3="What is the yearly distribution of Worldwide Gross for films released from 2005 to 2011?"
summary = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    global data, data1,data2,data3,summary
    question = request.form.get('question')
    file = request.files.get('file')

    if file:
        data = pd.read_csv(file)
        data1= data.copy()
        data2 =  data.copy()
        data3 =  data.copy()
        s = Summarizer()
        summary = s.summarize(data)
        dataset_description = summary.get('dataset_description', 'No description available.')
        return jsonify({'summary': dataset_description})
    else:
        return jsonify({'error': 'Please upload your data.'}), 400

@app.route('/split_question', methods=['POST'])
def split_question():
    global question1, question2, question3
    question = request.form.get('question')

    if data is not None and summary is not None:
        s = Summarizer()
        ts = TaskSeperator()
        tmp_summary = s.summarize(data, summary_method="default")
        question1, question2, question3 = ts.seperate(question, tmp_summary)
        return jsonify({
            'question1': question1,
            'question2': question2,
            'question3': question3
        })
    else:
        return jsonify({'error': 'Please first summarize the data.'}), 400

@app.route('/generate_answer', methods=['POST'])
def generate_answer():
    global question1, question2, question3, summary

    if data is not None and summary is not None and question1 and question2 and question3:
        chartchooser = ChooseChart()
        chartType1, score1, library = chartchooser.chart_confidence(question1, summary, "seaborn")
        chartType2, score2, library = chartchooser.chart_confidence(question2, summary, "seaborn")
        chartType3, score3, library = chartchooser.chart_confidence(question3, summary, "seaborn")
        
        vizgenerator = VizGenerator()
        chartexecutor = ChartExecutor()

        # Generate visualization codes
        code1 = vizgenerator.generate(summary, chartType1, question1, library="seaborn")
        code2 = vizgenerator.generate(summary, chartType2, question2, library="seaborn")
        code3 = vizgenerator.generate(summary, chartType3, question3, library="seaborn")

        # Execute codes to generate HTML
        with open("chart_output.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        print(html_content)

        # html1=html_content
        html1 = chartexecutor.execute([code1], data1, summary, library="seaborn")
        # print("html1",html1)
        html2 = chartexecutor.execute([code2], data2, summary, library="seaborn")
        # print("html2",html2)
        html3 = chartexecutor.execute([code3], data3, summary, library="seaborn")
        # print("html3",html3)
        

        # TODO: Generate final summary
        # with open("conclusion.txt", "r", encoding="utf-8") as file:
        #     summary = file.read()
        summary_handler = SummaryHandler()
        summary = summary_handler.generate_final_summary(question1, question2, question3, summary, chartType1, chartType2, chartType3)
        

        return jsonify({
            'chartType1': chartType1,
            'score1': score1,
            'html1': html1,
            'chartType2': chartType2,
            'score2': score2,
            'html2': html2,
            'chartType3': chartType3,
            'score3': score3,
            'html3': html3,
            'summary': summary
        })
    else:
        return jsonify({'error': 'Please split the questions first'}), 400

if __name__ == '__main__':
    app.run(debug=True)