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

from pyecharts import options as opts
from pyecharts.charts import Bar3D

# 准备数据
data = [
    [0, 0, 0, 5], [0, 1, 0, 20], [0, 2, 0, 36], [0, 3, 0, 10], [0, 4, 0, 75],
    [0, 0, 1, 10], [0, 1, 1, 35], [0, 2, 1, 87], [0, 3, 1, 73], [0, 4, 1, 45],
    [0, 0, 2, 15], [0, 1, 2, 45], [0, 2, 2, 67], [0, 3, 2, 98], [0, 4, 2, 56],
    [0, 0, 3, 20], [0, 1, 3, 55], [0, 2, 3, 46], [0, 3, 3, 89], [0, 4, 3, 67],
    [1, 0, 0, 12], [1, 1, 0, 45], [1, 2, 0, 76], [1, 3, 0, 20], [1, 4, 0, 77],
    [1, 0, 1, 23], [1, 1, 1, 67], [1, 2, 1, 98], [1, 3, 1, 87], [1, 4, 1, 34],
    [1, 0, 2, 34], [1, 1, 2, 78], [1, 2, 2, 65], [1, 3, 2, 43], [1, 4, 2, 89],
    [1, 0, 3, 45], [1, 1, 3, 23], [1, 2, 3, 56], [1, 3, 3, 12], [1, 4, 3, 34],
]

# 创建3D柱状图
bar3d = (
    Bar3D()
    .add("", data)
    .set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            max_=100,  # 设置最大值
            range_color=[
                "#313695", "#4575b4", "#74add1", "#abd9e9", "#e0f3f8",
                "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027", "#a50026"
            ]
        )
    )
)

# 保存图像
bar3d.render("3d_bar_chart.html")
