from LoadData import load_documents
from ExtractRelationships import extract_relationships
from neo4j_handler import Neo4jHandler
from VisualizeGraph import visualize_graph

if __name__ == "__main__":
    print("\n Starting Entity-Relationship Extraction...")

    folderpath = "data/docs"
    docs = load_documents(folderpath)
    print(f"\n Loaded {len(docs)} documents.\n")

    all_relationships = []

    for filename, text in docs.items():
        print(f" Processing document: {filename}", end=' ')
        rels = extract_relationships(text)
        # print(rels)
        # for subj, rel, obj in rels:
        #     print(f" --- Extracted relationship: {subj} -- {rel} --> {obj}")
        all_relationships.extend(rels)
        print(" ... Completed!")
    
    print("\n Entity and Relationship extraction completed.\n")

    # print("\n Extracting Relationships...")
    # relationships = extract_relationships(text)

    # for r in relationships:
    #     print(f"{r[0]} -- {r[1]} --> {r[2]}")
    
    print(" Connecting to Neo4j...")
    neo4jauth = {
        "uri": "neo4j://127.0.0.1:7687",
        "user": "neo4j",
        "password": "entityrelationships"
    }
    handler = Neo4jHandler(**neo4jauth)

    print(" Uploading to graph...")
    handler.clear_database()
    handler.upload_relationship(all_relationships)
    # for subj, rel, obj in relationships:
    #     neo4j.add_relationship(subj, rel, obj)

    handler.close()
    print("\n Success! Results can be seen in the Neo4j Browser.\n")

    print(" Visualizing the knowledge graph as a HTML file...")
    output_path = "outputs/KnowledgeGraph1.html"
    useNeo4j = True
    if useNeo4j:
        visualize_graph(output_path, neo4jauth)
    else:
        visualize_graph(output_path, useNeo4j=useNeo4j, relationships=all_relationships)