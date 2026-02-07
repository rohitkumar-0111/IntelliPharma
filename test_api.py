import requests
import json
import sys

def test_chat(message):
    url = "http://127.0.0.1:8000/api/chat"
    payload = {"message": message}
    headers = {"Content-Type": "application/json"}

    print(f"Sending message: '{message}'...")
    try:
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            response.raise_for_status()
            print("Response stream:")
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        print(data)
                    except json.JSONDecodeError:
                        print(f"Raw line: {line.decode('utf-8')}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Is it running? (uvicorn api.index:app --reload)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    msg = "Compare reimbursement for WonderDrug"
    if len(sys.argv) > 1:
        msg = sys.argv[1]
    test_chat(msg)
