from huggingface_hub import InferenceClient
from decouple import config

client = InferenceClient(
	provider="together",
	api_key=config("HF_API_KEY")
)

def send_prompt(user_message: str) -> str:
	messages = [
		{
			"role": "user",
			"content": f"{user_message}"
		},
		{
			"role": "assistant",
			"content": "You are a car maintenance expert. Answer only about vehicle repairs, maintenance, or related topics. Refuse to answer any unrelated questions.I want the answer to be like this form:\n cost: (your answer here)\n reason: (your answer here)\n time to fix: (your answer here)\n possibilities: (your answer here)\n note that i want the reason to be just one or two words, the cost just a number with no range values,the time to fix field give it to me in mintues and it starts from 120 mintues to 300 minutes and send just the number, and no limit for the possibilities"
		}
	]

	completion = client.chat.completions.create(
		model="meta-llama/Llama-3.3-70B-Instruct", 
		messages=messages, 
		temperature=0.5,
		max_tokens=256,
		top_p=0.7,
	)

	return completion.choices[0].message.content


def fetch_prompt_info(ai_response: str) -> dict:
	data = ai_response.split("\n")
	final_response = {}

	for info in data:
		[key, value] = info.split(":")
		final_response[key.strip()] = value.strip()

	return final_response	



print(fetch_prompt_info(send_prompt("i have oil leaks")).get("time to fix"))   