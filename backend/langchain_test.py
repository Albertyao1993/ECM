import pymongo
import serial
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_core.tools import tool
# from langchain_core.memory import ConversationBufferMemory
# from langchain_core.schema import SystemMessage

from Database.db_operation import Database

# MongoDB 连接设置
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "sensor_data"
COLLECTION_NAME = "readings"

# Arduino 连接设置
ARDUINO_PORT = "/dev/ttyACM0"  # 根据实际情况修改端口
BAUD_RATE = 9600

# 初始化数据库对象
db = Database(MONGO_URI, DB_NAME, COLLECTION_NAME)

# 初始化 Arduino 连接
arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE)

# 定义读取最新数据的函数
def read_latest():
    latest_record = db.read_latest()
    if (latest_record):
        return latest_record
    else:
        return "No data available"

# 定义工具
@tool
def get_latest_data(query: str) -> str:
    """Get the latest data from MongoDB."""
    return read_latest()

@tool
def control_led_based_on_conditions(query: str) -> str:
    """Control the LED on Arduino based on the latest data conditions."""
    latest_record = read_latest()
    if isinstance(latest_record, dict):
        person_count = latest_record.get("person_count", 0)
        light = latest_record.get("light", 100)
        led_status = latest_record.get("led_status", "OFF")  # 假设数据库中有 LED 状态字段

        if person_count == 0 and light < 50:
            if led_status == "ON":
                arduino.write(b'LED_OFF\n')
                return "LED turned off"
            else:
                return "LED is already off"
        elif person_count != 0 and light < 100:
            if led_status == "OFF":
                arduino.write(b'LED_ON\n')
                return "LED turned on"
            else:
                return "LED is already on"
        elif person_count != 0 and light >= 100:
            return "Conditions not met, LED remains unchanged"
        else:
            return "Conditions not met, LED remains unchanged"
    else:
        return latest_record

tools = [get_latest_data, control_led_based_on_conditions]

# 定义模板
template = """Question: {question}

Answer: Let's think step by step."""

prompt = ChatPromptTemplate.from_template(template)

# 初始化模型
model = OllamaLLM(model="llama3.2")

# 定义代理
class CustomAgent:
    def __init__(self, llm, tools, prompt):
        self.llm = llm
        self.tools = tools
        self.prompt = prompt
        # self.memory = ConversationBufferMemory(memory_key="chat_history")

    def plan(self, inputs):
        question = inputs["question"]
        if "latest data" in question.lower():
            return self.tools[0].func(question)
        elif "control led" in question.lower():
            return self.tools[1].func(question)
        else:
            return self.llm.invoke({"question": question})

# 初始化代理
agent = CustomAgent(llm=model, tools=tools, prompt=prompt)

# 运行代理
if __name__ == "__main__":
    question = "Can you control the LED based on the latest data?"
    response = agent.plan({"question": question})
    print(response)