from claive_sdk.claive import ChatClaive
from claive_sdk.secret import SecretClaive

secret_client = SecretClaive()
# Get all the models registered with the smart contracts
models = secret_client.get_models()
# For the chosen model you may obtain a list of LLM instance URLs to connect to
urls = secret_client.get_urls(model=models[0])
# You previosly exported the env var CLAIVE_AI_API_KEY=YOUR-API-KEY
claive_llm = ChatClaive(
base_url=urls[0], # in this case we choose to access the first url in the list

model='llama3.1:70b', # your previosly selected model
temperature=1.
)
# Define your messages you want to send to the confidential LLM for processing
messages = [
(
      "system",
      "You are my therapist. Help me with my issues.",
),
("human", "I miss my cat."),
]
# Invoke the llm
response = claive_llm.invoke(messages, stream=False)
print(response.content)