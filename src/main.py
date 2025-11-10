from ExtractRelationships import extract_relationships
from neo4j_handler import Neo4jHandler

if __name__ == "__main__":
    text = """Elon Musk founded SpaceX in 2002.
    OpenAI developed ChatGPT.
    Sundar Pichai leads Google.
    Microsoft acquired Github in 2018.
    Steve Jobs co-founded Apple with Steve Wozniak."""

    print("\n Extracting Relationships...")
    relationships = extract_relationships(text)

    for r in relationships:
        print(f"{r[0]} -- {r[1]} --> {r[2]}")
    
    print("\n Connecting to Neo4j...")
    neo4j = Neo4jHandler("neo4j://127.0.0.1:7687", "neo4j", "entityrelationships")

    print("\n Clearing old data...")
    neo4j.clear_database()

    print("\n Uploading to graph...")
    for subj, rel, obj in relationships:
        neo4j.add_relationship(subj, rel, obj)

    neo4j.close()
    print("\n Done! Results can be seen in Neo4j Browser.\n")