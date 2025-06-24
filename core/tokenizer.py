import tiktoken

ENC = tiktoken.encoding_for_model("gpt-3.5-turbo")

def count_tokens(text: str) -> int:
    return len(ENC.encode(text)) if text else 0
