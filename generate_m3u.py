import os
import re
import requests

def get_guest_token():
    try:
        resp = requests.post("https://api.gofile.io/accounts").json()
        return resp["data"]["token"]
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

def get_folder_files(folder_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(f"https://api.gofile.io/contents/{folder_id}", headers=headers).json()
        if resp["status"] != "ok":
            return []
        
        children = resp["data"].get("children", {})
        files = []
        for child_id, child_info in children.items():
            # Filter for video/audio files (or allow all files)
            if child_info["type"] == "file":
                files.append({
                    "name": child_info["name"],
                    "link": child_info["link"]
                })
        return files
    except Exception as e:
        print(f"Error fetching folder {folder_id}: {e}")
        return []

def main():
    input_file = "links.txt"
    output_file = "playlist.m3u"
    
    if not os.path.exists(input_file):
        print(f"{input_file} not found. Skipping.")
        return

    with open(input_file, "r") as f:
        lines = f.readlines()

    m3u_content = ["#EXTM3U"]
    current_group = "Uncategorized"
    token = get_guest_token()

    if not token:
        print("Failed to get GoFile token. Exiting.")
        return

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Assign groups based on the # headers
        if line.startswith("#"):
            current_group = line.lstrip("#").strip()
            continue
        
        # Extract GoFile folder ID
        match = re.search(r'gofile\.io/d/([a-zA-Z0-9]+)', line)
        if match:
            folder_id = match.group(1)
            files = get_folder_files(folder_id, token)
            
            for f_data in files:
                name = f_data["name"]
                # Append the auth token to the direct link so the TV player can bypass access denial
                link = f"{f_data['link']}?token={token}"
                m3u_content.append(f'#EXTINF:-1 group-title="{current_group}",{name}')
                m3u_content.append(link)

    with open(output_file, "w") as f:
        f.write("\n".join(m3u_content))
        
    print("M3U playlist updated successfully.")

if __name__ == "__main__":
    main()
