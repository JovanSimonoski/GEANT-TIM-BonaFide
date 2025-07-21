from clients.graph_client import GraphClient

"""
      |   
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""


def main():
    """
    Researcher connections finder script.

    Loads collaboration networks from CSV files and prompts the user
    for two researcher names, then uses GraphClient to find and display
    the shortest collaboration path between them if present.

    Parameters:
        None

    Returns:
        None
    """
    G = GraphClient.load_all_csv_edges()

    print("\nResearcher Connection Finder")
    author1 = input("Enter the first researcher's name: ").strip()
    author2 = input("Enter the second researcher's name: ").strip()

    GraphClient.find_connection(G, author1, author2)


if __name__ == "__main__":
    main()
