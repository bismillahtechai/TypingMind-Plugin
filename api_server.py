"""
API Server for Iterative Prompt Chain

This Flask server exposes API endpoints that allow the Iterative Prompt Chain
to be used by TypingMind or other applications.
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS  # Important for CORS support
from iterative_prompt_chain import IterativePromptChain
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "ok"})

@app.route('/generate-project-request', methods=['POST'])
def generate_project_request():
    """
    Generate or refine a project request based on an app idea and optional feedback
    
    Expected JSON payload:
    {
        "app_idea": "Description of the app idea",
        "feedback": "Optional feedback to refine the request",
        "api_key": "Optional API key (if not set as environment variable)"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        app_idea = data.get('app_idea')
        if not app_idea:
            return jsonify({"error": "app_idea is required"}), 400
        
        # Optional fields
        feedback = data.get('feedback', '')
        api_key = data.get('api_key')
        
        # If API key provided in request, temporarily set it as environment variable
        if api_key:
            os.environ['ANTHROPIC_API_KEY'] = api_key
        
        # Check if we have any API keys configured
        if not os.environ.get('ANTHROPIC_API_KEY') and not os.environ.get('OPENAI_API_KEY'):
            return jsonify({
                "error": "No API key available. Please provide ANTHROPIC_API_KEY or OPENAI_API_KEY."
            }), 400
            
        # Initialize the prompt chain
        chain = IterativePromptChain()
        
        # Generate project request
        result = chain.generate_project_request(app_idea, feedback)
        
        return jsonify({
            "result": result,
            "success": True
        })
        
    except Exception as e:
        logger.exception("Error generating project request")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/set-project-details', methods=['POST'])
def set_project_details():
    """
    Set project rules and starter template after finalizing the project request
    
    Expected JSON payload:
    {
        "session_id": "Unique session identifier",
        "project_rules": "Technology stack and constraints",
        "starter_template": "Information about the starter template",
        "api_key": "Optional API key (if not set as environment variable)"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Required fields
        project_rules = data.get('project_rules')
        starter_template = data.get('starter_template')
        
        if not project_rules or not starter_template:
            return jsonify({"error": "project_rules and starter_template are required"}), 400
        
        # Optional API key
        api_key = data.get('api_key')
        if api_key:
            os.environ['ANTHROPIC_API_KEY'] = api_key
        
        # Initialize the prompt chain
        # In a real implementation, you would restore the chain state from a database
        # using session_id to maintain state between requests
        chain = IterativePromptChain()
        chain.set_project_details(project_rules, starter_template)
        
        return jsonify({
            "message": "Project details set successfully",
            "success": True
        })
        
    except Exception as e:
        logger.exception("Error setting project details")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/generate-technical-specification', methods=['POST'])
def generate_technical_specification():
    """
    Generate or refine a technical specification based on project request and feedback
    
    Expected JSON payload:
    {
        "session_id": "Unique session identifier",
        "project_request": "Complete project request (if not stored in session)",
        "project_rules": "Technology stack and constraints (if not stored in session)",
        "starter_template": "Information about the starter template (if not stored in session)",
        "feedback": "Optional feedback to refine the specification",
        "api_key": "Optional API key (if not set as environment variable)"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Optional fields
        feedback = data.get('feedback', '')
        api_key = data.get('api_key')
        
        # In a production environment, you would:
        # 1. Retrieve the session from a database using session_id
        # 2. Restore the chain state with all previous steps
        
        # For this demo, we'll create a new chain and set required values directly
        project_request = data.get('project_request')
        project_rules = data.get('project_rules')
        starter_template = data.get('starter_template')
        
        if not project_request or not project_rules or not starter_template:
            return jsonify({
                "error": "project_request, project_rules, and starter_template are required"
            }), 400
        
        if api_key:
            os.environ['ANTHROPIC_API_KEY'] = api_key
            
        # Initialize the chain and set the state
        chain = IterativePromptChain()
        chain.state["project_request"] = project_request
        chain.set_project_details(project_rules, starter_template)
        
        # Generate technical specification
        result = chain.generate_technical_specification(feedback)
        
        return jsonify({
            "result": result,
            "success": True
        })
        
    except Exception as e:
        logger.exception("Error generating technical specification")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/generate-implementation-plan', methods=['POST'])
def generate_implementation_plan():
    """
    Generate or refine an implementation plan
    
    Expected JSON payload similar to technical specification endpoint
    with the addition of technical_specification if not stored in session
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Optional fields
        feedback = data.get('feedback', '')
        api_key = data.get('api_key')
        
        # In a production environment, you would:
        # 1. Retrieve the session from a database using session_id
        # 2. Restore the chain state with all previous steps
        
        # For this demo, we'll create a new chain and set required values directly
        project_request = data.get('project_request')
        project_rules = data.get('project_rules')
        starter_template = data.get('starter_template')
        technical_specification = data.get('technical_specification')
        
        if not all([project_request, project_rules, starter_template, technical_specification]):
            return jsonify({
                "error": "Missing required fields"
            }), 400
        
        if api_key:
            os.environ['ANTHROPIC_API_KEY'] = api_key
            
        # Initialize the chain and set the state
        chain = IterativePromptChain()
        chain.state["project_request"] = project_request
        chain.set_project_details(project_rules, starter_template)
        chain.state["technical_specification"] = technical_specification
        
        # Generate implementation plan
        result = chain.generate_implementation_plan(feedback)
        
        return jsonify({
            "result": result,
            "success": True
        })
        
    except Exception as e:
        logger.exception("Error generating implementation plan")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/generate-code', methods=['POST'])
def generate_code():
    """
    Generate code for a specific implementation step
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Required fields
        step_number = data.get('step_number')
        if step_number is None:
            return jsonify({"error": "step_number is required"}), 400
            
        # Convert to int if it's a string
        if isinstance(step_number, str):
            try:
                step_number = int(step_number)
            except ValueError:
                return jsonify({"error": "step_number must be an integer"}), 400
        
        # Optional fields
        feedback = data.get('feedback', '')
        api_key = data.get('api_key')
        
        # In a production environment, restore the entire chain state
        # For this demo, recreate the chain with necessary state
        project_request = data.get('project_request')
        project_rules = data.get('project_rules')
        starter_template = data.get('starter_template')
        technical_specification = data.get('technical_specification')
        implementation_plan = data.get('implementation_plan')
        existing_code = data.get('existing_code', {})
        
        if not all([project_request, project_rules, starter_template, 
                   technical_specification, implementation_plan]):
            return jsonify({"error": "Missing required fields"}), 400
        
        if api_key:
            os.environ['ANTHROPIC_API_KEY'] = api_key
            
        # Initialize the chain and set the state
        chain = IterativePromptChain()
        chain.state["project_request"] = project_request
        chain.set_project_details(project_rules, starter_template)
        chain.state["technical_specification"] = technical_specification
        chain.state["implementation_plan"] = implementation_plan
        
        # Set existing code for previous steps
        for step, code in existing_code.items():
            chain.state["generated_code"][int(step)] = code
        
        # Generate code for the specified step
        result = chain.generate_code_for_step(step_number, feedback)
        
        return jsonify({
            "result": result,
            "success": True
        })
        
    except Exception as e:
        logger.exception(f"Error generating code: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/full-workflow', methods=['POST'])
def full_workflow():
    """
    A simplified endpoint that runs one complete step of the workflow 
    (useful for TypingMind plugin integration)
    
    Expected JSON payload:
    {
        "app_idea": "Description of the app idea",
        "step": "project_request|technical_specification|implementation_plan|code", 
        "feedback": "Optional feedback for current step",
        "project_request": "Previous step output if applicable",
        "project_rules": "Tech stack info if applicable", 
        "starter_template": "Template info if applicable",
        "technical_specification": "Previous step output if applicable",
        "implementation_plan": "Previous step output if applicable",
        "code_step_number": "Step number for code generation if applicable",
        "api_key": "Optional API key"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        step = data.get('step', 'project_request')
        app_idea = data.get('app_idea')
        feedback = data.get('feedback', '')
        api_key = data.get('api_key')
        
        if not app_idea:
            return jsonify({"error": "app_idea is required"}), 400
            
        # Set API key if provided
        if api_key:
            os.environ['ANTHROPIC_API_KEY'] = api_key
            
        # Initialize chain
        chain = IterativePromptChain()
        
        # Process based on requested step
        if step == 'project_request':
            result = chain.generate_project_request(app_idea, feedback)
            return jsonify({
                "result": result,
                "success": True,
                "step": step
            })
            
        # For subsequent steps, we need previous outputs
        project_request = data.get('project_request')
        
        if not project_request:
            return jsonify({"error": "project_request is required for steps after project_request"}), 400
            
        chain.state["project_request"] = project_request
        
        if step in ['technical_specification', 'implementation_plan', 'code']:
            # We need project rules and starter template
            project_rules = data.get('project_rules')
            starter_template = data.get('starter_template')
            
            if not project_rules or not starter_template:
                return jsonify({
                    "error": "project_rules and starter_template are required"
                }), 400
                
            chain.set_project_details(project_rules, starter_template)
        
        if step == 'technical_specification':
            result = chain.generate_technical_specification(feedback)
            return jsonify({
                "result": result,
                "success": True,
                "step": step
            })
            
        if step in ['implementation_plan', 'code']:
            # We need technical specification
            technical_specification = data.get('technical_specification')
            
            if not technical_specification:
                return jsonify({
                    "error": "technical_specification is required"
                }), 400
                
            chain.state["technical_specification"] = technical_specification
        
        if step == 'implementation_plan':
            result = chain.generate_implementation_plan(feedback)
            return jsonify({
                "result": result,
                "success": True,
                "step": step
            })
            
        if step == 'code':
            # We need implementation plan and code step number
            implementation_plan = data.get('implementation_plan')
            code_step_number = data.get('code_step_number')
            
            if not implementation_plan:
                return jsonify({
                    "error": "implementation_plan is required"
                }), 400
                
            if code_step_number is None:
                return jsonify({
                    "error": "code_step_number is required"
                }), 400
                
            try:
                code_step_number = int(code_step_number)
            except ValueError:
                return jsonify({
                    "error": "code_step_number must be an integer"
                }), 400
                
            chain.state["implementation_plan"] = implementation_plan
            
            # Set any existing code from previous steps
            existing_code = data.get('existing_code', {})
            for step_num, code in existing_code.items():
                chain.state["generated_code"][int(step_num)] = code
            
            result = chain.generate_code_for_step(code_step_number, feedback)
            return jsonify({
                "result": result,
                "success": True,
                "step": step
            })
            
        return jsonify({
            "error": f"Unknown step: {step}",
            "success": False
        }), 400
        
    except Exception as e:
        logger.exception(f"Error in workflow: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 