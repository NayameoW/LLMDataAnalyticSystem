from llm import LLM
import re
llm = LLM()

class FindEncoding:
    def findencoding(self,code:str):
        sys_prompt = '''
You are a software engineer who is specialized in visualization.
Now I give you a code, and you should return me a dict which tells me the visualization encoding of the chart.
visualization encoding includes: filter, aggregate, x-axis, y-axis, color, type, sort
All the data should be included in the dataset and do not include any thing like ":T" ":N“
In aggregation part, you should include function and name. like count(id),sum(id)
return a dict like:
{"filter":"age > 18 and major != 600 and sex=1", "aggregate":"count(Fname)", "x-axis":"Fname","y-axis":"count(Fname)","color":None,"type":"pie","sort":"asc Fname"}
for pie chart, x-axis means the category and y-axis means theta.

        '''

        messages = []
        messages.append({"role": "system", "content": sys_prompt})
        messages.append({"role": "user", "content": f"Please find the visualization encoding:{code}"})
        llm = LLM()
        response = llm.chat(messages)

        return response

if __name__ == '__main__':
    fe = FindEncoding()
    code = """
def plot(data: pd.DataFrame):
  # Aggregate course counts per year, grouped by semester
  course_counts = data.groupby(['year', 'semester']).size().reset_index(name='counts')
  
  # Sort the aggregated data by year in ascending order and then by semester in descending order
  course_counts.sort_values(by=['year', 'semester'], ascending=[True, False], inplace=True)

  # Pivot the data to get years as index, semester as columns, and course counts as values
  pivot_course_counts = course_counts.pivot(index='year', columns='semester', values='counts').fillna(0)

  # Generating the line chart using pyecharts
  chart = Line(init_opts=opts.InitOpts(width='1000px', height='600px'))
  for semester in pivot_course_counts.columns:
    chart.add_xaxis(pivot_course_counts.index.tolist())
    chart.add_yaxis(semester, pivot_course_counts[semester].tolist(),
                    is_smooth=True,
                    label_opts=opts.LabelOpts(is_show=False),
                    linestyle_opts=opts.LineStyleOpts(width=2))
  chart.set_series_opts(
        markpoint_opts=opts.MarkPointOpts(
            data=[opts.MarkPointItem(type_="max", name="Max")],
            label_opts=opts.LabelOpts(position="inside", formatter=JsCode(
                "function(params){return params.value[2].toFixed(2);}"))),
    )
  chart.set_global_opts(title_opts=opts.TitleOpts(title="Course Counts Per Year, Grouped by Semester"),
                        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                        xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False, 
                                                 axislabel_opts=opts.LabelOpts(rotate=30)),
                        yaxis_opts=opts.AxisOpts(name="Number of Courses"),
                        legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="5%"))

  return chart.render_embed()

    """
    print(fe.findencoding(code))