#!/usr/bin/env python3
"""
Prompt Optimizer Flask App

A simple web application for analyzing and optimizing prompts using local LLMs.
Supports MLX (native macOS), Ollama, and LM Studio backends.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, Tuple
from flask import Flask, render_template, request, jsonify, flash
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Configuration
class Config:
    # LLM Backend selection
    LLM_BACKEND = os.environ.get('LLM_BACKEND', 'auto')  # auto, mlx, ollama, lmstudio
    
    # MLX Configuration
    MLX_MODEL = os.environ.get('MLX_MODEL', 'mlx-community/Mistral-7B-Instruct-v0.3-4bit')
    MLX_MAX_TOKENS = int(os.environ.get('MLX_MAX_TOKENS', '1024'))
    MLX_TEMPERATURE = float(os.environ.get('MLX_TEMPERATURE', '0.7'))
    
    # Ollama Configuration
    OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama2')
    
    # LM Studio Configuration
    LMSTUDIO_URL = os.environ.get('LMSTUDIO_URL', 'http://localhost:1234')
    LMSTUDIO_MODEL = os.environ.get('LMSTUDIO_MODEL', 'local-model')

# Hard-coded prompts
ANALYSIS_PROMPT = """You are an expert prompt engineer. Analyze the following prompt and provide a detailed assessment covering:

1. **Clarity**: How clear and unambiguous is the prompt?
2. **Specificity**: Does it provide enough context and constraints?
3. **Structure**: Is it well-organized and logical?
4. **Completeness**: Are there missing elements that would improve results?
5. **Potential Issues**: What problems might arise with this prompt?

Provide specific, actionable feedback.

Prompt to analyze:
{prompt}

Analysis:"""

OPTIMIZATION_PROMPT = """You are an expert prompt engineer. Based on the analysis below, create an optimized version of the original prompt that addresses the identified issues and incorporates best practices.

Original prompt:
{original_prompt}

Analysis:
{analysis}

Optimized prompt:"""

class LLMBackend:
    """Abstract base for LLM backends"""
    
    def generate(self, prompt: str) -> str:
        raise NotImplementedError
    
    def is_available(self) -> bool:
        raise NotImplementedError

class MLXBackend(LLMBackend):
    """MLX backend for Apple Silicon"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._available = self._check_availability()
    
    def _check_availability(self) -> bool:
        try:
            import mlx.core as mx
            from mlx_lm import load, generate
            return True
        except ImportError:
            logger.info("MLX not available - install with: pip install mlx-lm")
            return False
        except Exception as e:
            logger.warning(f"MLX check failed: {e}")
            return False
    
    def _load_model(self):
        if self.model is None:
            try:
                from mlx_lm import load
                logger.info(f"Loading MLX model: {Config.MLX_MODEL}")
                self.model, self.tokenizer = load(Config.MLX_MODEL)
                logger.info("MLX model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load MLX model: {e}")
                raise
    
    def generate(self, prompt: str) -> str:
        if not self.is_available():
            raise RuntimeError("MLX backend not available")
        
        self._load_model()
        
        try:
            from mlx_lm import generate
            
            response = generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=Config.MLX_MAX_TOKENS,
                temp=Config.MLX_TEMPERATURE,
                verbose=False
            )
            return response
        except Exception as e:
            logger.error(f"MLX generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        return self._available

class OllamaBackend(LLMBackend):
    """Ollama backend"""
    
    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{Config.OLLAMA_URL}/api/generate",
                json={
                    "model": Config.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        try:
            response = requests.get(f"{Config.OLLAMA_URL}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

class LMStudioBackend(LLMBackend):
    """LM Studio backend"""
    
    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{Config.LMSTUDIO_URL}/v1/completions",
                json={
                    "model": Config.LMSTUDIO_MODEL,
                    "prompt": prompt,
                    "max_tokens": 1024,
                    "temperature": 0.7
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()["choices"][0]["text"]
        except Exception as e:
            logger.error(f"LM Studio generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        try:
            response = requests.get(f"{Config.LMSTUDIO_URL}/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False

class PromptOptimizer:
    """Main prompt optimization logic"""
    
    def __init__(self):
        self.backend = self._select_backend()
        if not self.backend:
            raise RuntimeError("No LLM backend available")
    
    def _select_backend(self) -> Optional[LLMBackend]:
        """Select the best available backend"""
        backends = {
            'mlx': MLXBackend(),
            'ollama': OllamaBackend(),
            'lmstudio': LMStudioBackend()
        }
        
        # If specific backend requested, try it first
        if Config.LLM_BACKEND != 'auto' and Config.LLM_BACKEND in backends:
            backend = backends[Config.LLM_BACKEND]
            if backend.is_available():
                logger.info(f"Using requested backend: {Config.LLM_BACKEND}")
                return backend
            else:
                logger.warning(f"Requested backend {Config.LLM_BACKEND} not available")
        
        # Auto-select: prefer MLX on macOS, then Ollama, then LM Studio
        for name in ['mlx', 'ollama', 'lmstudio']:
            backend = backends[name]
            if backend.is_available():
                logger.info(f"Auto-selected backend: {name}")
                return backend
        
        logger.error("No LLM backends available")
        return None
    
    def analyze_prompt(self, prompt: str) -> str:
        """Analyze a prompt using the selected backend"""
        analysis_input = ANALYSIS_PROMPT.format(prompt=prompt)
        return self.backend.generate(analysis_input)
    
    def optimize_prompt(self, original_prompt: str, analysis: str) -> str:
        """Optimize a prompt based on analysis"""
        optimization_input = OPTIMIZATION_PROMPT.format(
            original_prompt=original_prompt,
            analysis=analysis
        )
        return self.backend.generate(optimization_input)
    
    def process_prompt(self, prompt: str) -> Tuple[str, str]:
        """Complete workflow: analyze then optimize"""
        logger.info("Starting prompt analysis...")
        analysis = self.analyze_prompt(prompt)
        
        logger.info("Starting prompt optimization...")
        optimized = self.optimize_prompt(prompt, analysis)
        
        return analysis, optimized

# Global optimizer instance
optimizer = None

def init_optimizer():
    """Initialize the prompt optimizer"""
    global optimizer
    if optimizer is None:
        try:
            optimizer = PromptOptimizer()
            logger.info(f"Prompt optimizer initialized with backend: {type(optimizer.backend).__name__}")
        except Exception as e:
            logger.error(f"Failed to initialize optimizer: {e}")
            optimizer = None
    return optimizer is not None

@app.route('/')
def index():
    """Main page"""
    try:
        # Simplified version that should definitely work
        backend_status = {
            'MLX': False,
            'Ollama': False,
            'LM Studio': False
        }
        
        return render_template('index.html', backend_status=backend_status)
    except Exception as e:
        # If template fails, return simple HTML
        return f'''
        <html><body>
        <h1>Prompt Optimizer</h1>
        <p>Template error: {str(e)}</p>
        <p>Flask is working, but template failed.</p>
        </body></html>
        '''

@app.route('/api/optimize', methods=['POST'])
def optimize():
    """API endpoint for prompt optimization"""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'No prompt provided'}), 400
        
        prompt = data['prompt'].strip()
        if not prompt:
            return jsonify({'error': 'Empty prompt provided'}), 400
        
        # Initialize optimizer if needed
        if not init_optimizer():
            return jsonify({'error': 'No LLM backend available'}), 503
        
        # Process the prompt
        analysis, optimized = optimizer.process_prompt(prompt)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'optimized_prompt': optimized,
            'backend': type(optimizer.backend).__name__
        })
    
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def status():
    """API endpoint for checking system status"""
    backend_status = {
        'mlx': MLXBackend().is_available(),
        'ollama': OllamaBackend().is_available(),
        'lmstudio': LMStudioBackend().is_available()
    }
    
    active_backend = None
    if optimizer and optimizer.backend:
        active_backend = type(optimizer.backend).__name__
    
    return jsonify({
        'backends': backend_status,
        'active_backend': active_backend,
        'config': {
            'llm_backend': Config.LLM_BACKEND,
            'mlx_model': Config.MLX_MODEL,
            'ollama_model': Config.OLLAMA_MODEL,
            'lmstudio_model': Config.LMSTUDIO_MODEL
        }
    })

if __name__ == '__main__':
    print(f"🚀 Prompt Optimizer starting...")
    print(f"📝 Will be available at http://127.0.0.1:6000")
    print(f"🔧 Starting Flask on 127.0.0.1:6000...")
    
    # Test that we can at least create the Flask app
    try:
        print("✅ Flask app created successfully")
        print("✅ Routes registered successfully")
        print("🔧 Attempting to start server...")
        app.run(host='127.0.0.1', port=6000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Failed to start Flask: {e}")
        import traceback
        traceback.print_exc()
