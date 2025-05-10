def fetch_prompt_info(ai_response: str) -> dict:
    data = ai_response.split("\n")
    final_response = {}

    for info in data:
        [key, value] = info.split(":")  
        final_response[key.strip()] = value.strip()


    return final_response


