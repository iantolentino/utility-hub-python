import requests

BOT_TOKEN = "YOUR TOKEM"
CHAT_ID = "YOUR CHAT ID"


def send_message(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()


def collect_moods():
    moods = []
    print("Enter 5 moods:")

    for i in range(5):
        mood = input(f"Mood {i + 1}: ").strip()
        moods.append(mood)

    return moods


def format_message(moods):
    lines = ["🧠 Daily Mood Report", ""]
    for mood in moods:
        lines.append(f"- {mood}")

    return "\n".join(lines)


if __name__ == "__main__":
    moods = collect_moods()
    message = format_message(moods)
    send_message(message)
    print("Message sent successfully.")
