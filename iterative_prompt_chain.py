"""
Iterative Prompt Chain Implementation for Web App Development

This script implements a truly iterative prompt chain for web application development
using Langchain. It guides the user from initial concept to optimized code, with
feedback loops at each step.
"""

import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic  # Add Anthropic import
from langchain.memory import ConversationBufferMemory

# Load environment variables
load_dotenv()

class IterativePromptChain:
    def __init__(self, use_anthropic=True):
        # Initialize the LLMs with appropriate temperature for different steps
        if use_anthropic:
            # Use Anthropic Claude models
            self.planning_llm = ChatAnthropic(temperature=0.7, model="claude-3-sonnet-20240229")  # More creative for planning/ideation
            self.implementation_llm = ChatAnthropic(temperature=0.2, model="claude-3-opus-20240229")  # More precise for implementation
        else:
            # Use OpenAI models as fallback
            self.planning_llm = ChatOpenAI(temperature=0.7)  # More creative for planning/ideation
            self.implementation_llm = ChatOpenAI(temperature=0.2)  # More precise for implementation
        
        # Initialize memory for each step to maintain context during iterations
        self.project_request_memory = ConversationBufferMemory(
            input_key="idea",
            memory_key="chat_history",
            return_messages=True
        )
        
        self.tech_spec_memory = ConversationBufferMemory(
            input_key="project_request",
            memory_key="chat_history",
            return_messages=True
        )
        
        self.implementation_plan_memory = ConversationBufferMemory(
            input_key="technical_specification",
            memory_key="chat_history",
            return_messages=True
        )
        
        self.code_generator_memory = ConversationBufferMemory(
            input_key="implementation_plan",
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize state to store results from each step
        self.state = {
            "project_request": None,
            "project_rules": None,  # Will be provided by user after project request
            "starter_template": None,  # Will be provided by user after project request
            "technical_specification": None,
            "implementation_plan": None,
            "generated_code": {},  # Will store code for each step
            "optimization_plan": None,
            "optimized_code": {}   # Will store optimized code for each step
        }
        
        # Initialize chains
        self._init_chains()
    
    def _init_chains(self):
        # Step 1: Project Request Generator Chain
        self.project_request_template = PromptTemplate(
            input_variables=["idea", "feedback"],
            template="""
            ## 1. Project Request Generator

            I have a web app idea I'd like to develop. Here's my initial concept:

            {idea}

            I'm looking to collaborate with you to turn this into a detailed project request. Let's iterate together until we have a complete request that I find to be complete.

            {feedback}

            Please return the current state of the request in this format:

            ```request
            # Project Name
            ## Project Description
            [Description]

            ## Target Audience
            [Target users]

            ## Desired Features
            ### [Feature Category]
            - [ ] [Requirement]
                - [ ] [Sub-requirement]

            ## Design Requests
            - [ ] [Design requirement]
                - [ ] [Design detail]

            ## Other Notes
            - [Additional considerations]
            ```

            Please:
            1. Ask me questions about any areas that need more detail
            2. Suggest features or considerations I might have missed
            3. Help me organize requirements logically
            4. Show me the current state of the spec
            5. Flag any potential technical challenges or important decisions
            """
        )
        
        self.project_request_chain = LLMChain(
            llm=self.planning_llm,
            prompt=self.project_request_template,
            output_key="project_request",
            verbose=True,
            memory=self.project_request_memory
        )
        
        # Step 2: Technical Specification Generator Chain
        self.tech_spec_template = PromptTemplate(
            input_variables=["project_request", "project_rules", "starter_template", "feedback"],
            template="""
            ## 2. Technical Specification Generator

            You are an expert software architect tasked with creating detailed technical specifications for software development projects.

            Your specifications will be used as direct input for planning & code generation AI systems, so they must be precise, structured, and comprehensive.

            First, carefully review the project request:

            <project_request>
            {project_request}
            </project_request>

            Next, carefully review the project rules:

            <project_rules>
            {project_rules}
            </project_rules>

            Finally, carefully review the starter template:

            <starter_template>
            {starter_template}
            </starter_template>

            User feedback on previous iteration (if any):
            {feedback}

            Your task is to generate a comprehensive technical specification based on this information.

            Begin with your specification planning, considering:
            1. Core system architecture and key workflows
            2. Project structure and organization
            3. Detailed feature specifications
            4. Database schema design
            5. Server actions and integrations
            6. Design system and component architecture
            7. Authentication and authorization implementation
            8. Data flow and state management
            9. Payment implementation
            10. Analytics implementation
            11. Testing strategy

            Then generate the technical specification using this markdown structure:

            ```markdown
            # {Project Name} Technical Specification

            ## 1. System Overview
            - Core purpose and value proposition
            - Key workflows
            - System architecture

            ## 2. Project Structure
            - Detailed breakdown of project structure & organization

            ## 3. Feature Specification
            For each feature:
            ### 3.1 Feature Name
            - User story and requirements
            - Detailed implementation steps
            - Error handling and edge cases

            ## 4. Database Schema
            ### 4.1 Tables
            For each table:
            - Complete table schema (field names, types, constraints)
            - Relationships and indexes

            ## 5. Server Actions
            ### 5.1 Database Actions
            For each action:
            - Detailed description of the action
            - Input parameters and return values
            - SQL queries or ORM operations

            ### 5.2 Other Actions
            - External API integrations (endpoints, authentication, data formats)
            - File handling procedures
            - Data processing algorithms

            ## 6. Design System
            ### 6.1 Visual Style
            - Color palette (with hex codes)
            - Typography (font families, sizes, weights)
            - Component styling patterns
            - Spacing and layout principles

            ### 6.2 Core Components
            - Layout structure (with examples)
            - Navigation patterns
            - Shared components (with props and usage examples)
            - Interactive states (hover, active, disabled)

            ## 7. Component Architecture
            ### 7.1 Server Components
            - Data fetching strategy
            - Suspense boundaries
            - Error handling
            - Props interface (with TypeScript types)

            ### 7.2 Client Components
            - State management approach
            - Event handlers
            - UI interactions
            - Props interface (with TypeScript types)

            ## 8. Authentication & Authorization
            - Clerk implementation details
            - Protected routes configuration
            - Session management strategy

            ## 9. Data Flow
            - Server/client data passing mechanisms
            - State management architecture

            ## 10. Stripe Integration
            - Payment flow diagram
            - Webhook handling process
            - Product/Price configuration details

            ## 11. PostHog Analytics
            - Analytics strategy
            - Event tracking implementation
            - Custom property definitions

            ## 12. Testing
            - Unit tests with Jest (example test cases)
            - e2e tests with Playwright (key user flows to test)
            ```

            Ensure that your specification is extremely detailed, providing specific implementation guidance wherever possible. Include concrete examples for complex features and clearly define interfaces between components.
            """
        )
        
        self.tech_spec_chain = LLMChain(
            llm=self.planning_llm,
            prompt=self.tech_spec_template,
            output_key="technical_specification",
            verbose=True,
            memory=self.tech_spec_memory
        )
        
        # Step 3: Implementation Plan Generator Chain
        self.implementation_plan_template = PromptTemplate(
            input_variables=["project_request", "project_rules", "technical_specification", "starter_template", "feedback"],
            template="""
            ## 3. Implementation Plan Generator

            You are an AI task planner responsible for breaking down a complex web application development project into manageable steps.

            Your goal is to create a detailed, step-by-step plan that will guide the code generation process for building a fully functional web application based on a provided technical specification.

            First, carefully review the following inputs:

            <project_request>
            {project_request}
            </project_request>

            <project_rules>
            {project_rules}
            </project_rules>

            <technical_specification>
            {technical_specification}
            </technical_specification>

            <starter_template>
            {starter_template}
            </starter_template>

            User feedback on previous iteration (if any):
            {feedback}

            After reviewing these inputs, your task is to create a comprehensive, detailed plan for implementing the web application.

            Begin with your brainstorming, then create a detailed implementation plan in the format:

            ```md
            # Implementation Plan

            ## [Section Name]
            - [ ] Step 1: [Brief title]
              - **Task**: [Detailed explanation of what needs to be implemented]
              - **Files**: [Maximum of 20 files, ideally less]
                - `path/to/file1.ts`: [Description of changes]
              - **Step Dependencies**: [Step Dependencies]
              - **User Instructions**: [Instructions for User]
            ```

            Ensure each step is atomic, builds logically on previous steps, and can be implemented in a single iteration.
            """
        )
        
        self.implementation_plan_chain = LLMChain(
            llm=self.planning_llm,
            prompt=self.implementation_plan_template,
            output_key="implementation_plan",
            verbose=True,
            memory=self.implementation_plan_memory
        )
        
        # Step 4: Code Generator Chain
        self.code_generator_template = PromptTemplate(
            input_variables=["project_request", "project_rules", "technical_specification", "implementation_plan", "existing_code", "current_step", "feedback"],
            template="""
            ## 4. Code Generator

            You are an AI code generator responsible for implementing a web application based on a provided technical specification and implementation plan.

            Your task is to systematically implement each step of the plan, one at a time.

            First, carefully review the following inputs:

            <project_request>
            {project_request}
            </project_request>

            <project_rules>
            {project_rules}
            </project_rules>

            <technical_specification>
            {technical_specification}
            </technical_specification>

            <implementation_plan>
            {implementation_plan}
            </implementation_plan>

            <existing_code>
            {existing_code}
            </existing_code>

            <feedback>
            {feedback}
            </feedback>

            Your task is to:
            1. Implement step #{current_step} from the implementation plan
            2. Generate the necessary code for all files specified in that step
            3. Return the generated code using the XML format

            For EVERY file you modify or create, provide the COMPLETE file contents using this XML structure:

            ```xml
            <code_changes>
              <changed_files>
                <file>
                  <file_operation>CREATE or UPDATE or DELETE</file_operation>
                  <file_path>path/to/file</file_path>
                  <file_code><![CDATA[
            /**
             * Complete file contents with extensive documentation
             */
            // Complete implementation with inline comments & documentation...
            ]]></file_code>
                </file>
                <!-- Additional files as needed -->
              </changed_files>
            </code_changes>
            ```

            Include comprehensive documentation:
            - File-level purpose and scope
            - Component/function-level documentation 
            - Inline comments for complex logic
            - Type documentation for interfaces and types
            - Notes about edge cases and error handling

            After the code, include:
            - "STEP {current_step} COMPLETE" with an explanation of what you did
            - User instructions for any manual steps required
            """
        )
        
        self.code_generator_chain = LLMChain(
            llm=self.implementation_llm,
            prompt=self.code_generator_template,
            output_key="generated_code",
            verbose=True,
            memory=self.code_generator_memory
        )
        
        # Step 5: Code Optimization Planner Chain
        self.optimization_planner_template = PromptTemplate(
            input_variables=["project_request", "project_rules", "technical_specification", "implementation_plan", "existing_code", "feedback"],
            template="""
            ## 5. Code Optimization Planner

            You are an expert code reviewer and optimizer responsible for analyzing the implemented code and creating a detailed optimization plan.

            Please review the following context and implementation:

            <project_request>
            {project_request}
            </project_request>

            <project_rules>
            {project_rules}
            </project_rules>

            <technical_specification>
            {technical_specification}
            </technical_specification>

            <implementation_plan>
            {implementation_plan}
            </implementation_plan>

            <existing_code>
            {existing_code}
            </existing_code>

            <feedback>
            {feedback}
            </feedback>

            First, analyze the implemented code against the original requirements and plan, considering:
            1. Code Organization and Structure
            2. Code Quality and Best Practices
            3. UI/UX Improvements

            Then create a detailed optimization plan using the following format:

            ```md
            # Optimization Plan
            ## [Category Name]
            - [ ] Step 1: [Brief title]
              - **Task**: [Detailed explanation of what needs to be optimized/improved]
              - **Files**: [List of files]
                - `path/to/file1.ts`: [Description of changes]
              - **Step Dependencies**: [Any steps that must be completed first]
              - **User Instructions**: [Any manual steps required]
            ```

            Focus on specific, concrete improvements with manageable changes (no more than 20 files per step, ideally less).
            """
        )
        
        self.optimization_planner_chain = LLMChain(
            llm=self.planning_llm,
            prompt=self.optimization_planner_template,
            output_key="optimization_plan",
            verbose=True
        )
        
        # Step 6: Code Optimization Generator Chain
        self.optimization_generator_template = PromptTemplate(
            input_variables=["optimization_plan", "existing_code", "current_optimization_step", "feedback"],
            template="""
            ## 6. Code Optimization Generator

            You are an AI code optimizer responsible for implementing the optimization steps identified in the optimization plan.

            Your task is to systematically implement each optimization step, one at a time.

            <optimization_plan>
            {optimization_plan}
            </optimization_plan>

            <existing_code>
            {existing_code}
            </existing_code>

            <feedback>
            {feedback}
            </feedback>

            Your task is to:
            1. Implement optimization step #{current_optimization_step} from the optimization plan
            2. Generate the optimized code for all files specified in that step
            3. Return the optimized code using the XML format

            For EVERY file you modify, provide the COMPLETE file contents using this XML structure:

            ```xml
            <code_changes>
              <changed_files>
                <file>
                  <file_operation>UPDATE</file_operation>
                  <file_path>path/to/file</file_path>
                  <file_code><![CDATA[
            /**
             * Complete optimized file contents with extensive documentation
             */
            // Complete implementation with inline comments explaining optimizations...
            ]]></file_code>
                </file>
                <!-- Additional files as needed -->
              </changed_files>
            </code_changes>
            ```

            After the code, include:
            - "OPTIMIZATION STEP {current_optimization_step} COMPLETE" with an explanation of the optimizations
            - Details on the improvements made and their benefits
            - User instructions for any manual steps required
            """
        )
        
        self.optimization_generator_chain = LLMChain(
            llm=self.implementation_llm,
            prompt=self.optimization_generator_template,
            output_key="optimized_code",
            verbose=True
        )
    
    # Step 1: Generate Project Request (iterative)
    def generate_project_request(self, idea, feedback=""):
        """
        Step 1: Generates or refines a project request based on the initial idea and user feedback.
        This function can be called multiple times to refine the request based on feedback.
        """
        result = self.project_request_chain({
            "idea": idea,
            "feedback": feedback
        })
        self.state["project_request"] = result["project_request"]
        return self.state["project_request"]
    
    # Set project rules and starter template after project request is finalized
    def set_project_details(self, project_rules, starter_template):
        """
        After the project request is finalized, the user can provide project rules and starter template.
        """
        self.state["project_rules"] = project_rules
        self.state["starter_template"] = starter_template
    
    # Step 2: Generate Technical Specification (iterative)
    def generate_technical_specification(self, feedback=""):
        """
        Step 2: Generates or refines a technical specification based on the project request and user feedback.
        This function can be called multiple times to refine the specification based on feedback.
        """
        if not self.state["project_request"]:
            raise ValueError("Project request must be generated and finalized first")
        
        if not self.state["project_rules"] or not self.state["starter_template"]:
            raise ValueError("Project rules and starter template must be set before generating technical specification")
        
        result = self.tech_spec_chain({
            "project_request": self.state["project_request"],
            "project_rules": self.state["project_rules"],
            "starter_template": self.state["starter_template"],
            "feedback": feedback
        })
        self.state["technical_specification"] = result["technical_specification"]
        return self.state["technical_specification"]
    
    # Step 3: Generate Implementation Plan (iterative)
    def generate_implementation_plan(self, feedback=""):
        """
        Step 3: Generates or refines an implementation plan based on the technical specification and user feedback.
        This function can be called multiple times to refine the plan based on feedback.
        """
        if not self.state["technical_specification"]:
            raise ValueError("Technical specification must be generated and finalized first")
        
        result = self.implementation_plan_chain({
            "project_request": self.state["project_request"],
            "project_rules": self.state["project_rules"],
            "technical_specification": self.state["technical_specification"],
            "starter_template": self.state["starter_template"],
            "feedback": feedback
        })
        self.state["implementation_plan"] = result["implementation_plan"]
        return self.state["implementation_plan"]
    
    # Step 4: Generate Code for a specific step (iterative)
    def generate_code_for_step(self, step_number, feedback=""):
        """
        Step 4: Generates or refines code for a specific implementation step based on user feedback.
        This function can be called multiple times to refine the code based on feedback.
        """
        if not self.state["implementation_plan"]:
            raise ValueError("Implementation plan must be generated and finalized first")
        
        # Get existing code (all previously generated code combined)
        existing_code = "\n\n".join([code for step, code in self.state["generated_code"].items() if step < step_number])
        
        if not existing_code:
            existing_code = "// No existing code yet"
        
        result = self.code_generator_chain({
            "project_request": self.state["project_request"],
            "project_rules": self.state["project_rules"],
            "technical_specification": self.state["technical_specification"],
            "implementation_plan": self.state["implementation_plan"],
            "existing_code": existing_code,
            "current_step": step_number,
            "feedback": feedback
        })
        
        # Store the result
        self.state["generated_code"][step_number] = result["generated_code"]
        return result["generated_code"]
    
    # Step 5: Generate Optimization Plan (iterative)
    def generate_optimization_plan(self, feedback=""):
        """
        Step 5: Generates or refines an optimization plan based on the implemented code and user feedback.
        This function can be called multiple times to refine the plan based on feedback.
        """
        if not self.state["generated_code"]:
            raise ValueError("Code must be generated before creating an optimization plan")
        
        # Combine all generated code
        all_code = "\n\n".join([code for _, code in sorted(self.state["generated_code"].items())])
        
        result = self.optimization_planner_chain({
            "project_request": self.state["project_request"],
            "project_rules": self.state["project_rules"],
            "technical_specification": self.state["technical_specification"],
            "implementation_plan": self.state["implementation_plan"],
            "existing_code": all_code,
            "feedback": feedback
        })
        
        self.state["optimization_plan"] = result["optimization_plan"]
        return self.state["optimization_plan"]
    
    # Step 6: Generate Optimized Code for a specific step (iterative)
    def generate_optimized_code_for_step(self, step_number, feedback=""):
        """
        Step 6: Generates or refines optimized code for a specific optimization step based on user feedback.
        This function can be called multiple times to refine the code based on feedback.
        """
        if not self.state["optimization_plan"]:
            raise ValueError("Optimization plan must be generated and finalized first")
        
        # Get existing code (all implementation code + previously optimized code)
        existing_code = "\n\n".join([code for _, code in sorted(self.state["generated_code"].items())])
        
        # Add previously optimized code
        for opt_step, code in self.state["optimized_code"].items():
            if opt_step < step_number:
                existing_code += f"\n\n{code}"
        
        result = self.optimization_generator_chain({
            "optimization_plan": self.state["optimization_plan"],
            "existing_code": existing_code,
            "current_optimization_step": step_number,
            "feedback": feedback
        })
        
        # Store the result
        self.state["optimized_code"][step_number] = result["optimized_code"]
        return result["optimized_code"]
    
    # Helper method to get the current state
    def get_state(self):
        """
        Returns the current state of the prompt chain.
        """
        return self.state


# Example usage with an interactive workflow
def interactive_workflow_example():
    print("=== INTERACTIVE WEB APP DEVELOPMENT WORKFLOW ===\n")
    
    # Check for API keys
    if os.getenv("ANTHROPIC_API_KEY"):
        api_provider = "anthropic"
        use_anthropic = True
        print("Using Anthropic Claude API")
    elif os.getenv("OPENAI_API_KEY"):
        api_provider = "openai"
        use_anthropic = False
        print("Using OpenAI API")
    else:
        print("Error: No API key found. Please set either ANTHROPIC_API_KEY or OPENAI_API_KEY in your .env file.")
        return
    
    # Initialize the prompt chain with the appropriate provider
    prompt_chain = IterativePromptChain(use_anthropic=use_anthropic)
    
    # Step 1: Start with the initial idea
    print("STEP 1: ENTER YOUR APP IDEA")
    initial_idea = input("Enter your app idea: ")
    
    # Generate the initial project request
    print("\nGenerating initial project request...")
    project_request = prompt_chain.generate_project_request(initial_idea)
    print("\nINITIAL PROJECT REQUEST:")
    print(project_request)
    
    # Iterate on the project request until satisfied
    while True:
        feedback = input("\nProvide feedback on the project request (or type 'done' to finalize): ")
        if feedback.lower() == 'done':
            break
        
        # Update the project request based on feedback
        print("\nUpdating project request...")
        project_request = prompt_chain.generate_project_request(initial_idea, feedback)
        print("\nUPDATED PROJECT REQUEST:")
        print(project_request)
    
    # After finalizing the project request, get project rules and starter template
    print("\nSTEP 2: ENTER PROJECT RULES AND STARTER TEMPLATE")
    project_rules = input("Enter project rules (technologies, constraints, etc.): ")
    starter_template = input("Enter starter template information: ")
    
    # Set the project details
    prompt_chain.set_project_details(project_rules, starter_template)
    
    # Generate the initial technical specification
    print("\nGenerating technical specification...")
    tech_spec = prompt_chain.generate_technical_specification()
    print("\nINITIAL TECHNICAL SPECIFICATION:")
    print(tech_spec[:1000] + "...\n(truncated for readability)")
    
    # Iterate on the technical specification until satisfied
    while True:
        feedback = input("\nProvide feedback on the technical specification (or type 'done' to finalize): ")
        if feedback.lower() == 'done':
            break
        
        # Update the technical specification based on feedback
        print("\nUpdating technical specification...")
        tech_spec = prompt_chain.generate_technical_specification(feedback)
        print("\nUPDATED TECHNICAL SPECIFICATION:")
        print(tech_spec[:1000] + "...\n(truncated for readability)")
    
    # Generate the initial implementation plan
    print("\nSTEP 3: GENERATE IMPLEMENTATION PLAN")
    print("\nGenerating implementation plan...")
    impl_plan = prompt_chain.generate_implementation_plan()
    print("\nINITIAL IMPLEMENTATION PLAN:")
    print(impl_plan[:1000] + "...\n(truncated for readability)")
    
    # Iterate on the implementation plan until satisfied
    while True:
        feedback = input("\nProvide feedback on the implementation plan (or type 'done' to finalize): ")
        if feedback.lower() == 'done':
            break
        
        # Update the implementation plan based on feedback
        print("\nUpdating implementation plan...")
        impl_plan = prompt_chain.generate_implementation_plan(feedback)
        print("\nUPDATED IMPLEMENTATION PLAN:")
        print(impl_plan[:1000] + "...\n(truncated for readability)")
    
    # Generate code for each step in the implementation plan
    print("\nSTEP 4: GENERATE CODE (EXAMPLE WITH STEP 1)")
    print("\nGenerating code for step 1...")
    code = prompt_chain.generate_code_for_step(1)
    print("\nGENERATED CODE (STEP 1):")
    print(code[:1000] + "...\n(truncated for readability)")
    
    # Example of iterating on the code for step 1
    feedback = input("\nProvide feedback on the generated code (or press Enter to skip): ")
    if feedback:
        print("\nUpdating code based on feedback...")
        code = prompt_chain.generate_code_for_step(1, feedback)
        print("\nUPDATED CODE (STEP 1):")
        print(code[:1000] + "...\n(truncated for readability)")
    
    # In a real scenario, you would continue for all steps in the implementation plan
    print("\nNote: In a real scenario, you would continue generating code for all steps in the implementation plan.")
    
    # Generate the optimization plan
    print("\nSTEP 5: GENERATE OPTIMIZATION PLAN")
    print("\nGenerating optimization plan...")
    opt_plan = prompt_chain.generate_optimization_plan()
    print("\nOPTIMIZATION PLAN:")
    print(opt_plan[:1000] + "...\n(truncated for readability)")
    
    # Example of iterating on the optimization plan
    feedback = input("\nProvide feedback on the optimization plan (or press Enter to skip): ")
    if feedback:
        print("\nUpdating optimization plan based on feedback...")
        opt_plan = prompt_chain.generate_optimization_plan(feedback)
        print("\nUPDATED OPTIMIZATION PLAN:")
        print(opt_plan[:1000] + "...\n(truncated for readability)")
    
    # Generate optimized code for step 1
    print("\nSTEP 6: GENERATE OPTIMIZED CODE (EXAMPLE WITH STEP 1)")
    print("\nGenerating optimized code for step 1...")
    opt_code = prompt_chain.generate_optimized_code_for_step(1)
    print("\nOPTIMIZED CODE (STEP 1):")
    print(opt_code[:1000] + "...\n(truncated for readability)")
    
    print("\n=== WORKFLOW COMPLETE ===")
    print("You have successfully completed an example of the interactive web app development workflow.")
    print("In a real scenario, you would continue through all implementation and optimization steps.")


if __name__ == "__main__":
    interactive_workflow_example() 