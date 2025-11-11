from pyvis.network import Network
from neo4j import GraphDatabase

def visualize_graph(
        output_path="outputs/sample_graph.html",
        neo4jauth=None,
        useNeo4j=True,
        relationships=None,
    ):
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="#333333", directed=True)
    nodes = set()
    if useNeo4j:
        relationships = []
        # print(" Connecting to Neo4j and fetching data...")
        driver = GraphDatabase.driver(neo4jauth["uri"], auth=(neo4jauth["user"], neo4jauth["password"]))
        with driver.session() as session:
            query = """
            MATCH (a)-[r]->(b)
            RETURN a.name AS source, type(r) AS rel, b.name AS target
            """
            results = session.run(query)
            for record in results:
                subj, rel, obj = record["source"], record["rel"], record["target"]
                relationships.append((subj, rel, obj))
        driver.close()
    for subj, rel, obj in relationships:
        if subj not in nodes:
            net.add_node(subj, label=subj, shape="dot", size=12, color="#90caf9")
            nodes.add(subj)
        if obj not in nodes:
            net.add_node(obj, label=obj, shape="dot", size=12, color="#ffcc80")
            nodes.add(obj)
        net.add_edge(subj, obj, label=rel, color="#b0bec5", width=1.2, font={"size": 10})
    options = """
    var options = {
        "nodes": {
            "font": {"size": 12, "face": "Arial"},
            "borderWidth": 1,
            "shadow": false
        },
        "edges": {
            "color": {"inherit": false},
            "smooth": true,
            "arrows": {"to": {"enabled": true, "scaleFactor": 0.5}},
            "font": {"size": 10, "align": "middle", "color": "#555"},
            "width": 1
        },
        "physics": {
            "enabled": true,
            "barnesHut": {
                "gravitationalConstant": -8000,
                "centralGravity": 0.25,
                "springLength": 90,
                "springConstant": 0.04
            },
            "minVelocity": 0.75
        }
    }
    """
    net.set_options(options)
    net.write_html(output_path, notebook=False)
    # print(f" Graph visualization saved to {output_path}")
    print(f"\n Success! The graph can now be viewed at {output_path}\n")
    return output_path

# def visualize_from_neo4j(uri, user, password, output_path="outputs/sample_neo4j.html"):
#     print("\n ===== GRAPH VISUALIZATION =====\n")
#     print(" Connecting to Neo4j and fetching data...")
#     driver = GraphDatabase.driver(uri, auth=(user, password))
#     net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="#333333", directed=True)
#     with driver.session() as session:
#         query = """
#         MATCH (a)-[r]->(b)
#         RETURN a.name AS source, type(r) AS rel, b.name AS target
#         """
#         results = session.run(query)
#         nodes = set()
#         for record in results:
#             subj, rel, obj = record["source"], record["rel"], record["target"]
#             if subj not in nodes:

if __name__ == "__main__":
    sample_rels = [
        ("Elon Musk", "founded", "SpaceX"),
        ("Elon Musk", "owns", "Tesla"),
        ("OpenAI", "developed", "ChatGPT"),
        ("Microsoft", "acquired", "GitHub"),
        ("GitHub", "owned by", "Microsoft"),
    ]
    visualize_graph(sample_rels, output_path="outputs/sample_rels.html")