# src/llm_quantized.py
# Wrapper pour charger Gemma 4 avec llama-cpp-python (quantization 4-bit)
# Réduit la mémoire requise de 11.9GB à ~6-7GB

import os
from typing import Optional, List, Dict, Any
from loguru import logger

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    logger.warning("llama-cpp-python not installed. Install with: pip install llama-cpp-python")

class QuantizedLLMClient:
    """
    Client LLM utilisant llama-cpp-python avec quantization 4-bit.
    Permet de charger Gemma 4 avec seulement 6-7GB au lieu de 11.9GB.
    """
    
    def __init__(self, model_path: Optional[str] = None, use_ollama_fallback: bool = True):
        """
        Initialize le client LLM.
        
        Args:
            model_path: Chemin vers le fichier GGUF quantisé (ex: models/gemma-4-q4.gguf)
            use_ollama_fallback: Si True, fallback sur Ollama si llama-cpp-python échoue
        """
        self.model_path = model_path
        self.use_ollama_fallback = use_ollama_fallback
        self.llm = None
        self.using_llama_cpp = False
        self.using_ollama = False
        
        if LLAMA_CPP_AVAILABLE and model_path:
            self._init_llama_cpp(model_path)
        elif use_ollama_fallback:
            self._init_ollama_fallback()
        else:
            logger.error("No LLM backend available!")
    
    def _init_llama_cpp(self, model_path: str):
        """Initialiser llama-cpp avec quantization 4-bit"""
        if not os.path.exists(model_path):
            logger.warning(f"Model not found: {model_path}. Using Ollama fallback.")
            if self.use_ollama_fallback:
                self._init_ollama_fallback()
            return
        
        try:
            logger.info(f"Loading quantized model with llama-cpp: {model_path}")
            self.llm = Llama(
                model_path=model_path,
                n_gpu_layers=35,  # Offload à GPU si disponible
                n_ctx=8192,  # Context window
                n_threads=4,  # CPU threads
                verbose=False
            )
            self.using_llama_cpp = True
            logger.info("✓ llama-cpp-python initialized successfully (4-bit quantized)")
        except Exception as e:
            logger.error(f"Failed to load with llama-cpp: {e}")
            if self.use_ollama_fallback:
                self._init_ollama_fallback()
    
    def _init_ollama_fallback(self):
        """Fallback sur Ollama si llama-cpp échoue"""
        try:
            import ollama
            self.ollama_client = ollama.Client(host="http://localhost:11434")
            self.using_ollama = True
            logger.info("✓ Ollama client initialized (fallback)")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1024,
        **kwargs
    ) -> str:
        """
        Générer une réponse de chat.
        
        Args:
            messages: Liste des messages [{"role": "user", "content": "..."}, ...]
            temperature: Température (0.0 = déterministe, 1.0 = créatif)
            max_tokens: Nombre max de tokens à générer
            
        Returns:
            Texte de la réponse
        """
        if self.using_llama_cpp:
            return self._chat_llama_cpp(messages, temperature, max_tokens)
        elif self.using_ollama:
            return self._chat_ollama(messages, temperature, max_tokens)
        else:
            raise RuntimeError("No LLM backend available!")
    
    def _chat_llama_cpp(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Chat via llama-cpp"""
        try:
            # Format messages comme prompt
            prompt = self._format_messages(messages)
            
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95,
                stop=["User:", "Assistant:"],
            )
            
            return response["choices"][0]["text"].strip()
        except Exception as e:
            logger.error(f"llama-cpp chat failed: {e}")
            if self.using_ollama:
                return self._chat_ollama(messages, temperature, max_tokens)
            raise
    
    def _chat_ollama(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Chat via Ollama"""
        try:
            response = self.ollama_client.chat(
                model="gemma4:e4b",
                messages=messages,
                stream=False,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            )
            return response["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Ollama chat failed: {e}")
            raise
    
    @staticmethod
    def _format_messages(messages: List[Dict[str, str]]) -> str:
        """Convertir messages au format prompt"""
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user").capitalize()
            content = msg.get("content", "")
            prompt += f"{role}: {content}\n"
        prompt += "Assistant: "
        return prompt


def get_llm_client(use_quantized: bool = True) -> QuantizedLLMClient:
    """
    Factory pour obtenir un client LLM approprié.
    
    Args:
        use_quantized: Si True, tente d'utiliser llama-cpp quantisé
        
    Returns:
        Instance de QuantizedLLMClient
    """
    if use_quantized:
        # Chemin attendu du modèle GGUF quantisé
        model_path = "models/gemma-4-9b-q4.gguf"
        return QuantizedLLMClient(model_path=model_path, use_ollama_fallback=True)
    else:
        # Fallback direct sur Ollama
        return QuantizedLLMClient(use_ollama_fallback=True)
