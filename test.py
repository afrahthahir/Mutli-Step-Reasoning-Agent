import json
import time
from agent import MultiStepAgent 

def run_evaluation_suite():
    agent = MultiStepAgent()
    
    # Easy Questions (Basic Arithmetic / Time)
    easy_questions = [
        "What is 15 + 27?",
        "If I have 12 apples and give 4 away, how many are left?",
        "What is 120 divided by 4?",
    ]
    
    # 3-5 Tricky Questions (Ambiguity / Edge Cases / Multi-step)
    tricky_questions = [
        "Is a meeting from 11:45 to 12:15 longer than a meeting from 14:10 to 14:45?", # Comparison / Time boundary
        "If 'a' is 10 and 'b' is twice 'a', what is 'a' plus 'b' minus 5?", # Variable assignment
        "A room is 10ft by 12ft. Each rug is 4ft by 4ft. How many rugs can fit without overlapping?" # Logic/Spatial constraint
    ]
    
    all_tests = [("Easy", q) for q in easy_questions] + [("Tricky", q) for q in tricky_questions]
    
    print(f"{'='*20} STARTING EVALUATION {'='*20}")
    
    for category, question in all_tests:
        print(f"\n[Category: {category}] Question: {question}")
        
        # Execute the agent
        result = agent.solve(question)
        
        # Log the question, the final JSON, verifier status, and retries
        # Note: 'status' in JSON indicates if the verifier ultimately passed
        print(f"Final JSON Output:\n{json.dumps(result, indent=2)}")
        print(f"Verifier Result: {result.get('status', 'failed').upper()}")
        print(f"Agent Retries: {result.get('metadata', {}).get('retries', 0)}")
        print("-" * 50)
        
        # Brief pause to respect rate limits during the batch run
        time.sleep(2)

if __name__ == "__main__":
    run_evaluation_suite()