import requests
import time

def fetch_server_data(protocol, version, alternate=False):
    domain = "growtopia2" if alternate else "growtopia1"
    url = f"https://www.{domain}.com/growtopia/server_data.php"

    print(f"Fetching server data from {domain}.com")

    headers = {
        "User-Agent": "UbiServices_SDK_2022.Release.9_PC64_ansi_static",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = f"platform=0&protocol={protocol}&version={version}"
    try:
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code != 200:
            print(f"Failed to fetch server data from {domain}.com, status code: {response.status_code}")
            time.sleep(1)
            return fetch_server_data(protocol, version, not alternate)
        
        data_text = response.text
        print(f"Server data fetched successfully from {domain}.com")
        return parse_server_data(data_text)
        
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        time.sleep(1)
        return fetch_server_data(protocol, version, not alternate)
    
def parse_server_data(data):
    lines = data.split('\n')
    result = {}
    
    for line in lines:
        idx = line.find('|')
        if idx > -1:
            key = line[:idx].strip()
            value = line[idx + 1:].strip()
            result[key] = value
    
    return result