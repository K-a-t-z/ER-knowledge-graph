from neo4j import GraphDatabase

class Neo4jHandler:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth = (user, password))
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    def add_relationship(self, subj, rel, obj):
        with self.driver.session() as session:
            session.execute_write(self._create_and_link, subj, rel, obj)
    
    @staticmethod
    def _create_and_link(tx, subj, rel, obj):
        safe_rel = rel.upper().replace("-", "_").replace(" ", "_")
        query = (
            "MERGE (a:Entity {name: $subj}) "
            "MERGE (b:Entity {name: $obj}) "
            f"MERGE (a)-[r:{safe_rel}]->(b)"
        )
        tx.run(query, subj=subj, obj=obj)