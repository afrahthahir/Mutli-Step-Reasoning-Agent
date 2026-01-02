import os
import json
import google.generativeai as genai
from typing import List, Dict, Any
import time
from google.api_core import exceptions


# --- configuration ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

PROMPTS = {
    "planner": """Given a user question, output a numbered plan.
    Question: {question}""",
    
    "executor": """Follow this plan. Show intermediate calculations.
    Question: {question}
    Plan: {plan}
    {history}""",
    
    "verifier": """Check the solution. 
    Question: {question}
    Solution: {solution}
    Output format: List exactly 2 checks in this style:
    1. Check Name | Passed: True/False | Details
    2. Check Name | Passed: True/False | Details
    Final Status: PASSED or FAILED""",
    
    "formatter": """Convert everything into this EXACT JSON schema:
    {{
      "answer": "short answer",
      "status": "success" or "failed",
      "reasoning_visible_to_user": "concise explanation",
      "metadata": {{
        "plan": "{plan}",
        "checks": [
          {{ "check_name": "string", "passed": true, "details": "string" }}
        ],
        "retries": {retries}
      }}
    }}
    Context: {solution} | Verification: {verification}"""
}

class MultiStepAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.model = genai.GenerativeModel(model_name)
        self.max_retries = 3

    def _safe_llm_call(self, prompt, is_json=False):
        """Calls LLM with automatic retry on 429 Resource Exhausted errors."""
        for attempt in range(5):
            try:
                config = {"response_mime_type": "application/json"} if is_json else {}
                response = self.model.generate_content(prompt, generation_config=config)
                # Small sleep to respect rate limits (RPM)
                time.sleep(2) 
                return response.text
            except exceptions.ResourceExhausted:
                wait_time = (attempt + 1) * 10
                print(f"Quota reached. Waiting {wait_time}s...")
                time.sleep(wait_time)
        return "ERROR: Quota exceeded"

    def solve(self, question: str):
        retries = 0
        history = ""
        
        # 1. Planner
        plan = self._safe_llm_call(PROMPTS["planner"].format(question=question))

        while retries < self.max_retries:
            # 2. Executor
            solution = self._safe_llm_call(PROMPTS["executor"].format(
                question=question, plan=plan, history=history
            ))

            # 3. Verifier
            verification = self._safe_llm_call(PROMPTS["verifier"].format(
                question=question, solution=solution
            ))

            if "PASSED" in verification.upper():
                # 4. Formatter (Strict JSON)
                final_json_str = self._safe_llm_call(PROMPTS["formatter"].format(
                    plan=plan, solution=solution, verification=verification, retries=retries
                ), is_json=True)
                return json.loads(final_json_str)
            
            history = f"\nPrevious attempt failed: {verification}"
            retries += 1
            print(f"Retrying... (Attempt {retries})")

        return {"status": "failed", "answer": "Could not verify solution."}

# --- Run Tests ---
agent = MultiStepAgent()
questions = [
    "If a train leaves at 14:30 and arrives at 18:05, how long is the journey?",
    "Alice has 3 red apples and twice as many green apples as red. Total?"
]

for q in questions:
    print(f"\nProcessing: {q}")
    result = agent.solve(q)
    print(json.dumps(result, indent=2))