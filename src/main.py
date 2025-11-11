from data_loader import load_documents
# from ExtractEntities import extract_entities
from ExtractRelationships import extract_relationships
from neo4j_handler import Neo4jHandler
# from to_neo4j import upload_data
# from VisualizeGraph import visualize_graph

if __name__ == "__main__":
    print("\n Starting Entity-Relationship Extraction Pipeline...")

    folderpath = "data/docs"
    docs = load_documents(folderpath)
    print(f"\n Loaded {len(docs)} documents.\n")

    all_relationships = []

    for filename, text in docs.items():
        print(f" Processing document: {filename}")
        # entities = extract_entities(text)
        rels = extract_relationships(text)
        # print(rels)
        for subj, rel, obj in rels:
            print(f" --- Extracted relationship: {subj} -- {rel} --> {obj}")
        all_relationships.extend(rels)
        # all_data.append({
        #     "doc_name": doc_name,
        #     "entities": entities,
        #     "relationships": relationships
        # })
    
    print("\n Entity and Relationship extraction completed.\n")

    # print("\n Extracting Relationships...")
    # relationships = extract_relationships(text)

    # for r in relationships:
    #     print(f"{r[0]} -- {r[1]} --> {r[2]}")
    
    print("\n Connecting to Neo4j...")
    handler = Neo4jHandler("neo4j://127.0.0.1:7687", "neo4j", "entityrelationships")

    print("\n Clearing old data...")
    handler.clear_database()

    print("\n Uploading to graph...")
    handler.upload_relationship(all_relationships)
    # for subj, rel, obj in relationships:
    #     neo4j.add_relationship(subj, rel, obj)

    handler.close()
    print("\n Done! Results can be seen in Neo4j Browser.\n")