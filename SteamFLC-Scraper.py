import asyncio
import aiohttp
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor

class SteamFLCrawler:
    def __init__(self, profile_link):
        self.initial_profile = profile_link
        self.session = None

    async def create_session(self):
        self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def fetch_url(self, url):
        async with self.session.get(url) as response:
            return await response.text()

    async def is_friend_list_private(self, profile_link):
        res = await self.fetch_url(profile_link)
        document = BeautifulSoup(res, 'html.parser')

        if document.select_one('.profile_private_info'):
            return True

        if not document.select_one('.profile_friend_links'):
            return True

        return False

    async def get_friend_list(self, profile_link):
        if await self.is_friend_list_private(profile_link):
            return None

        friends_page_url = profile_link + "friends/"
        res = await self.fetch_url(friends_page_url)
        document = BeautifulSoup(res, 'html.parser')

        friend_profiles = []
        for friend in document.select('div.friend_block_v2'):
            steam_id = friend.get('data-steamid')
            friend_name = friend.select_one('.friend_block_content').get_text(strip=True)
            if steam_id and friend_name:
                friend_profiles.append((steam_id, friend_name))

        return friend_profiles

    async def get_friend_lists(self, friends):
        tasks = []
        for steam_id, _ in friends:
            profile_url = f"https://steamcommunity.com/profiles/{steam_id}/"
            tasks.append(self.get_friend_list(profile_url))

        results = await asyncio.gather(*tasks)
        return {steam_id: friend_list for (steam_id, _), friend_list in zip(friends, results) if friend_list is not None}

async def main():
    profile_link = input("Enter the Steam profile link: ")
    crawler = SteamFLCrawler(profile_link)
    
    await crawler.create_session()

    initial_friend_list = await crawler.get_friend_list(profile_link)
    if initial_friend_list is None:
        print("Friend list is not available for this profile.")
        await crawler.close_session()
        return

    friend_lists = await crawler.get_friend_lists(initial_friend_list)

    res = await crawler.fetch_url(profile_link)
    document = BeautifulSoup(res, 'html.parser')
    profile_name = document.select_one('.actual_persona_name').get_text(strip=True)

    await crawler.close_session()

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

    # Use a separate thread for plotting to avoid blocking the event loop
    with ThreadPoolExecutor() as executor:
        executor.submit(plot_graph, G, profile_link)

def plot_graph(G, profile_link):
    pos = nx.spring_layout(G)
    labels = nx.get_node_attributes(G, 'label')
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=300, node_color="skyblue", font_size=10, font_color="black", font_weight="bold", edge_color="gray")
    plt.title("Steam Friends Graph")
    plt.show()

if __name__ == "__main__":
    asyncio.run(main())