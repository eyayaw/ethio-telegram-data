import asyncio
import json
import os
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")


async def get_channel_messages(channel, limit=None):
    # Create the client and connect
    client = TelegramClient("anon", api_id, api_hash)
    await client.start()

    # Ensure authorized
    if await client.is_user_authorized() == False:
        phone = input("Enter your phone number: ")
        await client.send_code_request(phone)

        try:
            await client.sign_in(phone, input("Enter the code: "))
        except SessionPasswordNeededError:
            await client.sign_in(password=input("Password: "))

    # Fetching the messages
    messages = []
    async for message in client.iter_messages(channel, limit=limit):
        messages.append(message)

    await client.disconnect()
    return messages


def save_messages_to_json(messages, dir="./data", include_timestamp=True):
    # Save messages to JSON file
    data = []
    for message in messages:
        # Convert each message to JSON string and write to file
        data.append(json.loads(message.to_json(ensure_ascii=False)))

    # Create a file name
    username = messages[0].chat.username.lower()
    title = messages[0].chat.title.title()
    channel_name = f"{username}_{title}"

    timestamp = datetime.utcnow().strftime("%F") if include_timestamp else ""
    filename = (
        f"{channel_name}_{timestamp}.json" if timestamp else f"{channel_name}.json"
    )

    # Prepend dirname
    os.makedirs(dir, exist_ok=True)
    filename = os.path.join(dir, filename)

    with open(filename, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Messages saved to {filename}")
