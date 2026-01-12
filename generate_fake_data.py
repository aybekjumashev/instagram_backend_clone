import requests
import random
from faker import Faker
import time

BASE_URL = "http://localhost:8000/api" 
NUM_USERS = 5 
NUM_POSTS = 10
NUM_ACTIVITIES = 20

fake = Faker()
created_users = []
created_posts = []

def print_status(message, status_code=None, details=None):
    if status_code and status_code in [200, 201]:
        print(f"✅ {message}")
    elif status_code:
        print(f"❌ {message} (Status: {status_code}) {details}")
    else:
        print(f"ℹ️ {message}")

def create_users():
    print("\n--- 1. PAYDALANIWSHILAR JARATILMAQTA ---")
    for _ in range(NUM_USERS):
        profile = {
            "username": fake.unique.user_name(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "password": "Qazwsx987!",
            "password_confirm": "Qazwsx987!"
        }

        response = requests.post(f"{BASE_URL}/auth/register/", json=profile)
        
        if response.status_code == 201:
            login_data = {"username": profile['username'], "password": "Qazwsx987!"}
            auth_resp = requests.post(f"{BASE_URL}/auth/token/", json=login_data)
            
            if auth_resp.status_code == 200:
                token = auth_resp.json()['access']
                created_users.append({
                    "id": response.json()['id'],
                    "username": profile['username'],
                    "token": token,
                    "header": {"Authorization": f"Bearer {token}"}
                })
                print_status(f"User jaratıldı: {profile['username']}", 201)
            else:
                print_status(f"Login qáte: {profile['username']}", auth_resp.status_code, auth_resp.text)
        else:
            print_status(f"Register qáte: {profile['username']}", response.status_code, response.text)

def create_posts():
    print("\n--- 2. POSTLAR JARATILMAQTA ---")
    if not created_users:
        print("Paydalanıwshılar joq!")
        return

    for i in range(NUM_POSTS):
        user = random.choice(created_users)
        
        image_content = requests.get(f"https://picsum.photos/600/400?random={i}").content
        
        files = {
            'image': ('random_image.jpg', image_content, 'image/jpeg')
        }
        data = {
            'caption': fake.sentence()
        }

        response = requests.post(
            f"{BASE_URL}/posts/", 
            headers=user['header'], 
            data=data,
            files=files
        )

        if response.status_code == 201:
            post_id = response.json()['id']
            created_posts.append(post_id)
            print_status(f"Post jaratıldı (User: {user['username']}, ID: {post_id})", 201)
        else:
            print_status(f"Post qáte", response.status_code)

def generate_activity():
    print("\n--- 3. AKTIVLIK (LIKE, COMMENT, FOLLOW) ---")
    if not created_users or not created_posts:
        return

    for _ in range(NUM_ACTIVITIES):
        user = random.choice(created_users)
        action_type = random.choice(['like', 'comment', 'follow'])

        if action_type == 'like':
            post_id = random.choice(created_posts)
            response = requests.post(f"{BASE_URL}/posts/{post_id}/like/", headers=user['header'])
            if response.status_code in [200, 201]:
                print(f"👍 {user['username']} -> Post {post_id} ge like bastı.")

        elif action_type == 'comment':
            post_id = random.choice(created_posts)
            comment_data = {"text": fake.text(max_nb_chars=50)}
            response = requests.post(f"{BASE_URL}/posts/{post_id}/comment/", json=comment_data, headers=user['header'])
            if response.status_code == 201:
                print(f"💬 {user['username']} -> Post {post_id} ge kommentariy jazdı.")

        elif action_type == 'follow':
            target_user = random.choice(created_users)
            if target_user['id'] != user['id']:
                response = requests.post(f"{BASE_URL}/users/{target_user['id']}/follow/", headers=user['header'])
                if response.status_code == 200:
                    print(f"➕ {user['username']} -> {target_user['username']} ǵa jazıldı.")

if __name__ == "__main__":
    try:
        requests.get(BASE_URL)
        
        create_users()
        create_posts()
        generate_activity()
        
        print("\n🎉 Skript jumısı tamamlandı!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Qátelik: Server (Django) islemey atır. 'docker-compose up' yamasa 'runserver' qılıń.")