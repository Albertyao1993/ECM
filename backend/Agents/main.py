import pymongo
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain.agents import AgentExecutor, Tool, LLMSingleActionAgent
# from langchain_core.memory import ConversationBufferMemory
# from langchain_core.schema import SystemMessage
from langchain_core.tools import tool

import Database 
from Database.db_operation import Database

# MongoDB 连接设置
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "sensor_data"
COLLECTION_NAME = "readings"

# 初始化数据库对象
db = Database(MONGO_URI, DB_NAME, COLLECTION_NAME)

# 定义读取最新数据的函数
def read_latest():
    latest_record = db.read_latest()
    if latest_record:
        return latest_record
    else:
        return "No data available"

# 定义工具
@tool
def get_latest_data(query: str) -> str:
    return read_latest()

tools = [get_latest_data]

# 定义模板
template = """Question: {question}

Answer: Let's think step by step."""

prompt = ChatPromptTemplate.from_template(template)

# 初始化模型
model = OllamaLLM(model="llama3.2")

# 定义代理
class CustomAgent(LLMSingleActionAgent):
    def __init__(self, llm, tools, prompt):
        super().__init__(llm=llm, tools=tools, prompt=prompt)
        # self.memory = ConversationBufferMemory(memory_key="chat_history")

    def plan(self, inputs):
        question = inputs["question"]
        if "latest data" in question.lower():
            return self.tools[0].func(question)
        else:
            return self.llm.invoke({"question": question})

# 初始化代理
agent = CustomAgent(llm=model, tools=tools, prompt=prompt)

# 运行代理
if __name__ == "__main__":
    question = "Can you get the latest data from MongoDB?"
    response = agent.plan({"question": question})
    print(response)