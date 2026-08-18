import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

def main():
    load_dotenv()

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    if len(sys.argv) < 2:
        print("i need a prompt!!")
        sys.exit(1)
    prompt = sys.argv[1]
    verbose_flag = False
    if len(sys.argv) == 3 and sys.argv[2] == "--verbose":
        verbose_flag=True
    prompt = sys.argv[1]

    messages=[types.Content(role="user", parts=[types.Part(text=prompt)]),]

    # response = client.models.generate_content(
    #     model="gemini-2.5-flash",
    #     contents="Why is water blue? use 3 line max"
    # )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
    )

    usage = response.usage_metadata

    if verbose_flag:
        print(f"User prompt : {prompt}")
        print(f"Input Tokens : {usage.prompt_token_count}")
        print(f"Output Tokens: {usage.candidates_token_count}")
        print(f"Total Tokens : {usage.total_token_count}")

    print(response.text)

    

main()