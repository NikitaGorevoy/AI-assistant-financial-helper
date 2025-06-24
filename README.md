# AI-assistant-financial-helper

#### This project is an AI agent that helps users:

* Analyze financial documents (like deposit or loan agreements)
* Explain legal terms and regulations
* Show current currency exchange rates
* Find financial news
* Work with uploaded .pdf, .docx, or .txt files
* Keep a history of all queries

#### How to run

* Install dependencies:

```pip install -r requirements.txt```

* Run agent.ipynb

#### File overview

* agent.ipynb – main demo with examples
* tools/ – agent tools (contracts, news, currency)
* prompts/ – system prompt and examples for the agent
* logs/, agent_calls.csv – query history
* eval_tasks.jsonl – simple keyword-based tests
  
The agent runs locally with a simple interface and supports document upload and analysis.
