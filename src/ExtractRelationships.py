import re
import spacy

nlp = spacy.load("en_core_web_trf")

def extract_relationships(text):
    relationships = []

    rel_keywords = {
        "founded": "FOUNDED",
        "co-founded": "CO-FOUNDED",
        "cofounded": "CO-FOUNDED",
        "developed": "DEVELOPED",
        "leads": "LEADS",
        "led": "LEADS",
        "acquired": "ACQUIRED",
        "owns": "OWNS",
        "created": "CREATED",
        "designed": "DESIGNED"
    }

    rel_pattern = re.compile("|".join(rel_keywords.keys()), re.IGNORECASE)
    fallback_ent_pattern = re.compile(r"\b([A-Z][a-zA-Z0-9&.\-]+(?:\s+[A-Z][a-zA-Z0-9&.\-]+)*)\b")

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

    for sent_text in sentences:
        doc = nlp(sent_text)
        matches = list(rel_pattern.finditer(sent_text))
        ents = [ent for ent in doc.ents]

        if len(ents) < 2:
            for match in fallback_ent_pattern.finditer(sent_text):
                ents.append(type("Entity", (), {"text": match.group(0), "start_char": match.start()}))
        
        if not matches or len(ents) < 2:
            continue

        for match in matches:
            relation_word = match.group(0).lower()
            relation = rel_keywords.get(relation_word.replace("-", ""), relation_word.upper())
            rel_start = match.start()

            before_ents = [ent for ent in ents if ent.start_char < rel_start]
            after_ents = [ent for ent in ents if ent.start_char > rel_start]

            if before_ents and after_ents:
                subj = before_ents[-1].text
                obj = after_ents[0].text
                relationships.append((subj, relation, obj))
    
    return relationships

if __name__ == "__main__":
    text = """Elon Musk founded SpaceX in 2002.
    OpenAI developed ChatGPT.
    Sundar Pichai leads Google.
    Microsoft acquired Github in 2018.
    Steve Jobs co-founded Apple with Steve Wozniak."""

    relations = extract_relationships(text)

    for r in relations:
        print(f"{r[0]} -- {r[1]} --> {r[2]}")