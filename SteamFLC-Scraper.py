import asyncio
import aiohttp
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt

class SteamFLCrawler:
    def __init__(self, profile_link):
        self.initial_profile = profile_link

    async def is_friend_list_private(self, profile_link):
        """
        Checks if the friend list of the given profile is private.
        
        Parameters:
            profile_link (str): The link to the Steam profile to check the friend list privacy.
        
        Returns:
            bool: True if the friend list is private, False otherwise.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(profile_link) as response:
                res = await response.text()
        document = BeautifulSoup(res, 'html.parser')

        if document.select_one('.profile_private_info'):
            return True

        if not document.select_one('.profile_friend_links'):
            return True

        return False

    async def get_friend_list(self, profile_link):
        """
        Retrieves the list of friends for a given Steam profile link.

        Parameters:
            profile_link (str): The link to the Steam profile for which the friend list is to be retrieved.

        Returns:
            list: A list of tuples containing the Steam ID and name of each friend.
        """
        if await self.is_friend_list_private(profile_link):
            return None

        friends_page_url = profile_link + "friends/"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(friends_page_url) as response:
                res = await response.text()

        document = BeautifulSoup(res, 'html.parser')

        friend_profiles = []
        for friend in document.select('div.friend_block_v2'):
            steam_id = friend.get('data-steamid')
            friend_name = friend.select_one('.friend_block_content').get_text(strip=True)
            if steam_id and friend_name:
                friend_profiles.append((steam_id, friend_name))

        return friend_profiles

    async def get_friend_lists(self, friends):
        """
        Retrieves the friend lists for a list of friends.

        Args:
            friends (list): A list of tuples containing the Steam ID and name of each friend.

        Returns:
            dict: A dictionary containing the friend lists, where the keys are the Steam IDs and the values are lists of tuples containing the Steam ID and name of each friend.
        """
        friend_lists = {}
        for steam_id, _ in friends:
            profile_url = f"https://steamcommunity.com/profiles/{steam_id}/"
            friend_list = await self.get_friend_list(profile_url)
            if friend_list is not None:
                friend_lists[steam_id] = friend_list
        return friend_lists

async def main():
    profile_link = input("Enter the Steam profile link: ")
    crawler = SteamFLCrawler(profile_link)
    
    initial_friend_list = await crawler.get_friend_list(profile_link)
    if initial_friend_list is None:
        print("Friend list is not available for this profile.")
        return

    friend_lists = await crawler.get_friend_lists(initial_friend_list)

    async with aiohttp.ClientSession() as session:
        async with session.get(profile_link) as response:
            res = await response.text()
    document = BeautifulSoup(res, 'html.parser')
    profile_name = document.select_one('.actual_persona_name').get_text(strip=True)

    G = nx.Graph()
    G.add_node(profile_link, label=profile_name)

    for steam_id, friend_name in initial_friend_list:
        friend_profile = f"https://steamcommunity.com/profiles/{steam_id}/"
        G.add_node(friend_profile, label=friend_name)
        G.add_edge(profile_link, friend_profile)

    for steam_id, friends_of_friend in friend_lists.items():
        friend_profile = f"https://steamcommunity.com/profiles/{steam_id}/"
        for mutual_steam_id, mutual_friend_name in friends_of_friend:
            mutual_friend_profile = f"https://steamcommunity.com/profiles/{mutual_steam_id}/"
            if mutual_friend_profile in G:
                G.add_edge(friend_profile, mutual_friend_profile)

    hide_isolated = input("Do you want to hide friends with no further connections? (yes/no): ").strip().lower()
    if hide_isolated == 'yes' or hide_isolated == 'y':
        isolated_nodes = [node for node, degree in dict(G.degree()).items() if degree == 1 and node != profile_link]
        G.remove_nodes_from(isolated_nodes)

    pos = nx.spring_layout(G)
    labels = nx.get_node_attributes(G, 'label')
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=300, node_color="skyblue", font_size=10, font_color="black", font_weight="bold", edge_color="gray")
    plt.title("Steam Friends Graph")
    plt.show()

if __name__ == "__main__":
    asyncio.run(main())