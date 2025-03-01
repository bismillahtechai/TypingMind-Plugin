# Setting Up the Iterative Web App Developer Plugin for TypingMind

This guide explains how to set up a TypingMind plugin that leverages the Iterative Prompt Chain for web application development. The plugin allows TypingMind users to:

1. Provide an app idea and get a detailed project request
2. Refine the project request through feedback
3. Generate technical specifications
4. Create implementation plans
5. Generate code for each implementation step

## Prerequisites

1. Your API server must be deployed and accessible via HTTPS
2. The API server should have CORS enabled (already configured in our Flask app)
3. Access to TypingMind to create a custom plugin

## Plugin Configuration

### 1. Basic Plugin Information

- **Plugin Name**: Iterative Web App Developer
- **Overview**: 
  ```markdown
  This plugin helps you develop web applications using an iterative approach. 
  It guides you from initial concept to implementation with feedback loops at each step:
  
  1. Start with your app idea ➡ Get a detailed project request
  2. Refine the project request ➡ Generate technical specifications
  3. Refine the specifications ➡ Create implementation plan
  4. Generate code step-by-step
  
  You can provide feedback at each step to refine the outputs before moving to the next stage.
  ```

### 2. OpenAI Function Specification

Copy and paste this into the "OpenAI Function Spec" field:

```json
{
  "name": "iterative_web_app_development",
  "description": "Iteratively develop a web application from an initial idea through planning to code generation, with feedback loops at each step.",
  "parameters": {
    "type": "object",
    "properties": {
      "app_idea": {
        "type": "string",
        "description": "The initial app idea or concept to develop."
      },
      "step": {
        "type": "string",
        "enum": ["project_request", "technical_specification", "implementation_plan", "code"],
        "description": "The current development step to execute."
      },
      "feedback": {
        "type": "string",
        "description": "Optional feedback to refine the output of the current step."
      },
      "project_request": {
        "type": "string",
        "description": "The finalized project request from a previous step."
      },
      "project_rules": {
        "type": "string",
        "description": "Technical constraints and rules for the project (tech stack, frameworks, etc.)."
      },
      "starter_template": {
        "type": "string",
        "description": "Information about the starter template to use."
      },
      "technical_specification": {
        "type": "string",
        "description": "The technical specification from a previous step."
      },
      "implementation_plan": {
        "type": "string",
        "description": "The implementation plan from a previous step."
      },
      "code_step_number": {
        "type": "integer",
        "description": "The implementation step number for code generation."
      }
    },
    "required": ["app_idea", "step"]
  }
}
```

### 3. User Settings (JSON)

```json
{
  "api_endpoint": {
    "type": "string",
    "default": "https://your-api-endpoint.com/full-workflow",
    "description": "The endpoint URL for the iterative prompt chain API"
  },
  "api_key": {
    "type": "string",
    "default": "",
    "description": "Your Anthropic API key (if not configured on the server)"
  }
}
```

### 4. Implementation: HTTP Action

Configure the HTTP Action with these settings:

- **HTTP Method**: POST
- **Endpoint URL**: {api_endpoint}
- **Headers**:
  ```json
  {
    "Content-Type": "application/json"
  }
  ```
- **Body**:
  ```json
  {
    "app_idea": "{app_idea}",
    "step": "{step}",
    "feedback": "{feedback}",
    "project_request": "{project_request}",
    "project_rules": "{project_rules}",
    "starter_template": "{starter_template}",
    "technical_specification": "{technical_specification}",
    "implementation_plan": "{implementation_plan}",
    "code_step_number": {code_step_number},
    "api_key": "{api_key}"
  }
  ```

### 5. Post-Processing (Handlebars Template)

```handlebars
{{#if error}}
**Error:** {{error}}
{{else}}
### Web App Development: {{step}}

{{result}}

---

{{#if (eq step "project_request")}}
**Next steps:** 
1. Review the project request above
2. Provide feedback to refine it or proceed to technical specification
3. If ready to proceed, please also provide:
   - Project rules (tech stack, frameworks, etc.)
   - Starter template information
{{/if}}

{{#if (eq step "technical_specification")}}
**Next steps:** 
1. Review the technical specification above
2. Provide feedback to refine it or proceed to implementation plan
{{/if}}

{{#if (eq step "implementation_plan")}}
**Next steps:** 
1. Review the implementation plan above
2. Provide feedback to refine it or proceed to code generation
3. If ready for code generation, specify which step number to implement
{{/if}}

{{#if (eq step "code")}}
**Next steps:** 
1. Review the generated code above
2. Provide feedback to refine it
3. Proceed to the next implementation step
{{/if}}
{{/if}}
```

## Usage Instructions

Here's how to use the plugin in TypingMind:

1. Enable the "Iterative Web App Developer" plugin in TypingMind
2. Start by asking something like: "I want to create a recipe sharing app"
3. The plugin will generate a project request
4. Provide feedback to refine the request:
   "Please add user authentication and the ability to save favorite recipes"
5. Once satisfied with the project request, provide project rules:
   "Let's use Next.js, TypeScript, and Tailwind CSS. Use a Next.js App Router template."
6. Continue the process through technical specification, implementation plan, and code generation
7. Provide feedback at each step to refine the outputs

## Deployment Guide

1. Deploy the Flask API server:
   ```bash
   # Clone the repository
   git clone https://your-repo.com/iterative-prompt-chain.git
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the server (development)
   python api_server.py
   
   # For production, use gunicorn
   gunicorn --bind 0.0.0.0:5000 api_server:app
   ```

2. Configure your environment variables:
   - Create a `.env` file with either `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
   - Alternatively, users can provide their own API key in the plugin settings

3. Update the `api_endpoint` in the plugin settings to point to your deployed API server

## Troubleshooting

If you encounter issues:

1. Check the server logs for errors
2. Verify your API key is valid
3. Ensure CORS is properly configured
4. Test the API endpoint directly using a tool like Postman before using it with TypingMind 