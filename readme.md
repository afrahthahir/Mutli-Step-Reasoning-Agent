
# Multi-Step Reasoning Agent with Self-Checking

This repository contains a Python-based reasoning agent designed to solve complex word problems using a **Planner-Executor-Verifier** architecture. The agent leverages the Gemini 2.5 Flash API to decompose problems, execute logic, and verify its own results before returning a structured JSON response.

## 1. How to Run

### Prerequisites

* Python 3.10+
* A Google Gemini API Key ([Get one here](https://aistudio.google.com/))

### Installation

1. Clone this repository:

2. Install dependencies:
```bash
pip install -U google-generativeai

```


3. Set your API Key:
```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```



### Execution

Run the evaluation suite (which includes 10 easy and 5 tricky cases):

```bash
python test.py

```

## 2. Where Prompts Live

All prompts are stored in a centralized dictionary named `PROMPTS` within `agent.py`. This design ensures that logic is separated from instructions, making it easier to version-control and iterate on prompt engineering without touching the core agent loop.

## 3. Prompt Documentation

### Design Philosophy

I implemented a **modular reasoning loop** to overcome the "hallucination" tendency of LLMs in mathematical tasks:

* **Planner:** Forces the model to identify variables and constraints *before* calculating. This prevents the model from rushing into an incorrect calculation.
* **Executor:** Specifically instructed to show "scratchpad" math. By showing intermediate steps, the model is more likely to maintain logical consistency.
* **Verifier:** Acts as an independent auditor. It is prompted to look for common pitfalls like "midnight rollovers" or "off-by-one" errors.
* **Formatter:** A final stage that strips out the raw "Chain-of-Thought" logs to ensure the user only sees a clean, concise summary as per the assignment requirements.

### What didn't work well

* **Single-Prompt Logic:** Initially, I tried a single prompt to "think and then output JSON." The model often failed on tricky time calculations (e.g., 23:30 to 01:15) because it tried to compute the answer and format the JSON simultaneously.

### Improvements with more time

* **Tool Use (Code Execution):** I would integrate the Gemini Code Interpreter tool to perform arithmetic in Python rather than relying on the LLM's internal math, which would guarantee 100% calculation accuracy.

## 4. Assumptions

* **Timezone:** All time-based questions assume the same timezone unless otherwise specified.
* **Rate Limits:** The code assumes a Gemini Free Tier quota (15 RPM). I have implemented a `time.sleep(4)` and a retry-with-backoff mechanism to prevent `429 ResourceExhausted` errors.
* **JSON Strictness:** The agent assumes that if the Verifier passes, the Formatter will produce valid JSON. As a fallback, I used Gemini's `response_mime_type: "application/json"` configuration.

## 5. Example Run Logs

### Test Case: Time Calculation

**Question:** If a train leaves at 14:30 and arrives at 18:05, how long is the journey?

```json
{
  "answer": "3 hours and 35 minutes",
  "status": "success",
  "reasoning_visible_to_user": "The total journey duration is calculated by adding the minutes from the start time to the next full hour, the number of full hours between, and the minutes from the last full hour to the arrival time.",
  "metadata": {
    "plan": "1. Determine minutes to next full hour. 2. Calculate full hours. 3. Determine remaining minutes.",
    "checks": [
      {
        "check_name": "Calculation Accuracy Check",
        "passed": true,
        "details": "All intermediate calculations (30m, 3h, 5m) are correct."
      }
    ],
    "retries": 0
  }
}

```

### Test Case: Logic/Arithmetic

**Question:** Alice has 3 red apples and twice as many green apples as red. Total?

```json
{
  "answer": "9 apples",
  "status": "success",
  "reasoning_visible_to_user": "Alice has 3 red apples. Since she has twice as many green apples, she has 6 green apples. Adding them together gives 9.",
  "metadata": {
    "plan": "1. Identify red apples. 2. Calculate green apples. 3. Sum total.",
    "checks": [{"check_name": "Multiplication Check", "passed": true, "details": "3 * 2 = 6"}],
    "retries": 0
  }
}

```
