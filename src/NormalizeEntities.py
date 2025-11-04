import json
import re
from typing import List, Tuple, Dict
from ExtractEntities import extract_entities

def normalize_entity(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text

def remove_duplicates(entities: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    seen = set()
    unique_entities = []
    for entity, label in entities:
        norm_entity = normalize_entity(entity)
        key = norm_entity.lower()
        if key not in seen:
            seen.add(key)
            unique_entities.append({"entity": norm_entity, "label": label})
    return unique_entities

def to_json(entities: List[Dict[str, str]], output_path: str = "data/entities.json"):
    data = {"entities": entities}
    with open(output_path, "w") as file:
        json.dump(data, file, indent=4)
    print(f"Saved {len(entities)} entities to {output_path}")

if __name__ == "__main__":

    filepath = "data/samples/sample1.txt"
    with open(filepath, "r") as file:
        text = file.read()
    
    extracted = extract_entities(text)

    unique_entities = remove_duplicates(extracted)

    to_json(unique_entities)