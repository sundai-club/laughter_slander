import openai
import os

# from env var
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_text(file_path, prompt):
    # Read the content of the .txt file
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Combine the file content with the customized prompt
    combined_prompt = f"{prompt}\n\n{file_content}"

    # Make the API call
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Specify the model you want to use
        messages=[
            {"role": "system", "content": "You are an assistant that analyzes text."},
            {"role": "user", "content": combined_prompt}
        ],
        max_tokens=1500,  # Adjust the number of tokens as needed
        temperature=0.7  # Adjust the temperature for creativity
    )

    # Return the response text
    return response.choices[0].message['content'].strip()

# Customize your prompt
custom_prompt = "Here is the text of a conversation and every time someoone laughs there is a [laugh] tag. Try to summarize the jokes before each [laugh] tag and output a json file with the jokes.The result json should only have the list of joke_1, joke_2 to indicate the joke order. "

# Specify the path to your .txt file
file_path = "./full_transcription.txt"

# Get the analysis from the API
response_text = analyze_text(file_path, custom_prompt)
output_file = "fulljoke.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(response_text)
