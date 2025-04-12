from gpt4all import GPT4All
model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf", device='gpu')
tokens = []
with model.chat_session():
    for token in model.generate("What is the capital of France?", streaming=True):
        tokens.append(token)
print(tokens)
