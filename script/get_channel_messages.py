import json
import os
from datetime import datetime
from telethon import TelegramClient, errors
from pathlib import Path

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")


async def get_channel_messages(channel, limit=None):
    try:
        client = TelegramClient("anon", api_id, api_hash)
        await client.start()

        if not await client.is_user_authorized():
            phone = input("Enter your phone number: ")
            await client.send_code_request(phone)
            try:
                await client.sign_in(phone, input("Enter the code: "))
            except errors.SessionPasswordNeededError:
                await client.sign_in(password=input("Password: "))

        messages = []
        async for message in client.iter_messages(channel, limit=limit):
            messages.append(message)

        await client.disconnect()
        return messages
    except (errors.TelegramError, ConnectionError) as e:
        raise e


def save_messages_to_json(messages, dir="./data", include_timestamp=True):
    if not messages:
        print("No messages to save.")
        return

    data = [json.loads(m.to_json(ensure_ascii=False)) for m in messages]
    # add channel info to the data
    # TODO: this is a way to get the channel name

    username = "unknown"
    if messages[0].chat.username:
        username = messages[0].chat.username.lower()
    else:
        timestamp = datetime.utcnow().strftime("%F%T")
        username += timestamp
        print(
            f"No `username` found, using `{username}`. Please adjust the name manually."
        )

    timestamp = datetime.utcnow().strftime("%F") if include_timestamp else ""
    filename = Path(dir) / (
        f"{username}_{timestamp}.json" if timestamp else f"{username}.json"
    )

    try:
        Path(dir).mkdir(exist_ok=True)
        with open(filename, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Messages saved to {filename}")
    except json.JSONDecodeError as e:
        raise e


def get_latest_message_id(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            messages = json.load(file)
            if not messages:
                return None
            # Assuming messages are stored in descending order of IDs
            latest_message = messages[0]
            return latest_message["id"]
    except FileNotFoundError:
        # File not found implies no messages have been saved yet
        return None
    except json.JSONDecodeError as e:
        print(f"Error reading JSON from file: {e}")
        return None


async def fetch_new_messages(channel, file_path):
    client = TelegramClient("anon", api_id, api_hash)
    await client.start()

    # Get the ID of the latest message in the file
    latest_message_id = get_latest_message_id(file_path)

    # Fetch messages newer than the latest message
    new_messages = []
    async for message in client.iter_messages(channel, offset_id=latest_message_id):
        new_messages.append(message)

    await client.disconnect()
    return new_messages


# Example usage:
# asyncio.run(get_channel_messages('channel_name'))
