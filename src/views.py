from src import app
from src.models import Model
from flask import request,jsonify
import json
import os
import pandas as pd
import openai
from vizclass import Viz
import plotly.express as px

model = Model()
viz = Viz()
print("==============================================")

def firstGenerate(question,filename,dataset):
    questions = viz.seperateTask(question,dataset)
    chart = viz.generateViz(questions,dataset)
    msglist = []
    explaination = ["", "", ""]
    assert len(chart) > 0
    for i in range(len(chart)):
        msglist.append({"id": 1, "type": 1, "content": chart[i], "me": False})
        msglist.append({"id": 1, "type": 2, "content": explaination[i], "me": False})
    package = {"msglist": msglist}
    try:
        with open("./history/chathistory.txt", "r", encoding="utf-8") as f:
                chathistory = eval(f.read())
    except:
        chathistory = {}
        print("load history error")
    chathistory[len(chathistory)] = {"id": len(chathistory), "name": question, "file": filename, "content": msglist}
    package["id"] = len(chathistory)-1
    with open("./history/chathistory.txt", "w", encoding="utf-8") as f:
        f.write(f"{chathistory}")
    return package
    # with open("./trytrytry/render.html","r") as f:
    #     chart = f.read()
    # return [{"id": 1, "type": 1, "content": chart, "me": False}]

def modifyGenerate(msglist,question):
    chart = viz.modifyViz(msglist, question)
    msglist = []
    msglist.append({"id": 1, "type": 1, "content": chart, "me": False})
    package = {"msglist": msglist}
    return package


@app.route("/ask",methods=["POST"])
def _generate():
    data = request.get_json()
    messagelist = data.get("msglist")
    question = data.get("question")
    filename = data.get("filename")
    ack = data.get("ack")
    dataset = pd.read_csv("./data/"+filename)
    # msglist = [{'id': 1, 'type': 1, 'content': '<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="UTF-8">\n    <title>Awesome-pyecharts</title>\n                <script type="text/javascript" src="https://assets.pyecharts.org/assets/v5/echarts.min.js"></script>\n\n</head>\n<body >\n    <div id="093b6dfc1a1044eba0b688ec6cc8804e" class="chart-container" style="width:900px; height:500px; "></div>\n    <script>\n        var chart_093b6dfc1a1044eba0b688ec6cc8804e = echarts.init(\n            document.getElementById(\'093b6dfc1a1044eba0b688ec6cc8804e\'), \'white\', {renderer: \'canvas\'});\n        var option_093b6dfc1a1044eba0b688ec6cc8804e = {\n    "animation": true,\n    "animationThreshold": 2000,\n    "animationDuration": 1000,\n    "animationEasing": "cubicOut",\n    "animationDelay": 0,\n    "animationDurationUpdate": 300,\n    "animationEasingUpdate": "cubicOut",\n    "animationDelayUpdate": 0,\n    "aria": {\n        "enabled": false\n    },\n    "color": [\n        "#5470c6",\n        "#91cc75",\n        "#fac858",\n        "#ee6666",\n        "#73c0de",\n        "#3ba272",\n        "#fc8452",\n        "#9a60b4",\n        "#ea7ccc"\n    ],\n    "series": [\n        {\n            "type": "line",\n            "name": "GDP Per Capita",\n            "connectNulls": false,\n            "xAxisIndex": 0,\n            "symbolSize": 4,\n            "showSymbol": true,\n            "smooth": true,\n            "clip": true,\n            "step": false,\n            "data": [\n                [\n                    1952,\n                    400.448611\n                ],\n                [\n                    1957,\n                    575.9870009\n                ],\n                [\n                    1962,\n                    487.6740183\n                ],\n                [\n                    1967,\n                    612.7056934\n                ],\n                [\n                    1972,\n                    676.9000921\n                ],\n                [\n                    1977,\n                    741.2374699\n                ],\n                [\n                    1982,\n                    962.4213805\n                ],\n                [\n                    1987,\n                    1378.904018\n                ],\n                [\n                    1992,\n                    1655.784158\n                ],\n                [\n                    1997,\n                    2289.234136\n                ],\n                [\n                    2002,\n                    3119.280896\n                ],\n                [\n                    2007,\n                    4959.114854\n                ]\n            ],\n            "hoverAnimation": true,\n            "label": {\n                "show": false,\n                "margin": 8\n            },\n            "logBase": 10,\n            "seriesLayoutBy": "column",\n            "lineStyle": {\n                "show": true,\n                "width": 2,\n                "opacity": 1,\n                "curveness": 0,\n                "type": "solid"\n            },\n            "areaStyle": {\n                "opacity": 0\n            },\n            "zlevel": 0,\n            "z": 0,\n            "rippleEffect": {\n                "show": true,\n                "brushType": "stroke",\n                "scale": 2.5,\n                "period": 4\n            }\n        }\n    ],\n    "legend": [\n        {\n            "data": [\n                "GDP Per Capita"\n            ],\n            "selected": {},\n            "show": true,\n            "padding": 5,\n            "itemGap": 10,\n            "itemWidth": 25,\n            "itemHeight": 14,\n            "backgroundColor": "transparent",\n            "borderColor": "#ccc",\n            "borderWidth": 1,\n            "borderRadius": 0,\n            "pageButtonItemGap": 5,\n            "pageButtonPosition": "end",\n            "pageFormatter": "{current}/{total}",\n            "pageIconColor": "#2f4554",\n            "pageIconInactiveColor": "#aaa",\n            "pageIconSize": 15,\n            "animationDurationUpdate": 800,\n            "selector": false,\n            "selectorPosition": "auto",\n            "selectorItemGap": 7,\n            "selectorButtonGap": 10\n        }\n    ],\n    "tooltip": {\n        "show": true,\n        "trigger": "axis",\n        "triggerOn": "mousemove|click",\n        "axisPointer": {\n            "type": "line"\n        },\n        "showContent": true,\n        "alwaysShowContent": false,\n        "showDelay": 0,\n        "hideDelay": 100,\n        "enterable": false,\n        "confine": false,\n        "appendToBody": false,\n        "transitionDuration": 0.4,\n        "textStyle": {\n            "fontSize": 14\n        },\n        "borderWidth": 0,\n        "padding": 5,\n        "order": "seriesAsc"\n    },\n    "xAxis": [\n        {\n            "type": "category",\n            "name": "Year",\n            "show": true,\n            "scale": false,\n            "nameLocation": "end",\n            "nameGap": 15,\n            "gridIndex": 0,\n            "inverse": false,\n            "offset": 0,\n            "splitNumber": 5,\n            "minInterval": 0,\n            "splitLine": {\n                "show": true,\n                "lineStyle": {\n                    "show": true,\n                    "width": 1,\n                    "opacity": 1,\n                    "curveness": 0,\n                    "type": "solid"\n                }\n            },\n            "data": [\n                1952,\n                1957,\n                1962,\n                1967,\n                1972,\n                1977,\n                1982,\n                1987,\n                1992,\n                1997,\n                2002,\n                2007\n            ]\n        }\n    ],\n    "yAxis": [\n        {\n            "type": "value",\n            "name": "GDP Per Capita (USD)",\n            "show": true,\n            "scale": false,\n            "nameLocation": "end",\n            "nameGap": 15,\n            "gridIndex": 0,\n            "inverse": false,\n            "offset": 0,\n            "splitNumber": 5,\n            "minInterval": 0,\n            "splitLine": {\n                "show": true,\n                "lineStyle": {\n                    "show": true,\n                    "width": 1,\n                    "opacity": 1,\n                    "curveness": 0,\n                    "type": "solid"\n                }\n            }\n        }\n    ],\n    "title": [\n        {\n            "show": true,\n            "text": "GDP Per Capita of China Over Time",\n            "target": "blank",\n            "subtarget": "blank",\n            "padding": 5,\n            "itemGap": 10,\n            "textAlign": "auto",\n            "textVerticalAlign": "auto",\n            "triggerEvent": false\n        }\n    ]\n};\n        chart_093b6dfc1a1044eba0b688ec6cc8804e.setOption(option_093b6dfc1a1044eba0b688ec6cc8804e);\n    </script>\n</body>\n</html>\n', 'me': False}, {'id': 1, 'type': 2, 'content': 'explain', 'me': False}]
    msglist = []
    for m in messagelist:
        if m["id"] > 0:
            if m["me"]:
                msglist.append({"role":"user","content":m["content"]})
            else:
                msglist.append({"role":"assistant","content":m["content"]})
    if len(msglist) <= 2:
        package = firstGenerate(question,filename,dataset)
    else:
        package = modifyGenerate(msglist,question)

    return jsonify(package)

@app.route("/change/1",methods=["POST"])
def _change1():
    data = request.get_json()
    question = data.get("question")
    chart1 = data.get("chart1")
    chart2 = data.get("chart2")
    chart1 = viz.modifyViz(question,chart1)
    package = {"chart1":chart1,"chart2":chart2,"explain1":"N/A","explain2":"N/A"}
    return jsonify(package)

@app.route("/change/2",methods=["POST"])
def _change2():
    data = request.get_json()
    question = data.get("question")
    chart1 = data.get("chart1")
    chart2 = data.get("chart2")
    chart2 = viz.modifyViz(question,chart2)
    package = {"chart1":chart1,"chart2":chart2,"explain1":"N/A","explain2":"N/A"}
    return jsonify(package)

@app.route('/file',methods=["POST"])
def _file():
    file = request.files['file']
    file.save("data/"+file.filename)
    df = pd.read_csv("./data/"+file.filename)
    column = list(df)
    data = df.values.tolist()
    datadict = []
    for d in data:
        temp = {}
        for i in range(len(d)):
            temp[column[i]] = d[i]
        datadict.append(temp)
    info = {"data":datadict,"column":column}
    return jsonify(info)

@app.route('/gethistory',methods=["POST"])
def _gethistory():
    with open("./history/chathistory.txt","r") as f:
        chathistory = eval(f.read())
    historylist = []
    for k,v in chathistory.items():
        historylist.append({"id":k,"name":v["name"],"content":v["content"]})
    print(historylist)
    return jsonify({"historylist":historylist})

@app.route('/feedback',methods=["POST"])
def _feedback():
    with open("./history/chathistory.txt", "r", encoding="utf-8") as f:
        try:
            chathistory = eval(f.read())
        except:
            chathistory = {}
            print("load history error")
    data = request.get_json()
    id = data.get("id")
    feedback = data.get("feedback")
    print(id)
    print(feedback)
    chathistory[id]["feedback"] = feedback
    with open("./history/chathistory.txt", "w", encoding="utf-8") as f:
        f.write(f"{chathistory}")

