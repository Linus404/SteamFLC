# Steam Friend List Crawler

This Python script crawls a Steam user's friend list and their friends' friend lists to create a network graph visualization. It uses asynchronous programming to efficiently fetch data from Steam profiles and generates a graph showing the connections between friends.

## Features

- Asynchronous crawling of Steam friend lists
- Visualization of friend connections using NetworkX and Matplotlib
- Option to hide isolated nodes (friends with no further connections)
- Handles private profiles and friend lists

## Requirements

- Python 3.7+
- aiohttp
- beautifulsoup4
- networkx
- matplotlib

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/steam-friend-list-crawler.git
   cd steam-friend-list-crawler
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the script:
   ```
   python steam_crawler.py
   ```

2. Enter the Steam profile URL when prompted.

3. Wait for the script to crawl the friend lists and generate the graph.

4. Choose whether to hide isolated nodes when prompted.

5. The graph will be displayed using Matplotlib.

## Note

This script is for educational purposes only. Please be respectful of Steam's terms of service and do not use this script excessively or in a way that could be considered abusive. Currently can't go into more depth because of RecursionError

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.