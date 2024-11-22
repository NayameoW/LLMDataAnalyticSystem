from llm import LLM

class SummaryHandler:
    def __init__(self):
        self.llm = LLM()

    def generate_final_summary(self, question1, question2, question3, summary, chartType1, chartType2, chartType3):
        summary_prompt = """
Based on the following questions and visualizations:\n1. {question1} - Chart Type: {chartType1}\n2. {question2} - Chart Type: {chartType2}\n3. {question3} - Chart Type: {chartType3}\n
And considering the dataset summary:\n{summary}\n
Please provide a final conclusion summarizing the insights.
        """
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates conclusions based on questions, answers, and visualizations."},
            {"role": "user", "content": summary_prompt.format(question1=question1, question2=question2, question3=question3, summary=summary, chartType1=chartType1, chartType2=chartType2, chartType3=chartType3)}
        ]
        return self.llm.chat(messages)
