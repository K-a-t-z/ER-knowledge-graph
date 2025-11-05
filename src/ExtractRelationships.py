import spacy
import json
from ExtractEntities import extract_entities
from NormalizeEntities import normalize_entity, remove_duplicates

nlp = spacy.load("en_core_web_sm")

def extract_relationships(text: str):
    doc = nlp(text)
    relationships = []
    relation_keywords = {
        "founded": "FOUNDED",
        "founded by": "FOUNDED_BY",
        "CEO": "CEO_OF",
        "chief executive": "CEO_OF",
        "works at": "WORKS_AT",
        "based in": "BASED_IN",
        "partnered with": "PARTNERED_WITH",
        "acquired": "ACQUIRED",
    }

    for sent in doc.sents:
        sent_text = sent.text.lower()
        ents = [(ent.text, ent.label_) for ent in sent.ents]

        if len(ents) < 2:
            continue

        for phrase, rel_label in relation_keywords.items():
            if phrase in sent_text:
                source = normalize_entity(ents[0][0])
                target = normalize_entity(ents[-1][0])
                relationships.append(
                    {"source": source, "relation": rel_label, "target": target}
                )
    return relationships

def SaveGraphData(entities, relationships, output_path="data/graph_data.json"):

    data = {
        "entities": entities,
        "relationships": relationships,
    }

    with open(output_path, "w") as file:
        json.dump(data, file, indent=4)
    
    print(f"Saved {len(entities)} entities and {len(relationships)} relationships to {output_path}")

if __name__ == "__main__":

    filepath = "data/samples/sample1.txt"
    with open(filepath, "r") as file:
        text = file.read()
    
    raw_entities = extract_entities(text)
    unique_entities = remove_duplicates(raw_entities)

    relationships = extract_relationships(text)

    SaveGraphData(unique_entities, relationships)