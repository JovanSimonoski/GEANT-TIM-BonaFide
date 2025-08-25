import json
from arxiv_api.clients.graph_client import GraphClient


class GraphGenerator:
    def __init__(self):
        return

    def generate_graph(self, author_name, max_depth):
        graph = GraphClient.build_collaboration_network(author_name, max_depth)
        edge_list = [{"source": u, "target": v} for u, v in graph.edges()]

        return json.dumps(edge_list, indent=2)

