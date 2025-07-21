import os.path

import networkx as nx
import matplotlib.pyplot as plt
import csv
import json
from arxiv_api.clients.arxiv_client import ArxivClient
from collections import deque

"""
      |   
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""


class GraphClient:
    """
    A client for building and analyzing academic collaboration networks using ArXiv publication data.
    """

    def __init__(self):
        """
        Initialize the GraphClient with an ArxivClient instance for publication searches.

        Parameters:
            None

        Returns:
            None
        """
        self.arxiv_client = ArxivClient()

    @staticmethod
    def build_collaboration_network(start_author, max_depth=2):
        """
        Build a collaboration network graph by exploring co-authorship relationships from a starting author.

        Parameters:
            start_author (str): The full name of the author to begin network exploration from.
                               Should match ArXiv author name formatting for optimal results.
            max_depth (int): Maximum degrees of separation to explore from the starting author
                           (default: 2). Higher values result in exponentially larger networks.

        Returns:
            nx.Graph: NetworkX graph object representing the collaboration network where:
                     - Nodes represent individual authors
                     - Edges represent co-authorship relationships
                     - Graph includes all authors within max_depth collaborations
                     Returns empty graph if starting author has no publications or network errors occur.
        """
        G = nx.Graph()
        processed_authors = set()
        queue = deque([(start_author, 0)])

        while queue:
            current_author, depth = queue.popleft()

            if current_author in processed_authors:
                continue

            processed_authors.add(current_author)
            print(f"Processing author: {current_author} (depth {depth})")

            if not G.has_node(current_author):
                G.add_node(current_author)

            if depth >= max_depth:
                continue

            results = ArxivClient.search_arxiv_publications(current_author)

            if not results:
                continue

            for r in results:
                coauthors = ArxivClient.get_coauthors(r)

                for coauthor in coauthors:
                    if coauthor != current_author:
                        G.add_edge(current_author, coauthor)

                        if coauthor not in processed_authors:
                            queue.append((coauthor, depth + 1))

        return G

    @staticmethod
    def visualize_network(G, author, max_depth):
        """
        Generate and save a visual representation of the collaboration network as a PNG image.

        Parameters:
            G (nx.Graph): The collaboration network graph from build_collaboration_network.
                         Should contain nodes and edges representing author relationships.
            author (str): The starting author name used for filename generation.
                         Special characters and spaces will be removed for file compatibility.
            max_depth (int): The depth parameter used in network construction for filename labeling.

        Returns:
            None: Creates and saves a high-resolution network visualization to '../images_database/'
                 with filename format 'collaboration_network_[author]_depth_[depth].png'.
                 Displays the graph and prints save confirmation message.
        """
        plt.figure(figsize=(50, 25))
        pos = nx.spring_layout(G, seed=42, k=0.3, iterations=100)

        nx.draw(G, pos,
                with_labels=True,
                node_color='skyblue',
                node_size=300,
                edge_color='gray',
                font_size=9,
                width=0.8,
                alpha=0.8)

        plt.title("Author Collaboration Network", fontsize=16)
        plt.tight_layout()
        plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.05)

        filename = "../images_database/" + "collaboration_network_" + author.replace(" ", "") + "_depth_" + str(
            max_depth) + ".png"
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        plt.savefig(filename, dpi=300)
        print(f"Graph image saved as {filename}")

        plt.show()
        plt.close()

    @staticmethod
    def save_edges_to_csv(G, author, max_depth):
        """
        Export collaboration network edges to a CSV file for external analysis or data sharing.

        Parameters:
            G (nx.Graph): The collaboration network graph containing author relationships.
                         Graph should have valid nodes and edges.
            author (str): The starting author name for filename generation.
                         Spaces will be removed for file system compatibility.
            max_depth (int): The network depth parameter for filename labeling.

        Returns:
            None: Creates CSV file in '../csv_database/' directory with format
                 'collaboration_network_[author]_depth_[depth].csv' containing
                 two columns: 'Author1' and 'Author2' representing each collaboration edge.
                 Prints confirmation message with full file path.
        """
        filename = "../csv_database/" + "collaboration_network_" + author.replace(" ", "") + "_depth_" + str(
            max_depth) + ".csv"
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Author1", "Author2"])

            for u, v in G.edges():
                writer.writerow([u, v])

        print(f"Collaboration edges saved to {filename}")

    @staticmethod
    def save_edges_to_json(G, author, max_depth):
        """
        Export collaboration network edges to a JSON file with source-target format for web visualization.

        Parameters:
            G (nx.Graph): The collaboration network graph to export.
                         Must contain valid nodes and edge relationships.
            author (str): The starting author name for filename generation.
                         Spaces removed automatically for file naming.
            max_depth (int): The network exploration depth for filename identification.

        Returns:
            None: Creates JSON file in '../json_database/' with structure containing
                 array of objects with 'source' and 'target' fields for each collaboration.
                 File saved as 'collaboration_network_[author]_depth_[depth].json'.
                 Prints save confirmation message.
        """
        filename = "../json_database/" + "collaboration_network_" + author.replace(" ", "") + "_depth_" + str(
            max_depth) + ".json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        edge_list = [{"source": u, "target": v} for u, v in G.edges()]

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(edge_list, f, indent=2)

        print(f"Collaboration edges saved to {filename}")

    @staticmethod
    def save_edges_to_sigma_json(G, author, max_depth):
        """
        Export collaboration network in Sigma.js compatible JSON format for interactive web visualization.

        Parameters:
            G (nx.Graph): The collaboration network graph for export.
                         Should contain author nodes and collaboration edges.
            author (str): The starting author name for filename generation.
                         Processed to remove spaces for file system compatibility.
            max_depth (int): The network depth parameter for filename labeling.

        Returns:
            None: Creates Sigma.js format JSON file containing 'nodes' array with id/label fields
                 and 'edges' array with id/source/target fields. Saved to '../sigma_json_database/'
                 as 'collaboration_network_[author]_depth_[depth].json'.
                 Overwrites basic JSON format. Prints confirmation message.
        """
        filename = "../sigma_json_database/" + "collaboration_network_" + author.replace(" ", "") + "_depth_" + str(
            max_depth) + ".json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        data = {
            "nodes": [{"id": node, "label": node} for node in G.nodes()],
            "edges": [{"id": f"{u}_{v}", "source": u, "target": v} for u, v in G.edges()]
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Collaboration edges saved to {filename}")

    @staticmethod
    def load_all_csv_edges(csv_folder="../csv_database"):
        """
        Load and combine multiple CSV edge files into a single collaboration network graph.

        Parameters:
            csv_folder (str): Path to directory containing CSV files with collaboration edges
                             (default: "../csv_database"). Files should have 'Author1,Author2' format
                             with header row.

        Returns:
            nx.Graph: Combined NetworkX graph containing all edges from CSV files where:
                     - Nodes represent unique authors across all files
                     - Edges represent all collaboration relationships found
                     - Duplicate edges are automatically merged
                     Returns empty graph if no valid CSV files found or folder doesn't exist.
        """
        G = nx.Graph()

        for filename in os.listdir(csv_folder):
            if filename.endswith(".csv"):
                filepath = os.path.join(csv_folder, filename)
                print(f"Loading edges from {filename}...")

                with open(filepath, newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)

                    for row in reader:
                        if len(row) == 2:
                            G.add_edge(row[0], row[1])

        print(f"\nTotal nodes: {G.number_of_nodes()}")
        print(f"Total edges: {G.number_of_edges()}")
        return G

    @staticmethod
    def find_connection(G, author1, author2):
        """
        Find and display the shortest collaboration path between two authors in the network.

        Parameters:
            G (nx.Graph): The collaboration network graph to search within.
                         Must contain both authors as nodes for successful path finding.
            author1 (str): The first author's full name as it appears in the network.
                          Name matching is case-sensitive and must be exact.
            author2 (str): The second author's full name for connection endpoint.
                          Must exist as a node in the graph.

        Returns:
            None: Prints the shortest collaboration path between authors showing each intermediary,
                 degrees of separation count, or appropriate error messages if:
                 - Either author is not found in the network
                 - No connection path exists between the authors
                 Does not return a value but provides console output with results.
        """
        if not G.has_node(author1):
            print(f"Author '{author1}' not found in the network.")
            return

        if not G.has_node(author2):
            print(f"Author '{author2}' not found in the network.")
            return

        try:
            path = nx.shortest_path(G, source=author1, target=author2)
            print(f"\nConnection found between '{author1}' and '{author2}':")
            for i, author in enumerate(path):
                if i == 0:
                    print(f"  {author}")
                else:
                    print(f"    {author}")
            print(f"\nDegrees of separation: {len(path) - 1}")
        except nx.NetworkXNoPath:
            print(f"No connection found between '{author1}' and '{author2}'.")
