import asyncio
from get_channel_messages import get_channel_messages, save_messages_to_json


def main():
    channels = [
        "@habzema21",  # -1001335250788"
        "@freelance_ethio",  # -1001193582142
        "@afriworkamharic",  # -1001377094832
        "leulbrkag",
        "Ermyas27",
        "ethiojobsofficial",
        "condoaddis",
        "efoyplus",
        "ETHIOhouseagents"
    ]
    data = {}
    for channel in channels:
        print(f"Fetching messages from {channel=}")
        data[channel] = asyncio.run(get_channel_messages(channel))
        print(f"Fetched {len(data[channel])} messages")
        save_messages_to_json(data[channel])


if __name__ == "__main__":
    main()
