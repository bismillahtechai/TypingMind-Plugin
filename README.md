# Iterative Prompt Chain - TypingMind Plugin

This directory contains the API server implementation for integrating the Iterative Prompt Chain with TypingMind as a plugin.

## Directory Structure

```
TypingMind Plugin/
├── api_server.py            # Main Flask API server
├── iterative_prompt_chain.py # Core prompt chain implementation
├── typingmind_plugin_setup.md # Instructions for setting up the TypingMind plugin
├── requirements.txt         # Python dependencies
├── Dockerfile               # For containerized deployment
├── deploy.sh                # General deployment script
├── render_setup.sh          # Render-specific deployment script
└── README.md                # This file
```

## Deployment to Render

1. Make sure `iterative_prompt_chain.py` is in this directory (copied from parent directory)
2. Run the `render_setup.sh` script to verify everything is ready for deployment
3. Push this directory to a Git repository
4. Create a new Web Service in Render pointing to this repository
5. Configure with the following settings:
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn api_server:app`
6. Add the required environment variables:
   - `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`

## Testing Locally

To test locally before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Flask development server
python api_server.py

# Or with Gunicorn
gunicorn api_server:app
```

## Setting Up the TypingMind Plugin

Once your API server is deployed, follow the instructions in `typingmind_plugin_setup.md` to configure the plugin in TypingMind.

## Common Issues

If you encounter the "ModuleNotFoundError: No module named 'iterative_prompt_chain'" error:

1. Verify that `iterative_prompt_chain.py` exists in the same directory as `api_server.py`
2. Make sure the file has been committed to your Git repository if deploying from version control
3. Check if the import statement in `api_server.py` matches the actual filename and location
