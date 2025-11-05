import os
from ExtractEntities import extract_entities
from ExtractRelationships import extract_relationships
from to_neo4j import KnowledgeGraphUploader

def process_text_file(file_path):
    with open(file_path, "r") as f:
        return f.read()

def process_multiple_documents(source_folder, uploader):
    for idx, filename in enumerate(os.listdir(source_folder)):
        if not filename.endswith(".txt"):
            continue
        file_path = os.path.join(source_folder, filename)
        print(f"\n Processing document {idx + 1}: {filename}")

        text = process_text_file(file_path)

        entities = extract_entities(text)
        print(f" Extracted {len(entities)} entities.")

        relationships = extract_relationships(text, entities)
        print(f" Extracted {len(relationships)} relationships.")

        uploader.upload_data(entities, relationships, doc_name=filename)

if __name__ == "__main__":

    source_folder = "data/samples/"
    uri = "neo4j://127.0.0.1:7687"
    user = "neo4j"
    password = "entityrelationships"

    uploader = KnowledgeGraphUploader(uri, user, password)

    try:
        process_multiple_documents(source_folder, uploader)
        print("\n All documents processed and uploaded successfully.")
    finally:
        uploader.close()