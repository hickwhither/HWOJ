def check(output_path="output", answer_path="answer"):
    with open(output_path, 'r', encoding='utf-8') as f_out, open(answer_path, 'r', encoding='utf-8') as f_ans:
        out_tokens = f_out.read().split()
        ans_tokens = f_ans.read().split()
    
    if len(ans_tokens) != len(out_tokens):
        return "The number of output tokens does not match."
    for i, (token_out, token_ans) in enumerate(zip(out_tokens, ans_tokens)):
        if token_out != token_ans:
            return f"Token #{i}: expected '{token_ans}', got '{token_out}'"
    return None
