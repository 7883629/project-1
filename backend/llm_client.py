from typing import Literal

import openai
from openai import OpenAI
from config import PROVIDERS


class LLMClient:

    def __init__(self, model_name: Literal["DEEPSEEK", "ALI"]):
        model = PROVIDERS[model_name]
        self.model_name = model["MODEL"]
        self.price_in_unit = model["PRICE_IN"]
        self.price_out_unit = model["PRICE_OUT"]
        self.total_tokens = 0
        self.total_cost = 0
        self.client = OpenAI(
            api_key=model["KEY"],
            base_url=model["BASE_URL"],

        )

    def chat(self, messages: list[dict], is_json=False) -> str | None:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
            )

            input_price = response.usage.prompt_tokens / 1000000 * self.price_in_unit
            output_price = response.usage.completion_tokens / 1000000 * self.price_out_unit

            total = response.usage.prompt_tokens + response.usage.completion_tokens
            price = round((input_price + output_price), 6)
            self.total_tokens += total
            self.total_cost += price
            print(f"本次使用输入:{input_price:.6f}元----输出:{output_price:.6f}元")
            return response.choices[0].message.content
        except openai.APITimeoutError as e:
            print("请求超时了", e)
            return None
        except openai.RateLimitError as e:
            print("请求受限", e)
            return None
        except openai.AuthenticationError as e:
            print("认证错误", e)
            return None
        except openai.APIError as e:
            print("报错了", e)
            return None

    def stream_chat(self, messages: list[dict]):
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True,
            )

            # input_price = response.usage.prompt_tokens / 1000000 * self.price_in_unit
            # output_price = response.usage.completion_tokens / 1000000 * self.price_out_unit
            #
            # total = response.usage.prompt_tokens + response.usage.completion_tokens
            # price = round((input_price + output_price), 6)
            # self.total_tokens += total
            # self.total_cost += price
            # print(f"本次使用输入:{input_price:.6f}元----输出:{output_price:.6f}元")
            for chunk in stream:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except openai.APITimeoutError as e:
            print("请求超时了", e)
            raise
        except openai.RateLimitError as e:
            print("请求受限", e)
            raise
        except openai.AuthenticationError as e:
            print("认证错误", e)
            raise
        except openai.APIError as e:
            print("报错了", e)
            raise
