import spacy

def extract_entities(text: str):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    entities = [{"name": ent.text, "type": ent.label_} for ent in doc.ents]
    return entities

if __name__ == "__main__":
    
    filepath = "data/samples/sample1.txt"
    with open(filepath, "r") as file:
        text = file.read()
    
    entities = extract_entities(text)

    for ent in entities:
        print(f"{ent['name']:<20} -> {ent['type']}")