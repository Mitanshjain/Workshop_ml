# Text ---> Machine understand Numbers ---> we use (TF-IDF, Glove, GENSIM, FASTTEXT), Advance(HuggingFace transformer(all-minilm-16-v2),
#  googlegenerativeembeddings, openaiembeddings)

import sys
import gensim.downloader as api
from src.exception import CustomException
from src.logger import get_logger
logger = get_logger(__name__)

_model = None
MODEL_NAME = "glove-wiki-gigaword-50"

def _get_model():
    global _model
    if _model is None:
        logger.info(f"Loading pretrained model for Embeddings :{MODEL_NAME}")
        _model = api.load(MODEL_NAME)
        logger.info(f"Embeddings loaded , Vocabulary size: {len(_model.index_to_key)}")
    return _model

def most_similar_word(word:str, topn:int=5):
    try:
        model = _get_model()
        word = word.lower()
        if word not in model:
            logger.info(f" '{word}' was not found in vocabulary.")
            return []
        results = model.most_similar(word, topn)
        logger.info(f"Most similar to '{word} : '{results}'")
        return results
    except Exception as e:
        raise CustomException(e,sys)


def word_similarity(word1:str, word2:str):
    try:
        model = _get_model()
        score = float(model.similarity(word1.lower(),word2.lower()))
        logger.info(f"Similarity( '{word1}', '{word2}') = {score:.3f}")
        return score
    except Exception as e:
        raise CustomException(e,sys)