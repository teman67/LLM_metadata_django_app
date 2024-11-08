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

    try:
        response_json = response.json()  # Try to parse JSON response
    except requests.exceptions.JSONDecodeError:
        # Print and handle the response if it’s not JSON
        print("Non-JSON response received:", response.text)
        return {"error": f"Non-JSON response: {response.text}", "status_code": response.status_code}

    if response.status_code == 200:
        choice = response_json.get('choices', [])[0].get('message', {}).get('content', '')
        return {
            "content": choice,
            "elapsed_time": response.elapsed.total_seconds(),
            "response_tokens": len(choice.split())
        }
    else:
        error_message = response_json.get('error', 'Unknown error occurred')
        return {"error": f"Error: {error_message}", "status_code": response.status_code}