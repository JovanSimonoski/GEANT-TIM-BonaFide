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
    Collaboration network generator script.

    Prompts the user for an author name and network depth, then builds
    and visualizes the academic collaboration network using GraphClient.
    Saves results in CSV, JSON, and PNG formats.

    Parameters:
        None

    Returns:
        None
    """
    author_name = input("Enter the starting author name: ")
    # author_name = "Yoshua Bengio"
    max_depth = int(input("Enter the maximum depth to explore (1-3 recommended): "))
    # max_depth = 3

    try:
        print(f"Building collaboration network starting from '{author_name}' with depth {max_depth}...")
        G = GraphClient.build_collaboration_network(author_name, max_depth)

        print(f"\nNetwork statistics:")
        print(f"Number of authors: {G.number_of_nodes()}")
        print(f"Number of collaborations: {G.number_of_edges()}")

        GraphClient.save_edges_to_csv(G, author_name, max_depth)
        GraphClient.save_edges_to_json(G, author_name, max_depth)
        # GraphClient.save_edges_to_sigma_json(G, author_name, max_depth)
        GraphClient.visualize_network(G, author_name, max_depth)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
