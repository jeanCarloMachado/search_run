import os

HOME = os.environ["HOME"]


class T5ModelConfig:
    """
    Configuration for the T5 model
    """

    TARGET_VERSION = "v9"
    NEW_MODEL_RELATIVE_TARGET_DIRECTORY = "t5_llm_models/model_" + TARGET_VERSION
    BASE_MODEL_PATH = HOME + "/.python_search/t5_llm_models"
    FULL_MODEL_PATH = HOME + "/.python_search/" + NEW_MODEL_RELATIVE_TARGET_DIRECTORY
    #NEXT_ITEM_PRODUCTIONALIZED_MODEL = BASE_MODEL_PATH + "/model_v7_epoch_10"
    SUMMARIZATION_PRODUCTIONALIZED_MODEL = BASE_MODEL_PATH + '/model_v9_epoch_10'
    NEXT_ITEM_PRODUCTIONALIZED_MODEL = SUMMARIZATION_PRODUCTIONALIZED_MODEL
    BASE_MODEL_TO_TRAIN_OVER = NEXT_ITEM_PRODUCTIONALIZED_MODEL



