def check():
    with open("output", 'r', encoding='utf-8') as f_out, open("output", 'r', encoding='utf-8') as f_ans:
        out_tokens = f_out.read().split(' ')
        ans_tokens = f_ans.read().split(' ')
    
    if len(ans_tokens) > len(out_tokens):
        return "The number of output tokens does not match."
    min_len = min(len(out_tokens), len(ans_tokens))
    for i in range(min_len):
        token_out = out_tokens[i].strip()
        token_ans = ans_tokens[i].strip()
        
        if token_out != token_ans:
            return f"Token #{i}: expected '{token_ans}', got '{token_out}"
