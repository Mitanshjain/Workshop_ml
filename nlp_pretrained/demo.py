# This is the file where we can connect all the nlp_pretrained logics in this file.

from nlp_pretrained.embedding import most_similar_word,word_similarity
from nlp_pretrained.ner_tagger import get_pos_tags,extract_entities

if __name__ == "__main__":
    text = "I have fever for 3 days and I am from Mumbai"
    print(get_pos_tags(text))
    print(extract_entities(text))
    print("Most similar words:",most_similar_word("fever"))
    print("Word Similarity:",word_similarity("fever","mumbai"))
    