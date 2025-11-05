from neo4j import GraphDatabase
import json

class KnowledgeGraphUploader:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def create_entity(self, tx, name, label):
        tx.run(
            "MERGE (e:Entity {name: $name, type: $label})",
            name=name,
            label=label,
        )
    
    def create_relationship(self, tx, source, relation, target):
        tx.run(
            """
            MATCH (a:Entity {name: $source})
            MATCH (b:Entity {name: $target})
            MERGE (a)-[r:RELATION {type: $relation}]->(b)
            """,
            source=source,
            target=target,
            relation=relation,
        )
    
    def upload_data(self, entities, relationships, doc_name=None):
        with self.driver.session() as session:
            for ent in entities:
                session.run(
                    """
                    MERGE (e:Entity {name: $name})
                    ON CREATE SET e.type = $type
                    SET e.source_doc = coalesce(e.source_doc, []) + [$doc_name]
                    """,
                    name=ent["name"], type=ent["type"], doc_name=doc_name
                )
            for rel in relationships:
                session.run(
                    """
                    MATCH (a:Entity {name: $source})
                    MATCH (b:Entity {name: $target})
                    MERGE (a)-[r:RELATION {type: $type}]->(b)
                    """,
                    source=rel["source"], target=rel["target"], type=rel["type"]
                )
        print(f"Uploaded {len(entities)} entities and {len(relationships)} relationships to Neo4j.")

if __name__ == "__main__":

    with open("data/graph_data.json", "r") as f:
        data = json.load(f)
    
    entities = data["entities"]
    relationships = data["relationships"]

    uri = "neo4j://127.0.0.1:7687"
    user = "neo4j"
    password = "entityrelationships"

    uploader = KnowledgeGraphUploader(uri, user, password)
    uploader.upload_data(entities, relationships)
    uploader.close()