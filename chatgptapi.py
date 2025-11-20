import os
from constants import OPENAI_APIKEY,OPENAI_MODEL
from openai import OpenAI

# NOTE: You need an OpenAI API key to run this.
# You can get one at https://platform.openai.com/api-keys

# Initialize the client
# Option 1: Hardcode your key (Not recommended for sharing code)
# client = OpenAI(api_key="sk-proj-your-actual-key-here")

# Option 2: Best Practice (Set OPENAI_API_KEY in your environment variables)
# If you set the environment variable, you don't need to pass api_key here.
client = OpenAI(
    api_key=OPENAI_APIKEY
)

def chat_with_gpt(system_prompt, user_prompt):
    # add logic to add retry mechanism
    try:
        # Create the chat completion request
        response = client.responses.create(
            model = OPENAI_MODEL,  # You can also use "gpt-4o" or "gpt-4"
            input = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7, # Controls randomness (0 = strict, 1 = creative)
        )

        # Extract the message content
        return response.output[0].content[0].text 

    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    system_prompt = "You are an expert in log analysis to find the root cause."
    user_prompt = "consider you are a helpful assistant , What is python in 3 lines" #input("Enter your message for ChatGPT: ")
    response = chat_with_gpt(system_prompt, user_prompt)
    print(response)


#Convert this to a class.
