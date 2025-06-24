from agents import Agent, OpenAIChatCompletionsModel, AsyncOpenAI, RunConfig, Runner, function_tool
from dotenv import load_dotenv
import os
import requests
import chainlit as cl

# Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Function to get coin price
@function_tool
def get_coin_price(currency):
    url=f"https://api.binance.com/api/v3/ticker/price?symbol={currency}"
    response = requests.get(url)
    data = response.json()
    return f"The current price of {currency} is {data['price']} USD."

# Openai client setup
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

# Create a RunConfig with the model and client
config = RunConfig(
    model = model,
    model_provider = external_client,
    tracing_disabled = True
)
# Create an agent with the model and function tool
agent = Agent(
    name = "Digital Coins Agent",
    instructions = 
    """ You are a smart crypto assistant. Use tools to fetch real-time prices for cryptocurrencies like BTCUSDT, ETHUSDT, and more. 
        Always provide accurate and clear information based on the latest market data. """,
    tools = [get_coin_price]
)
# Chainlit setup
@cl.on_chat_start
async def start_message():
   await cl.Message(content="💰 Welcome to the world of Crypto Currency! 🚀 Let's get started..").send()
#----------------------------
@cl.on_message
async def my_message(msg: cl.Message):
    user_input = msg.content

    response = Runner.run_sync(agent, user_input,run_config=config)
    await cl.Message(content = response.final_output).send()