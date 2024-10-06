import time
import random
import json
from datetime import datetime, timedelta
from langchain.agents import initialize_agent, Tool
# from langchain.llms import ollama
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.output_parsers import JsonOutputParser


# 定义全局变量来存储之前的传感器状态
previous_people_count = None
previous_light_level = None
previous_temperature = None

# 1. 人数检测器
def get_current_people_count():
    global previous_people_count
    # 模拟获取室内人数
    people_count = random.randint(0, 5)
    result = people_count
    # 检测人数是否发生变化
    if previous_people_count != people_count:
        previous_people_count = people_count
        return people_count
    else:
        return None  # 未发生变化

# 2. 光线传感器读取器
def read_light_sensor():
    global previous_light_level
    # 模拟读取光线传感器数据
    light_level = random.uniform(0, 100)
    # 检测光线是否发生变化
    if previous_light_level != light_level:
        previous_light_level = light_level
        return light_level
    else:
        return None  # 未发生变化

# 3. 温度传感器读取器
def read_temperature_sensor():
    global previous_temperature
    # 模拟读取温度传感器数据
    temperature = random.uniform(18, 30)
    # 检测温度是否发生变化
    if previous_temperature != temperature:
        previous_temperature = temperature
        return temperature
    else:
        return None  # 未发生变化

# 4. 设备控制器
def control_device(device_name, action):
    # 模拟设备控制
    return f"已{'打开' if action == 'on' else '关闭'} {device_name}。"

# 5. 天气预报查询器
def get_weather_forecast():
    # 模拟获取未来几天的天气
    forecast = []
    for i in range(5):
        day = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        temp = random.uniform(20, 35)
        forecast.append({'date': day, 'temperature': temp})
    return forecast

# 6. 能源消耗计算器
def calculate_energy_consumption():
    # 模拟计算能源消耗
    consumption = {
        'today': {
            'led_usage_kwh': 10 * 0.1,  # 假设每个LED灯每天耗电0.1kWh
            'ac_usage_kwh': 5.0  # 假设空调每天耗电5kWh
        },
        'future': []
    }
    for i in range(1, 6):
        day = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        led_usage = 10 * 0.1
        ac_usage = 5.0
        consumption['future'].append({
            'date': day,
            'led_usage_kwh': led_usage,
            'ac_usage_kwh': ac_usage
        })
    # 生成 JSON 文件
    with open('energy_consumption.json', 'w') as f:
        json.dump(consumption, f)
    return "能源消耗计算完成，结果已保存为 energy_consumption.json 文件。"

# 定义工具列表
tools = [
    Tool(
        name="GetCurrentPeopleCount",
        func=get_current_people_count,
        description="获取当前室内人数。"
    ),
    Tool(
        name="ReadLightSensor",
        func=read_light_sensor,
        description="读取当前光线传感器的数据。"
    ),
    Tool(
        name="ReadTemperatureSensor",
        func=read_temperature_sensor,
        description="读取当前温度传感器的数据。"
    ),
    Tool(
        name="ControlDevice",
        func=lambda x: control_device(*x.split(',')),
        description="控制设备的开关。用法：ControlDevice('设备名称', 'on/off')"
    ),
    Tool(
        name="GetWeatherForecast",
        func=get_weather_forecast,
        description="获取未来几天的天气预报信息。"
    ),
    Tool(
        name="CalculateEnergyConsumption",
        func=calculate_energy_consumption,
        description="计算能源消耗并生成 JSON 文件。"
    )
]

# 初始化语言模型
llm = OllamaLLM(model="llama3.2")

# 定义自定义的 Prompt 模板
prompt = PromptTemplate(
    input_variables=["input"],
    template="""
你是一位智能家居助手，具备能源消耗监控的功能。你的任务是根据传感器数据，使用提供的工具完成相应的操作。

可用工具:
{tool_names}

工具描述:
{tools}

当前传感器数据：
{input}

请根据当前传感器数据，选择合适的工具来完成任务。
Thought: 确定室内的人数
Action: GetCurrentPeopleCount()
Observation: GetCurrentPeopleCount()返回了一个整数，表示当前室内人数。

{agent_scratchpad}
Final Answer: 人数检测


"""
)

# 初始化代理
agent = create_react_agent(
    tools=tools,
    llm=llm,
    # agent="zero-shot-react-description",
    # verbose=True,
    prompt=prompt
)
agent_executor = AgentExecutor(agent=agent, tools=tools,handle_parsing_errors=True, output_parser=JsonOutputParser())
# 主循环
# while True:
    # 收集当前传感器数据
sensor_data = []
people_count = get_current_people_count()
if people_count is not None:
    sensor_data.append(f"当前室内人数为 {people_count} 人。")
light_level = read_light_sensor()
if light_level is not None:
    sensor_data.append(f"当前光线强度为 {light_level:.2f} 流明。")
temperature = read_temperature_sensor()
if temperature is not None:
    sensor_data.append(f"当前室内温度为 {temperature:.2f}℃。")

# 如果有新的传感器数据，则让代理处理
if sensor_data:
    input_data = '\n'.join(sensor_data)
    # 代理处理输入
    agent_response = agent_executor.invoke({"input": input_data})

    print(agent_response["output"])
    print('-' * 50)
    
    # 每隔一段时间检查一次，例如每隔10秒
    # time.sleep(2)
