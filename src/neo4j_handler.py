from neo4j import GraphDatabase

class Neo4jHandler:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth = (user, password))
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    def upload_relationship(self, relationships):
        with self.driver.session() as session:
            for subj, rel, obj in relationships:
                safe_rel = rel.upper().replace(" ", "_").replace("-", "_")
                query = f"""
                MERGE (a:Entity {{name: $subj}})
                MERGE (b:Entity {{name: $obj}})
                MERGE (a)-[r:{safe_rel}]->(b)
                """
                session.run(query, subj=subj, obj=obj)