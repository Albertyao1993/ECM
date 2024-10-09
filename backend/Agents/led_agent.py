from langchain_community.llms import Ollama
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from server.energy_calculator import EnergyCalculator
import logging
import json
import re
import traceback
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

class LEDAgent:
    def __init__(self, dth111):
        self.dth111 = dth111
        try:
            load_dotenv()  # 加载 .env 文件中的环境变量
            self.llm = ChatOpenAI(model_name="gpt-3.5-turbo")  # 使用 OpenAI 的模型
            self.energy_calculator = EnergyCalculator()
            self.tools = [
                Tool(
                    name="LED Control",
                    func=self.control_led,
                    description="Control LED light based on light intensity"
                ),
                Tool(
                    name="Energy Calculation",
                    func=self.calculate_energy,
                    description="Calculate energy consumption and cost of LED light"
                )
            ]
            
            response_schemas = [
                ResponseSchema(name="led_action", description="LED light control action (on or off)"),
                ResponseSchema(name="current_light", description="Current indoor light intensity"),
                ResponseSchema(name="energy_info", description="Energy consumption and cost information"),
                ResponseSchema(name="analysis", description="Brief analysis of LED light usage")
            ]
            self.output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
            
            template = '''You are an AI assistant for a smart home system, responsible for analyzing LED light usage. You have the following tools at your disposal:

                {tools}

                Use the following format to answer questions:

                Question: the input question you must answer
                Thought: you should always think about what to do next
                Action: the action to take, should be one of [{tool_names}]
                Action Input: the input for the action. For the "LED Control" tool, use the format "light_value=X", where X is the light intensity. For the "Energy Calculation" tool, use the format "duration=Y", where Y is the usage duration in hours.
                Observation: the result of the action
                ... (this Thought/Action/Action Input/Observation can repeat N times)
                Thought: I now know the final answer
                Final Answer: {format_instructions}

                Note:
                1. First use the "LED Control" tool to decide whether to turn on the LED light, input format is "light_value=X".
                2. Then use the "Energy Calculation" tool to calculate energy consumption and cost, input format is "duration=Y".
                3. Finally, analyze the information obtained and provide the final answer.
                4. Ensure all values are numbers, do not include any additional text.

                Begin!

                Question: {input}
                Thought:{agent_scratchpad}'''

            prompt = PromptTemplate(
                template=template,
                input_variables=["tools", "tool_names", "input", "agent_scratchpad"],
                partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
            )
            
            self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            self.agent = create_react_agent(self.llm, self.tools, prompt)
            self.agent_executor = AgentExecutor.from_agent_and_tools(
                agent=self.agent, 
                tools=self.tools, 
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True
            )
        except Exception as e:
            logging.error(f"Error initializing LEDAgent: {str(e)}")
            logging.error(traceback.format_exc())
            raise

    def control_led(self, input_str):
        try:
            light_value = float(input_str.split('=')[-1].strip())
            if light_value < 100:
                action = "Turn on LED light"
            else:
                action = "Turn off LED light"
            
            # 调用 DTH111 的方法来实际控制 LED
            success = self.dth111.control_led_from_agent(action)
            if success:
                return action
            else:
                return "Failed, can not control led"
        except Exception as e:
            logging.error(f"控制 LED 时出错: {str(e)}")
            return "无法控制 LED 灯。请确保您提供了正确的光照值。"

    def calculate_energy(self, input_str):
        try:
            duration = float(input_str.split('=')[-1].strip())
            energy_kwh = self.energy_calculator.calculate_energy_consumption(duration * 3600)  # convert to seconds
            cost = self.energy_calculator.calculate_cost(energy_kwh)
            return f"Energy consumption: {energy_kwh:.2f} kWh, Cost: {cost:.2f} currency units"
        except Exception as e:
            logging.error(f"Error in calculate_energy: {str(e)}")
            return "Unable to calculate energy consumption and cost. Please ensure you provided a correct duration."

    def analyze_and_suggest(self, light_value, duration):
        try:
            logging.info(f"Analyzing LED usage: light_value={light_value}, duration={duration}")
            response = self.agent_executor.invoke(
                {"input": f"Light intensity is {light_value}, LED light usage duration is {duration} hours."}
            )
            logging.info(f"Agent response: {response}")

            if not isinstance(response, dict) or 'output' not in response:
                raise ValueError(f"Unexpected response format from agent_executor: {response}")

            output = response['output']
            logging.info(f"Agent output: {output}")

            try:
                parsed_output = self.output_parser.parse(output)
                logging.info(f"Parsed output: {parsed_output}")
                
                # 直接返回解析后的输出，不进行额外处理
                return parsed_output
            except Exception as parse_error:
                logging.error(f"Error parsing output: {str(parse_error)}")
                # 如果解析失败，使用fallback响应
                return self.fallback_response(light_value, duration)

        except Exception as e:
            logging.error(f"Error in analyze_and_suggest: {str(e)}")
            logging.error(traceback.format_exc())
            return self.fallback_response(light_value, duration)

    def fallback_response(self, light_value, duration):
        return {
            "led_action": self.control_led(f"light_value={light_value}"),
            "energy_info": self.calculate_energy(f"duration={duration}"),
            "analysis": "Unable to generate detailed analysis due to technical issues.",
            "suggestion": "Please try again later."
        }