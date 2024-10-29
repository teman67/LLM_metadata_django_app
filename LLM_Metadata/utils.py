import os
import requests

def query_api(messages, model, temperature=0.7, max_tokens=600, top_k=40, top_p=0.9):
    url = os.getenv('API_URL')
    headers = {"Authorization": f"Bearer {os.getenv('API_KEY')}"}
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_k": top_k,
        "top_p": top_p
    }

    response = requests.post(url, json=payload, headers=headers)
    response_json = response.json()

    if response.status_code == 200:
        choice = response_json.get('choices', [])[0].get('message', {}).get('content', '')
        return {
            "content": choice,
            "elapsed_time": response.elapsed.total_seconds(),
            "response_tokens": len(choice.split())
        }
    else:
        return {"error": f"Error: {response.status_code}"}
