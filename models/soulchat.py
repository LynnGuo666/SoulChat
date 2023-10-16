import torch
from transformers import AutoModel, AutoTokenizer

# GPU设置
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 加载模型与tokenizer
model_name_or_path = 'scutcyr/SoulChat'
model = AutoModel.from_pretrained(model_name_or_path, trust_remote_code=True).half()
model.to(device)
tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)

def chat_with_soulchat(user_input):
    input_text = "用户：" + user_input + "\n心理咨询师："
    response, _ = model.chat(tokenizer, query=input_text, history=None, max_length=2048, num_beams=1, do_sample=True, top_p=0.75, temperature=0.95, logits_processor=None)
    return response

