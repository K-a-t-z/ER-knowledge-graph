from transformers import pipeline
import re

re_pipeline = pipeline("text2text-generation", model="Babelscape/rebel-large")

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_rebel_output(generated_text: str):
    triples = []
    text = generated_text.strip()
    if not text:
        return triples
    text = re.sub(r'\s{3,}', '  ', text)
    parts = [p.strip() for p in re.split(r'\s{2,}', text) if p.strip()]
    if len(parts) >= 3:
        for i in range(0, len(parts), 3):
            if i + 2 < len(parts):
                subj = parts[i]
                obj = parts[i+1]
                rel = parts[i+2]
                rel = rel.strip().strip(".")
                triples.append((subj, rel, obj))
    if not triples:
        cand = re.findall(r'([A-Z][\w\-\s&\.]{1,80}?)\s{1,3}([a-z][a-z\s]{1,40}?)\s{1,3}([A-Z][\w\-\s&\.]{1,80}?)', text)
        for c in cand:
            subj, rel, obj = c
            triples.append((subj.strip(), rel.strip(), obj.strip()))
    return triples

def postprocess_triples(triples):
    cleaned = []
    seen = set()
    for subj, rel, obj in triples:
        if not subj or not obj or not rel:
            continue
        if re.fullmatch(r'[\d\W_]+', subj) or re.fullmatch(r'[\d\W_]+', obj):
            continue
        if len(rel.split()) > 7:
            continue
        if not (re.search(r'[A-Z]', subj) or re.search(r'[A-Z]', obj)):
            continue
        subj_norm = re.sub(r'\s+', ' ', subj).strip(" ,.-")
        rel_norm = re.sub(r'\s+', ' ', rel).strip(" ,.-")
        obj_norm = re.sub(r'\s+', ' ', obj).strip(" ,.-")
        triple = (subj_norm, rel_norm.lower(), obj_norm)
        if triple not in seen:
            seen.add(triple)
            cleaned.append(triple)
    return cleaned

def extract_relationships(text: str):
    text = clean_text(text)
    triples = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for sentence in sentences:
        if len(sentence.strip()) < 10:
            continue
        try:
            outputs = re_pipeline(
                sentence,
                max_length=512,
                num_beams=3,
                truncation=True,
            )
            generated_text = outputs[0]["generated_text"]
            # print("\n ===== MODEL OUTPUT RAW =====\n", generated_text)
            raw_triples = parse_rebel_output(generated_text)
            extracted_triples = postprocess_triples(raw_triples)
            triples.extend(extracted_triples)
            # for subj, rel, obj in extracted_triples:
            #     print(f" --- Extracted rel: {subj} -- {rel.upper()} --> {obj}")
            #     triples.append((subj, rel, obj))
        except Exception as e:
            print(f"Error processing sentence: {e}")
    return triples

if __name__ == "__main__":
    sample_text = """Elon Musk founded SpaceX in 2002.
    OpenAI developed ChatGPT.
    Sundar Pichai leads Google.
    Microsoft acquired GitHub in 2018.
    Steve Jobs co-founded Apple with Steve Wozniak."""

    relationships = extract_relationships(sample_text)
    print("\n Final extracted relationships:")
    for r in relationships:
        print(f" {r[0]} -- {r[1]} --> {r[2]}")

"""
import re
import spacy

nlp = spacy.load("en_core_web_trf")

def extract_relationships(text):
    doc = nlp(text)
    relationships = []

    def nearest_entity(token):
        for ent in doc.ents:
            if ent.start <= token.i <= ent.end:
                return ent.text
        left = [ent for ent in doc.ents if ent.end < token.i]
        right = [ent for ent in doc.ents if ent.start > token.i]
        if left:
            return left[-1].text
        elif right:
            return right[0].text
        return token.text
    
    for sent in doc.sents:
        for token in sent:
            if token.pos_ == "VERB":
                subj = [w for w in token.lefts if w.dep_ in ("nsubj", "nsubjpass")]
                obj = [w for w in token.rights if w.dep_ in ("dobj", "attr", "pobj")]

                for s in subj:
                    for o in obj:
                        subj_ent = nearest_entity(s)
                        obj_ent = nearest_entity(o)
                        if subj_ent != obj_ent:
                            relationships.append((subj_ent, token.lemma_.lower(), obj_ent))
            if token.dep_ == "acl" and any(child.text.lower() == "by" for child in token.children):
                actor = None
                for child in token.children:
                    if child.text.lower() == "by":
                        pobj = [t for t in child.subtree if t.dep_ in ("pobj", "compound")]
                        if pobj:
                            actor = " ".join([t.text for t in pobj])
                if actor:
                    target = nearest_entity(token.head)
                    relationships.append((actor, token.lemma_.lower(), target))
            if token.dep_ == "poss" and token.head.ent_type_:
                relationships.append((token.text, "owns", token.head.text))
    
    clean = []
    for triple in relationships:
        if triple not in clean and all(len(x.strip()) > 1 for x in triple):
            clean.append(triple)
    return clean

def extract_general_relationships(text):
    doc = nlp(text)
    relationships = []

    for sent in doc.sents:
        for token in sent:
            if token.pos_ == "VERB":
                subjects = [w for w in token.lefts if w.dep_ in ("nsubj", "nsubjpass")]
                objects = [w for w in token.rights if w.dep_ in ("dobj", "attr", "pobj")]

                for subj in subjects:
                    for obj in objects:
                        subj_text = " ".join(t.text for t in subj.subtree)
                        rel_text = token.lemma_.lower()
                        obj_text = " ".join(t.text for t in obj.subtree)
                        relationships.append((subj_text, rel_text, obj_text))
                
                if token.dep_ == "acl" and any(child.text.lower() == "by" for child in token.children):
                    by_objs = [
                        [tok for tok in child.subtree if tok.dep_ in ("pobj", "compound")]
                        for child in token.children if child.text.lower() == "by"
                    ]
                    for group in by_objs:
                        if group:
                            actor = " ".join(tok.text for tok in group)
                            target = " ".join(tok.text for tok in token.head.subtree)
                            relationships.append((actor, token.lemma_.lower(), target))
    
    cleaned = []
    for (s, r, o) in relationships:
        if len(s.strip()) > 1 and len(o.strip()) > 1:
            triple = (s.strip(), r.strip(), o.strip())
            if triple not in cleaned:
                cleaned.append(triple)
    return cleaned

def extract_relationships_spec(text):
    relationships = []
    doc = nlp(text)

    for sent in doc.sents:
        # sent_doc = nlp(sent.text)
        # matches = list(rel_pattern.finditer(sent))

        # if not matches:
        #     continue

        ents = [ent for ent in sent.ents if ent.label_ in ["PERSON", "ORG", "PRODUCT", "WORK_OF_ART"]]
        # if len(ents) < 2:
        #     continue

        for token in sent:
            if token.dep_ in ("ROOT", "acl", "advcl", "relcl") and token.pos_ == "VERB":
                subj = [w for w in token.lefts if w.dep_ in ("nsubj", "nsubjpass")]
                obj = [w for w in token.rights if w.dep_ in ("dobj", "attr", "pobj")]

                if subj and obj:
                    subj_text = subj[-1].text
                    obj_text = obj[0].text
                    rel_text = token.lemma_.upper()
                    relationships.append((subj_text, rel_text, obj_text))
        
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
        if re.search(rel_pattern, sent.text):
            matches = list(rel_pattern.finditer(sent.text))
            if ents and len(ents) >= 2:
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
    
    cleaned = []
    for r in relationships:
        if len(r[0]) > 1 and len(r[2]) > 1 and r not in cleaned:
            cleaned.append(r)
    
    return cleaned
"""