import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Union

def fetch_webpage(url: str) -> str:
    """Fetch the webpage content."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise Exception(f"Error fetching the webpage: {e}")

def preprocess_html(html: str) -> Dict[str, Union[str, List[Dict[str, str]]]]:
    """Preprocess the HTML content and extract relevant information."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove script and style tags
    for script in soup(["script", "style"]):
        script.decompose()
    
    preprocessed_data = {
        "title": soup.title.string if soup.title else "",
        "main_content": soup.get_text(strip=True),
        "buttons": [],
        "videos": [],
        "audios": [],
        "interactive_elements": []
    }
    
    # Extract buttons
    buttons = soup.find_all('button') + soup.find_all('a', class_=re.compile(r'btn|button', re.I))
    for button in buttons:
        preprocessed_data["buttons"].append({
            "text": button.get_text(strip=True),
            "href": button.get('href', ''),
            "id": button.get('id', ''),
            "class": ' '.join(button.get('class', []))
        })
    
    # Extract videos
    videos = soup.find_all('video') + soup.find_all('iframe', src=re.compile(r'youtube|vimeo'))
    for video in videos:
        preprocessed_data["videos"].append({
            "src": video.get('src', ''),
            "title": video.get('title', ''),
            "id": video.get('id', ''),
            "class": ' '.join(video.get('class', []))
        })
    
    # Extract audios
    audios = soup.find_all('audio')
    for audio in audios:
        preprocessed_data["audios"].append({
            "src": audio.get('src', ''),
            "title": audio.get('title', ''),
            "id": audio.get('id', ''),
            "class": ' '.join(audio.get('class', []))
        })
    
    # Extract other interactive elements
    interactive_elements = soup.find_all(['input', 'select', 'textarea'])
    for element in interactive_elements:
        preprocessed_data["interactive_elements"].append({
            "type": element.name,
            "id": element.get('id', ''),
            "name": element.get('name', ''),
            "class": ' '.join(element.get('class', []))
        })
    
    return preprocessed_data

def send_to_venice_llm(preprocessed_data: Dict[str, Union[str, List[Dict[str, str]]]]) -> str:
    """Send preprocessed data to Venice LLM API and return the response."""
    url = "https://api.venice.ai/api/v1/chat/completions"
    
    payload = json.dumps({
        "messages": [
            {
                "role": "system",
                "content": "Please summarize the content of the webpage."
            },
            {
                "role": "user",
                "content": json.dumps(preprocessed_data, indent=2)
            }
        ],
        "model": "nous-hermes-8b"
    })
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer po3YpuVSFKDkwO0S9Yz0NjascEq699ZDbRxv7FYYSS'
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.RequestException as e:
        raise Exception(f"Error calling Venice LLM API: {e}")

def main():
    print("Welcome to the Webpage Content Extractor and Summarizer!")
    
    while True:
        url = input("Please enter a URL (or 'quit' to exit): ").strip()
        
        if url.lower() == 'quit':
            print("Thank you for using the Webpage Content Extractor and Summarizer. Goodbye!")
            break
        
        try:
            print("Fetching webpage content...")
            html_content = fetch_webpage(url)
            
            print("Preprocessing HTML content...")
            preprocessed_data = preprocess_html(html_content)
            
            print("Sending preprocessed data to Venice LLM API...")
            summary = send_to_venice_llm(preprocessed_data)
            
            print("\nWebpage Summary:")
            print(summary)
            print("\n" + "="*50 + "\n")
        
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again with a different URL.")
        
        print()

if __name__ == "__main__":
    main()
