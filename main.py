import os
import requests
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, function_tool

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is missing in .env file")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

# Function tool calling for crypto price | Pyhton user build function
@function_tool
def crypto_price(symbol: str) -> str:
    """
    Get current price of cryptocurrency.
    """
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"
        response = requests.get(url)
        response.raise_for_status()
        price = response.json()["price"]
        return f"The current price of {symbol.upper()} is **${price}**."
    except Exception as e:
        return f"Failed to fetch price for {symbol.upper()}. Error: {e}"

#Create Agent
crypto_agent = Agent(
    name="Crypto Currency Agent",
    instructions="You are a Crypto currency agent. You provide real-time crypto prices using the Binance API.",
    tools=[crypto_price]
)

results = Runner.run_sync(
    crypto_agent,
    input="What is the price of ETHBTC?",
    run_config= config
    
)

print(results.final_output)