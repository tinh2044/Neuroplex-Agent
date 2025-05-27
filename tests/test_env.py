import os
from dotenv import load_dotenv
load_dotenv()

# for key, value in os.environ.items():
#     print(f"{key}: {value}")

print(os.getenv("OPENAI_API_KEY"))