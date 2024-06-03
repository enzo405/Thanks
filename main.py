import sys
import os
from dotenv import load_dotenv

from bot.client import Client

if len(sys.argv) > 1 and sys.argv[1] == "prod":
    environment = "prod"
else:
    environment = "dev"

# Load the appropriate .env file
if environment == "dev":
    load_dotenv(".env.local")
else:
    load_dotenv(".env.prod")

Thanks_Bot = Client()

if __name__ == "__main__":
    if environment == "dev":
        print('Dev mode launched running ...')
        Thanks_Bot.run(os.getenv("DEV_TOKEN"))
    elif environment == "prod":
        print('Prod mode launched running ...')
        Thanks_Bot.run(os.getenv("PROD_TOKEN"))
    else:
        print("Invalid environment")