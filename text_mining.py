import nltk
import json
import wikipedia


def extractEntities(ne_chunked):
    data = {}
    for entity in ne_chunked:
        if isinstance(entity, nltk.tree.Tree):
            text = " ".join([word for word, tag in entity.leaves()])
            ent = entity.label()
            data[text] = ent
        else:
            continue
    return data

def customNER(tagged):
    entity = []
    ret = []
    for tagged_entry in tagged:
        if(tagged_entry[1].startswith("JJ") or tagged_entry[1].startswith("NN") or (entity and tagged_entry[1].startswith("IN"))):
            entity.append(tagged_entry)
        else:
            if(entity) and entity[-1][1].startswith("IN"):
                entity.pop()
            if(entity and " ".join(e[0] for e in entity)[0].isupper()):
                if " ".join(e[0] for e in entity) not in ret:
                    ret.append(" ".join(e[0] for e in entity))
            entity = []
    if(entity and " ".join(e[0] for e in entity)[0].isupper()):
        if " ".join(e[0] for e in entity) not in ret:
            ret.append(" ".join(e[0] for e in entity))
    return ret

def wikiNER(tagged):
    entity = []
    ret = []
    for tagged_entry in tagged:
        if(tagged_entry[1].startswith("JJ") or tagged_entry[1].startswith("NN") or (entity and tagged_entry[1].startswith("IN")) or 
            (entity and tagged_entry[1].startswith("VB")) or (entity and tagged_entry[1].startswith("DT")) or (entity and tagged_entry[1].startswith("RB"))
             or (entity and tagged_entry[1].startswith("TO")) or (entity and tagged_entry[1].startswith("CD"))  or (entity and tagged_entry[1].startswith("CC"))
             or (entity and tagged_entry[1].startswith("POS"))):
            entity.append(tagged_entry)
        else:
            if(entity) and entity[-1][1].startswith("IN"):
                entity.pop()
            if(entity):
                ret.append(" ".join(e[0] for e in entity))
            entity = []
    if (entity):
        ret.append(" ".join(e[0] for e in entity))
    return ret

def loadText():
    data = json.load(open('./bbccrawler/bbccrawler/data.json'))
    return "\n".join(x["story"] for x in data)

def wiki(input):
    results = wikipedia.search(input)
    if results:
        result = results[0]
        while True:
            try:
                page = wikipedia.page(result)
            except wikipedia.exceptions.DisambiguationError as e:
                result = e.options[0]
            else:
                break
        summary = nltk.sent_tokenize(page.summary)[0]
        if len(summary.split(" is ")) >= 2:
            summary = summary.split(" is ")[1]
        elif len(summary.split(" was ")) >= 2:
            summary = summary.split(" was ")[1]
        elif len(summary.split(" are ")) >= 2:
            summary = summary.split(" are ")[1]
        else:
            summary = "Thing"
    else:
        summary = "Thing"
    return summary

def get_entities(tagged):
    ne_chunked = nltk.ne_chunk(tagged, binary=True)
    entities = extractEntities(ne_chunked)
    entitylist = []
    i = 0
    for key, value in entities.items():
        entitylist.append([key, value])
        i += 1
        if i == 5:
            break
    return entities, entitylist

def get_classifications(tagged):
    ne_chunked2 = nltk.ne_chunk(tagged, binary=False)
    classifications = extractEntities(ne_chunked2)
    classlist = []
    i = 0
    for key, value in classifications.items():
        classlist.append([key, value])
        i += 1
        if i == 5:
            break
    return classifications, classlist

def main():
    text = loadText()

    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)

    print("POS: " + str(tagged[:5]))
    print("\n")
    
    entities, entitylist = get_entities(tagged)
    print("NER based on ne_chunk: " + str(entitylist))
    print("\n")
    
    cutomentities = customNER(tagged)
    print("Custom NER: " + str(cutomentities[:5]))
    print("\n")

    classifications, classlist = get_classifications(tagged)
    print("Entity classification: " + str(classlist))
    print("\n")

    for idx, x in enumerate(entities.items()):
        key, _ = x
        wikiclass = ""
        summary = wiki(key)
        if summary == "Thing":
            wikiclass = summary
        else:
            wikitokens = nltk.word_tokenize(summary)
            wikitagged = nltk.pos_tag(wikitokens)
            wikiclass = wikiNER(wikitagged)
            if wikiclass:
                wikiclass = wikiclass[0]
            else:
                wikiclass = "Thing"

        print("ne_chunk entity: " + key)
        print("Wikipedia classification: " + wikiclass)
        try:
            print("NLTK classification: " + classifications[key])
        except:
            print("NLTK classification: Thing")
        print("\n")

        if idx == 20:
            break

    for idx, key in enumerate(cutomentities):
        wikiclass = ""
        summary = wiki(key)
        if summary == "Thing":
            wikiclass = summary
        else:
            wikitokens = nltk.word_tokenize(summary)
            wikitagged = nltk.pos_tag(wikitokens)
            wikiclass = wikiNER(wikitagged)
            if wikiclass:
                wikiclass = wikiclass[0]
            else:
                wikiclass = "Thing"

        print("Custom entity: " + key)
        print("Wikipedia classification: " + wikiclass)
        try:
            print("NLTK classification: " + classifications[key])
        except:
            print("NLTK classification: Thing")
        print("\n")

        if idx == 20:
            break


if __name__ == "__main__": main()
