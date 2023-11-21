import torch
from transformers import AutoModel, AutoTokenizer

# GPU设置
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 加载模型与tokenizer
model_name_or_path = 'scutcyr/SoulChat'
model = AutoModel.from_pretrained(model_name_or_path, trust_remote_code=True).half()
model.to(device)
tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)


def chat_with_soulchat(user_input, user_history=None, bot_history=None):
    if user_history and bot_history:
        # 多轮对话模式
        context = "\n".join([f"用户：{user_history[i]}\n心理咨询师：{bot_history[i]}" for i in range(len(bot_history))])
        input_text = context + "\n用户：" + user_history[-1] + "\n心理咨询师："
    else:
        # 单轮对话模式
        input_text = "用户：" + user_input + "\n心理咨询师："

    encoded_input = tokenizer.encode(input_text, return_tensors="pt", max_length=2048, truncation=True).to(device)
    output = model.generate(encoded_input, max_length=2048, num_beams=1, do_sample=True, top_p=0.75, temperature=0.95)
    response = tokenizer.decode(output[0], skip_special_tokens=True)

    # 提取心理咨询师的回复
    response = response.split("\n心理咨询师：")[-1].strip()

    return response
