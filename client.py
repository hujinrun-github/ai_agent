from openai import OpenAI
import os

class OpenAICompatibleClient:
    """
    一个用于调用任何兼容OpenAI接口的LLM服务的客户端。
    """
    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        print("init openai")
        # 设置环境变量
        os.environ['OPENAI_API_KEY'] = api_key
        os.environ['OPENAI_BASE_URL'] = base_url

        # 尝试不同的初始化方式
        try:
            # 先尝试新的方式
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            print(f"成功使用新方式初始化，base_url: {base_url}")
        except TypeError as e:
            print(f"新方式失败: {e}")
            # 新方式失败，尝试旧方式
            try:
                from httpx import Client
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=base_url,
                    http_client=Client(
                        base_url=base_url,
                        headers=headers
                    )
                )
                print(f"成功使用旧方式初始化")
            except Exception as e2:
                print(f"所有初始化方式都失败: {e2}")
                raise

    def generate(self, prompt: str, system_prompt: str) -> str:
        """调用LLM API来生成回应。"""
        print("正在调用大语言模型...")
        try:
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            answer = response.choices[0].message.content
            print("大语言模型响应成功。")
            return answer
        except Exception as e:
            print(f"调用LLM API时发生错误: {e}")
            return "错误:调用语言模型服务时出错。"
