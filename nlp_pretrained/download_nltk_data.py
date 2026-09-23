import nltk
import sys
from src.logger import get_logger
logger = get_logger(__name__)
from src.exception import CustomException
REQUIRED_RESOURCES = [
    "punkt", # It is used for sentence/word based takenization
    "punkt_tab", # This is newer version of tokenization
    "averaged_perceptron_tagger", # This is used for pos-tagging
    "averaged_perceptron_tagger_eng", # This is newer version of pos(part of speech tagging) tagger
    "maxnet_ne_chunker", # This is for NER(Named entity recognition) this gives the entities in the sentence like person organization,location in sentences.
    "maxnet_ne_chunker_tab", # This is the latest version of NER
    "words", # This is used for convert our word into lexical format.
    "vader_lexicon", # This is used for sentiment analysis(text == positive, text == negative,text == neutral)
    "stopwords", # It will provide common stopword list[the,is,a,an,of,and]
    "wordnet", # This is used for understanding the relationship of context.
]

if __name__ == "__main__":
    logger.info("Downloading NLTK pretrained models/data....")
    print("Downloading NLTK pretrained models/data....")
    for i in REQUIRED_RESOURCES:
        try:
            nltk.download(i)
        except Exception as e:
            raise CustomException(e,sys)
    logger.info("All models download")