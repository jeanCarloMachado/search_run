
import os
HOME = os.environ['HOME']
class T5ModelConfig:
    VERSION = 'v2'
    NEW_MODEL_TARGET_DIRECTORY = 't5_llm_models/' + VERSION
    BASE_MODEL_PATH = HOME + '/.python_search/t5_llm_models'
    FULL_MODEL_PATH = BASE_MODEL_PATH + NEW_MODEL_TARGET_DIRECTORY
    PRODUCTIONALIZED_MODEL = BASE_MODEL_PATH + '/production_model'


class T5Model:

    def __init__(self):
        from transformers import T5Tokenizer
        self.tokenizer = T5Tokenizer.from_pretrained('t5-small')
        self.config = T5ModelConfig()

    def load_trained_model(self):
        from transformers import T5ForConditionalGeneration, logging
        logging.set_verbosity_error()
        # Load the model
        from python_search.logger import setup_generic_stdout_logger
        logger = setup_generic_stdout_logger()

        logger.debug("Loading model from:" + self.config.FULL_MODEL_PATH)
        model = T5ForConditionalGeneration.from_pretrained(self.config.PRODUCTIONALIZED_MODEL)

        # Ensure the model is in evaluation mode
        model.eval()
        return model, self.tokenizer
