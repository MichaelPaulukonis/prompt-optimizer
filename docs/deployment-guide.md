# Deployment Guide

## Current Implementation Status

✅ **WORKING**: The Prompt Optimizer is fully functional with MLX backend.

### Architecture

The final implementation uses:
- **Flask Web App** (`app_mlx_api.py`) running on port 5001
- **MLX API Server** (`mlx_lm.server`) running on port 8080  
- **HTTP Communication** between Flask and MLX server

This architecture follows MLX community best practices and avoids the threading/GIL issues that occurred with direct MLX integration.

## Quick Deployment

### Automated Launch (Recommended)

```bash
# One command to start everything
./launch.sh
```

This script:
1. Validates environment and dependencies
2. Starts MLX server on port 8080
3. Starts Flask app on port 5001
4. Opens browser automatically
5. Handles cleanup on exit

### Manual Deployment

If you prefer manual control:

1. **Terminal 1 - Start MLX Server:**
   ```bash
   source venv/bin/activate
   python -m mlx_lm.server \
     --model mlx-community/Mistral-7B-Instruct-v0.3-4bit \
     --host 127.0.0.1 \
     --port 8080
   ```

2. **Terminal 2 - Start Flask App:**
   ```bash
   source venv/bin/activate
   python app_mlx_api.py
   ```

3. **Access:** http://127.0.0.1:5001

## Port Configuration

- **Flask App**: Port 5001 (changed from 6000 due to Chrome X11 restrictions)
- **MLX Server**: Port 8080
- **Ollama**: Port 11434 (if used)
- **LM Studio**: Port 1234 (if used)

## Backend Selection

The app automatically selects the best available backend:
1. **MLX API** (preferred on Apple Silicon)
2. **Ollama** (if running)
3. **LM Studio** (if running)

## Environment Variables

Key configuration options in `.env`:

```bash
# Backend selection
LLM_BACKEND=auto  # auto, mlx, ollama, lmstudio

# MLX Configuration
MLX_API_URL=http://localhost:8080
MLX_MODEL=mlx-community/Mistral-7B-Instruct-v0.3-4bit
MLX_MAX_TOKENS=1024
MLX_TEMPERATURE=0.7

# Ollama Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# LM Studio Configuration
LMSTUDIO_URL=http://localhost:1234
```

## Troubleshooting

### Common Issues

1. **Port 6000 blocked by Chrome**
   - Solution: App now uses port 5001
   - Chrome blocks port 6000 (X11) for security

2. **MLX server not starting**
   - Check: `python -c "import mlx_lm"`
   - Install: `pip install mlx-lm`

3. **Flask app can't connect to MLX**
   - Check MLX server is running: `curl http://localhost:8080/health`
   - Check firewall/network settings

4. **Virtual environment issues**
   - Recreate: `rm -rf venv && python -m venv venv`
   - Reinstall: `source venv/bin/activate && pip install -r requirements.txt`

### Health Checks

```bash
# Check MLX server
curl http://localhost:8080/health

# Check Flask app
curl http://localhost:5001/api/status

# Test full workflow
curl -X POST -H "Content-Type: application/json" \
  -d '{"prompt": "test prompt"}' \
  http://localhost:5001/api/optimize
```

## Performance Notes

- **Model Loading**: First request may take 30-60 seconds
- **Analysis**: Typically 10-30 seconds per prompt
- **Optimization**: Additional 10-30 seconds
- **Memory**: ~4-8GB RAM for 4-bit models

## Production Considerations

For production deployment:
1. Use proper WSGI server (gunicorn, uWSGI)
2. Set up reverse proxy (nginx)
3. Configure proper logging
4. Use environment-specific configs
5. Set up monitoring and health checks
