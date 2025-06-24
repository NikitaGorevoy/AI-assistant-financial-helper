import time
from utils.logger import log_agent_call
from core.tokenizer import count_tokens

def run_and_log(agent, task: str):
    start = time.time()
    result = agent.run(task)
    end = time.time()

    input_tokens = getattr(agent.model, "last_input_token_count", None)
    output_tokens = getattr(agent.model, "last_output_token_count", None)
    last_thought = ""
    prompt = ""

    # Попытка извлечь информацию из последнего шага
    if hasattr(agent, "memory") and agent.memory.steps:
        last_step = agent.memory.steps[-1]
        prompt = getattr(last_step, "model_input", "") or task
        result_text = getattr(last_step, "model_output", "") or ""
        last_thought = result_text.strip()

    if input_tokens is None:
        input_tokens = count_tokens(prompt)
    if output_tokens is None:
        output_tokens = count_tokens(last_thought)

    log_agent_call(
        user_input=task,
        tool_used="Auto",  # опционально — можно расширить извлечением tool name
        duration=round(end - start, 2),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        final_answer=str(result),
        agent_thought=last_thought,
    )

    return result
