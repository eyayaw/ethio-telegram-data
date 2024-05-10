import asyncio
from get_channel_messages import get_channel_messages, save_messages_to_json


def main():
    channels = [
        # "@freelance_ethio",
        # "@afriworkamharic",
        # "ethiojobsofficial",
        # "sera7",
        # "effoyjobs",
        # "hahujobs",
        # "ethio_jobs",
        # "bigdreamET",

        # "leulbrkag",
        # "Ermyas27",
        # "condoaddis",
        # "efoyplus",
        # "ETHIOhouseagents",
        # "EthiopianHouses",
        # "LiveEthio",

        # "Car_For_Sale_In_Addis",
        
        # "@habzema21",
        # "fanatelevision"
    ]
    data = {}
    for channel in channels:
        print(f"Fetching messages from {channel=}")
        data[channel] = asyncio.run(get_channel_messages(channel))
        print(f"Fetched {len(data[channel])} messages")
        save_messages_to_json(data[channel])


if __name__ == "__main__":
    main()
