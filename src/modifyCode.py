import re
from contextlib import redirect_stdout
from io import StringIO
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Pie,Bar,Line
from pyecharts.faker import Faker
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot
from pyecharts.globals import ThemeType
from collections import Counter
import pyecharts
def modify(code:str):
    # 处理python代码块
    if "```python" in code:
        cd = code.split("```python\n")
        code = ""
        if len(cd) <= 2:
            code += cd[1]
        else:
            for c in cd:
                if "```" in c:
                    code += c.split("```")[0]
    if "```" in code:
        code = code.split("```")[0]
    # 删掉所有的注释
    code = re.sub(r"# [\w ]+","",code)


    # 将render(“xxx.html”) 变成render_embed
    if len(re.findall(r"render[(][)]",code)) > 0:
        code = re.sub(r"render[(][)]","render_embed()",code)
    if len(re.findall(r"[a-zA-Z_]+.render[(].[0-9A-Za-z\u4e00-\u9fa5_]+.[\w]+.[)]",code)) > 0:
        if len(re.findall(r"v = [a-zA-Z_]+.render[(].[0-9A-Za-z\u4e00-\u9fa5_]+.[\w]+.[)]",code)):
            code = re.sub(r'render[(].[0-9A-Za-z\u4e00-\u9fa5_]+.html.[)]', 'render_embed()',code)
        else:
            temp = re.findall(r"[a-zA-Z_]+.render[(].[0-9A-Za-z\u4e00-\u9fa5_]+.[\w]+.[)]",code)[0]
            temp = re.findall(r"[a-zA-Z\u4e00-\u9fa5_]+",temp)[0]
            code = re.sub( r"[a-zA-Z_]+.render[(].[0-9A-Za-z\u4e00-\u9fa5_]+.[\w]+.[)]","return "+ temp + ".render_embed()",code)
    if len(re.findall("return v",code)) > 0:
        code = re.sub("\nreturn v","",code)

    # 将render_embed("xxx.html") 变为render_embed()
    if len(re.findall(r"render_embed[(]..[0-9A-Za-z\u4e00-\u9fa5_]+.[\w]+.[)]",code)):
        code = re.sub(r"render_embed[(]..[0-9A-Za-z\u4e00-\u9fa5_]+.[\w]+.[)]","render_embed()",code)

    # 将render_xxx()变为render_embed()
    code = re.sub(r"render_[\w]+","render_embed",code)

    # 处理只提供def函数而没有提供调用的情况
    if len(re.findall("def",code)) == 1:  # >=2的情况会出现多次调用，gpt理应帮忙写好，否则该重写
        temp = re.findall(r"def [a-zA-Z_(,)]+",code)[0].split(" ")[1]
        try:
            if len(re.findall(r"print",code)) < 1:      # 只在定义时出现过一次
                temp = re.findall(r"def [a-zA-Z_]+[(][a-zA-Z_,]+[)]",code)[0].split(" ")[1]
                code = code +  "\nprint(" + temp + ")"
        except:
            pass

    # 删除所有对df的定义
    if len(re.findall(r"df = pd.read_csv[(]...[\w]+.csv.[)]",code)) > 0:
        code = re.sub(r"df = pd.read_csv[(]...[\w]+.csv.[)]","",code)

    # 处理没有print但是有return的情况
    if len(re.findall("print",code)) == 0:
        if len(re.findall("return",code)) > 0:
            temp = re.findall(r"return [\w_().]+",code)[0].split(" ")[1]
            code = re.sub(r"return [\w_().]+",r"print("+temp+")\n    return 0",code)

    # 去掉所有import，因为没用....
    code = re.sub(r"import", "# import", code)
    code = re.sub(r"from", "# from", code)

    # 去掉title_pos属性，不支持
    code = re.sub(r", title_pos=.center.","",code)

    # TITLE_OPTS改为title_opts
    code = re.sub("TITLE_OPTS","title_opts",code)

    # pyecharts.render_embed改为图表名称(pie,bar,line).render_embed

    # 删掉所有的注释
    code = re.sub(r"# [\w .#]+","",code)

    # 导入csv文件，返回正确率更高的代码
    code = "import pandas as pd\ndf=pd.read_csv('./src/data.csv')\n" + code
    return code


def execCode(code):
    output = StringIO()
    df = pd.read_csv("./src/data.csv")
    with redirect_stdout(output):
        exec(code)
    return output.getvalue()
