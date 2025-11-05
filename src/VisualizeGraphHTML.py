from neo4j import GraphDatabase
from pyvis.network import Network

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
        net = Network(height="700px", width="100%", bgcolor="#ffffff", directed=True)
        # G = nx.DiGraph()

        for record in data:
            s, stype = record['source'], record['source_type']
            t, ttype = record['target'], record['target_type']
            rel = record['relation']
            net.add_node(s, label=s, title=stype, color=self.color_for_type(stype))
            net.add_node(t, label=t, title=ttype, color=self.color_for_type(ttype))
            net.add_edge(s, t, label=rel, title=rel)
        net.repulsion(node_distance=180, spring_length=200)
        return net
    
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
    net = visualizer.build_network(data)
    visualizer.close()

    output_file = "data/graph_visualization.html"
    net.write_html(output_file, open_browser=False)

    print(f"Interactive Graph visualization saved to {output_file}")