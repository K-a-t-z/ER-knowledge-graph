from neo4j import GraphDatabase
import networkx as nx
import matplotlib.pyplot as plt

class GraphVisualizer:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def fetch_graph_data(self):
        query = """
        MATCH (a:Entity)-[r:RELATION]->(b:Entity)
        RETURN a.name AS source, a.type AS source_type,
               r.type AS relation,
               b.name AS target, b.type AS target_type
        """
        with self.driver.session() as session:
            results = session.run(query)
            data = [record.data() for record in results]
        return data
    
    def build_network(self, data):
        G = nx.DiGraph()
        for record in data:
            s, stype = record['source'], record['source_type']
            t, ttype = record['target'], record['target_type']
            rel = record['relation']
            G.add_node(s, label=stype)
            G.add_node(t, label=ttype)
            G.add_edge(s, t, label=rel)
        return G
    
    def plot_graph(self, G):
        pos = nx.spring_layout(G, seed=42)

        node_colors = []
        for node, attrs in G.nodes(data=True):
            node_type = attrs.get("label", "")
            node_colors.append(self.color_for_type(node_type))
        
        plt.figure(figsize=(10, 7))
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=900)
        nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=15)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")

        edge_labels = nx.get_edge_attributes(G, "label")
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="gray")

        plt.axis("off")
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def color_for_type(label):
        colors = {
            "PERSON": "#1f77b4",
            "ORG": "#ff7f0e",
            "GPE": "#2ca02c",
            "TECH": "#9467bd",
        }
        return colors.get(label, "#7f7f7f")

if __name__ == "__main__":

    uri = "neo4j://127.0.0.1:7687"
    user = "neo4j"
    password = "entityrelationships"

    visualizer = GraphVisualizer(uri, user, password)
    data = visualizer.fetch_graph_data()
    G = visualizer.build_network(data)
    visualizer.plot_graph(G)
    visualizer.close()