import torch
from transformers.generation.stopping_criteria import StoppingCriteria, StoppingCriteriaList

class EndOfSentenceStoppingCriteria(StoppingCriteria):

    def __init__(self, tokenizer, sentence_endings=None):
        if sentence_endings is None:
            sentence_endings = [".", "!", "?"]

        self.tokenizer = tokenizer
        self.sentence_endings = sentence_endings

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        last_token_id = input_ids[0, -1].item()
        last_token = self.tokenizer.decode([last_token_id]).strip()

        if any(last_token.endswith(end) for end in self.sentence_endings):
            return True

        return False
