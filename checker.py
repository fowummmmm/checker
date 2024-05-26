import requests
import time
from bs4 import BeautifulSoup

# Define the headers
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.7",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": '"Brave";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "sec-gpc": "1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

# Define the main Discord webhook URL
main_webhook_url = 'https://discord.com/api/webhooks/1244077498153828382/6N_-MIhUYr6LDToRammQK63pACkb2p2PEsbS-UjYgusDdDxXlLundVuQC6i1OuwjXqj8'

# Define the webhook URL for deleted usernames
deleted_webhook_url = 'https://discord.com/api/webhooks/1244092210811506729/alGe7JOX3nY08Uq2AHsIqBaz7cox4mrxplj29sk3PaUG3ObOEP0Cfa7PIMna5Uek2a0t'

def check_user_status(username):
    url = f"https://plancke.io/hypixel/player/stats/{username}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check if the user is online
        status_tag = soup.find('h4', string='Status')
        if status_tag and 'Offline' not in status_tag.find_next_sibling('b').text:
            # User is online
            server_type, mode = get_server_and_mode(soup)
            social_media = get_social_media(soup)
            stats = get_user_stats(soup)
            
            send_discord_message(username, server_type, mode, social_media, stats)
        else:
            print(f"User {username} is offline")
    elif response.status_code == 404:
        print(f"User {username} not found. Deleting from message.txt...")
        delete_username_from_file(username)
        send_deleted_message(username)
    else:
        print(f"Failed to retrieve data for {username}. Status code: {response.status_code}")

def delete_username_from_file(username):
    with open('message.txt', 'r') as file:
        lines = file.readlines()
    with open('message.txt', 'w') as file:
        for line in lines:
            if line.strip() != username:
                file.write(line)

def send_deleted_message(username):
    data = {
        "content": f"Deleted username {username} from message.txt because it was not found on Hypixel."
    }
    response = requests.post(deleted_webhook_url, json=data)
    if response.status_code == 204:
        print(f"Successfully sent deleted message for {username}")
    else:
        print(f"Failed to send deleted message for {username}. Status code: {response.status_code}")

def get_server_and_mode(soup):
    server_type = 'N/A'
    mode = 'N/A'
    
    status_div = soup.find('div', class_='card-box m-b-10')
    if status_div:
        server_type_text = status_div.find('b', string='ServerType:')
        if server_type_text:
            server_type = server_type_text.next_sibling.strip()
        
        mode_text = status_div.find('b', string='Mode:')
        if mode_text:
            mode = mode_text.next_sibling.strip()
    
    return server_type, mode

def get_social_media(soup):
    social_media = 'N/A'
    social_media_links = []
    
    social_media_section = soup.find('div', class_='card-box m-b-10')
    if social_media_section and social_media_section.find('h4', string='Social Media'):
        links = social_media_section.find_all('a')
        for link in links:
            social_media_links.append(f"{link['id'].replace('social_', '')}: {link['href']}")
    
    if social_media_links:
        social_media = '\n'.join(social_media_links)
    
    return social_media

def get_user_stats(soup):
    stats = {
        'rank_history': 'N/A',
        'multiplier': 'N/A',
        'level': 'N/A',
        'karma': 'N/A',
        'achievement_points': 'N/A',
        'quests_completed': 'N/A',
        'ranks_gifted': 'N/A',
        'first_login': 'N/A',
        'last_login': 'N/A'
    }
    
    player_info_div = soup.find('div', class_='card-box m-b-10')
    if player_info_div and player_info_div.find('h3', string='Player Information'):
        rank_history = player_info_div.find('b', string='Rank History')
        if rank_history:
            rank_history = rank_history.find_next('li')
            if rank_history:
                stats['rank_history'] = rank_history.text.strip()
        
        for key in stats.keys():
            if key != 'rank_history':
                stat = player_info_div.find('b', string=f'{key.replace("_", " ").title()}:')
                if stat:
                    stats[key] = stat.next_sibling.strip()
    
    return stats

def send_discord_message(username, server_type, mode, social_media, stats):
    message_content = "@everyone\n"  # Mention everyone at the beginning of the message
    
    embed = {
        "title": f"{username} is online!",
        "fields": [
            {"name": "Server Type", "value": server_type, "inline": True},
            {"name": "Mode", "value": mode, "inline": True},
            {"name": "Social Media", "value": social_media, "inline": False},
            {"name": "Multiplier", "value": stats['multiplier'], "inline": True},
            {"name": "Level", "value": stats['level'], "inline": True},
            {"name": "Karma", "value": stats['karma'], "inline": True},
            {"name": "Achievement Points", "value": stats['achievement_points'], "inline": True},
            {"name": "Quests Completed", "value": stats['quests_completed'], "inline": True},
            {"name": "Ranks Gifted", "value": stats['ranks_gifted'], "inline": True},
        ],
        "color": 3066993  # Discord embed color code for green
    }

    data = {
        "content": message_content,  # Include @everyone in the message content
        "embeds": [embed]  # Include the embed in the message
    }

    response = requests.post(main_webhook_url, json=data)
    if response.status_code == 204:
        print(f"Successfully sent message for {username}")
    else:
        print(f"Failed to send message for {username}. Status code: {response.status_code}")

def main():
    while True:
        with open('message.txt') as f:
            usernames = f.read().splitlines()

        for username in usernames:
            check_user_status(username)
            time.sleep(5)  # Wait for 5 seconds before checking the next user

if __name__ == "__main__":
    main()

