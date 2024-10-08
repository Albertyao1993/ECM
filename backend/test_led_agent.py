import logging
import traceback
import json
from Agents.led_agent import LEDAgent

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        # 创建 LEDAgent 实例
        agent = LEDAgent()
        
        # 测试参数
        light_value = 1.67
        duration = 2.8

        # 运行分析
        result = agent.analyze_and_suggest(light_value, duration)
        
        # 打印结果
        print("Analysis Result:")
        print(json.dumps(result, indent=2))

    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    main()