from llm import LLM
from RAGRetrieval import load_vectorstore, my_key
import re

import json
llm = LLM()
chart_info = {
  "bar chart":"compare data from different categories. When words like year, month etc. appears in the question, avoid bar chart.",
  "line chart":"Changes in the same variable OVER TIME. Use bar chart if years, months apeear in the question.",
  "pie chart":"You want to highlight the proportion of a part of the whole",
  "sunburst chart":"Ideal for representing data with multiple levels",
  "radar chart":"In cases where a data object consists of multiple feature categories, a radar chart is used to depict the data object. The required feature categories are limited and cannot be excessive. And they can all be normalized, or standardized according to uniform standards.",
  "box plot":"It is suitable for displaying the distribution overview of a single set of data (when there is only one boxline) or the distribution comparison between multiple sets of data (when there are multiple boxes).",
  "polar bar chart":"Compare the sizes of different classes, and the values of each category are not too different.",
  "force directed graph":"Describe the relationships between things, such as the relationship between people, computer networks, etc. More used to express abstract relationships.",
  "chord diagram":"When there are many categories of suitable data and the relationship is complex, especially bidirectional relationships (data is matrix-shaped). Chord diagrams are most commonly used to represent complex relationships (such as genetic connections between humans and other species) and the flow of data (such as mobile phone market share flows).",
  "heatmap":"The advantage of heat map is that it has high space utilization and can accommodate a relatively large amount of data.",
  "scatter chart":"Scatterplots are useful for analyzing whether there is a relationship or correlation between variables.",
  "bubble chart": "Multidimensional data which you can show 2 variables in coordinate system and show others by size, color or transparency.",
  "word cloud": "To visualize the frequency of words",
  "theme river": "To visualize the hottest words by time",
}
word_info = {
  "word cloud":"To visualize the frequency of words",
  "theme river":"To visualize the hottest words by time",
}

library_chart = {
  "bar chart":"altair",
  "line chart":"altair",
  "pie chart":"pyecharts",
  "sunburst chart":"pyecharts",
  "radar chart":"pyecharts",
  "box plot":"plotly",
  "polar bar chart":"pyecharts",
  "force directed chart":"pyecharts",
  "chord diagram":"pyecharts",
  "heatmap":"pyecharts",
  "scatter chart":"altair",
  "word cloud":"pyecharts",
  "theme river":"pyecharts",
}

class ChooseChart:
  def rule(self,confidence:dict,question:str):
    system_prompt = """
      You are a person good at data analysis. Now I will give you a visualization question and a rule. You should answer me whether the question obeys the rule.
      You should only answer YES or NO and do not give any explanation.
    """
    rule = [
      "Are variables from different categories?",
      "Do the variables change over time?"
      ""
    ]
    return confidence

  def isTextVisualization(self,question:str,summary:dict):
      system_prompt = """
      Now I want you to judge whether the question and data is suitable to use text visualization method(like wordcloud, theme-river)
      You should only answer YES or NO and do not give any explaination.
      """
      messages = []
      prompt = f"How much confidence do you have in visualization question:{question}"
      messages.append({"role":"system","content":system_prompt})
      messages.append({"role":"system","content":f"The dataset summary is:{summary}\n\n"})
      messages.append({"role":"user","content":prompt})
      response = llm.chat(messages)
      return response


  def chart_confidence(self,question:str,summary:dict,library:str):
    # try:
      system_prompt = """
      You are an expert in visualization and can give how much confidence you have to use a specific chart to visualize question.
      You MUST carefully understand what scenarios each chart is good at and give your confidence(0-100). evaluate each chart under the SAME STANDARD.
      Now I will give you an example. When I ask you the question "How much data is there per day", you should give me the dict as follows:
      {"bar chart":80, "line chart":70, "pie chart":30, "sunburst chart":20, "radar chart":20, "box plot":10, "polar bar chart":20, "force directed graph":10, "chord diagram":5, "heatmap":0, "scatter chart":40,"bubble chart":50}
      Only return a dict and DO NOT CONTAIN ANY EXPLANATION.
      """
      chart_prompt = ""
      try:
          response = self.isTextVisualization(question,summary)
      except:
          response = "NO"

      if "YES" in response:
          for k, v in word_info.items():
              chart_prompt += f"{k} is suitable for the following scenarios:\n{v}\n\n"
      else:
          for k,v in chart_info.items():
              chart_prompt += f"{k} is suitable for the following scenarios:\n{v}\n\n"
      
      # Retrieve relevant visualization examples and scenarios from RAG
      try:
        vectorstore = load_vectorstore("vectorstore")
        similar_docs = vectorstore.similarity_search(
            question,
            k=5
        )
        
        rag_context = "\nRelevant visualization examples and scenarios:\n"
        for doc in similar_docs:
            rag_context += f"{doc.page_content}\n"
        
        enhanced_chart_prompt = chart_prompt + rag_context
        
      except Exception as e:
        print(f"RAG retrieval failed: {e}")
        enhanced_chart_prompt = chart_prompt
      
      prompt = f"How much confidence do you have in visualization question:{question}"
      messages = [{"role":"system","content":enhanced_chart_prompt}]
      messages.append({"role":"system","content":system_prompt})
      messages.append({"role":"system","content":f"The dataset summary is:{summary}\n\n"})
      messages.append({"role":"user","content":prompt})

      try:
          response = llm.chat(messages)
          print(response)
          response = self.preprocess_dict(response)
      except:
          response = llm.chat(messages)
          response = self.preprocess_dict(response)
      chartType, score, library = self.choose(response)

      try:
          with open("history/chartChosen.txt","r",encoding="utf-8") as f:
              history = eval(f.read())
      except:
          history = []
      history.append({"question":question,"type":chartType})
      # with open("history/chartChosen.txt","w") as f:
      #     f.write(f"{history}")

      return chartType, score,library
    # except:
    #   return self.chart_confidence(question,summary,library)

  def preprocess_dict(self,response:str):
    matches = re.findall(r'[{](.*?)[}]', response)
    if matches:
        result = "{" + matches[0] + "}"
    else:
        result = response
    return result


  def choose(self,response:str):
    response = eval(response)
    response = list(response.items())
    response.sort(key=lambda x: x[1], reverse=True)
    chart = response[0][0]
    score = response[0][1]
    library = library_chart[chart]
    return chart, score, library


if __name__ == '__main__':
  choosechart = ChooseChart()
  choosechart.chart_confidence("How do the sales change by years?","","pyecharts")
