import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5062")

def register_user(name: str, email: str, password: str) -> dict:
    """Registrera en användare via API."""
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "name": name,
        "email": email,
        "password": password
    })
    return response.json()

def login(email: str, password: str) -> str:
    """Logga in och hämta JWT-token."""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": email,
        "password": password
    })
    data = response.json()
    return data.get("token")

def get_exercises(token: str) -> list:
    """Hämta alla övningar från API."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/exercise", headers=headers)
    return response.json()

def get_workout_sessions(user_id: int, token: str) -> list:
    """Hämta träningspass för en användare."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/workoutsession/user/{user_id}",
        headers=headers
    )
    return response.json()

if __name__ == "__main__":
    print("Testar API-anslutning...")

    
    result = register_user("Test User", "apitest@healthapp.com", "Test1234!")
    print(f"Registrering: {result}")

    
    token = login("apitest@healthapp.com", "Test1234!")
    if token:
        print(f"Inloggning lyckades! Token: {token[:30]}...")

        
        exercises = get_exercises(token)
        print(f"Hämtade {len(exercises)} övningar från API")
    else:
        print("Inloggning misslyckades!")