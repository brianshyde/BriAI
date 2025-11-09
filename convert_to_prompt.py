import json

input_file = "bri_ai_training.jsonl"
output_file = "bri_ai_training_prompt.jsonl"

with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
    for line in f_in:
        data = json.loads(line.strip())
        messages = data["messages"]
        
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        user = next(m["content"] for m in messages if m["role"] == "user")
        assistant = next(m["content"] for m in messages if m["role"] == "assistant")
        
        prompt = f"System: {system}\n\nUser: {user}"
        completion = f"Assistant: {assistant}"
        
        f_out.write(json.dumps({"prompt": prompt, "completion": completion}) + "\n")

print("Converted to prompt/completion format!")
