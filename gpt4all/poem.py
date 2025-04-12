from gpt4all import GPT4All 


model = GPT4All(model_name='orca-mini-3b-gguf2-q4_0.gguf', device='gpu')
with model.chat_session():
    response1 = model.generate(prompt='hello', temp=0)
    response2 = model.generate(prompt='write me a short poem', temp=0)
    response3 = model.generate(prompt='thank you', temp=0)
    print(model.current_chat_session)
