from typing import List, Dict, Any
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from langchain.schema import SystemMessage, HumanMessage, AIMessage


class LLaMAChat:
    def __init__(
        self,
        model_name: str = "meta-llama/Llama-2-7b-chat-hf",
        temperature: float = 0.7,
        max_tokens: int = 256,
        request_timeout: int = None
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            pad_token_id=self.tokenizer.eos_token_id  
        )
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, messages, stop=None):
        prompt = self._convert_messages_to_prompt(messages[0])
        
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            padding=True,
            truncation=True,
            max_length=2048
        )
        input_ids = inputs["input_ids"].to(self.model.device)
        
        prompt_tokens = len(inputs["input_ids"][0])
        
        gen_kwargs = {
            "max_new_tokens": self.max_tokens,
            "do_sample": True if self.temperature > 0 else False,
            "temperature": self.temperature,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }
        
        if stop:
            gen_kwargs["stopping_criteria"] = self._create_stopping_criteria(stop)
        
        with torch.no_grad():
            outputs = self.model.generate(input_ids, **gen_kwargs)
        
        new_tokens = outputs[:, input_ids.shape[1]:]
        completion_tokens = len(new_tokens[0])
        response_text = self.tokenizer.decode(new_tokens[0], skip_special_tokens=True)
        
        generation = type('Generation', (), {'message': type('Message', (), {'content': response_text})()})
        generations = type('Generations', (), {
            'generations': [[generation]],
            'llm_output': {
                'token_usage': {
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens
                }
            }
        })
        
        return generations
    
    def _convert_messages_to_prompt(self, messages: List[Any]) -> str:
        """Convert langchain messages to LLaMA chat format"""
        prompt = ""
        for message in messages:
            if isinstance(message, SystemMessage):
                prompt += f"[INST] <<SYS>>\n{message.content}\n<</SYS>>\n\n"
            elif isinstance(message, HumanMessage):
                prompt += f"{message.content} [/INST]"
            elif isinstance(message, AIMessage):
                prompt += f"{message.content} [INST]"
        return prompt
    
    def _create_stopping_criteria(self, stop_sequences):
        """Create stopping criteria for generation"""
        from transformers import StoppingCriteria, StoppingCriteriaList
        
        class StopSequenceCriteria(StoppingCriteria):
            def __init__(self, stop_sequences, tokenizer):
                self.stop_sequences = stop_sequences
                self.tokenizer = tokenizer
            
            def __call__(self, input_ids, scores):
                decoded = self.tokenizer.decode(input_ids[0])
                return any(stop_seq in decoded for stop_seq in self.stop_sequences)
        
        return StoppingCriteriaList([StopSequenceCriteria(stop_sequences, self.tokenizer)])