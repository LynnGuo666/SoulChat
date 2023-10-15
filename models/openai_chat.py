import openai

openai.api_key = ""  # OpenAI API
openai.api_base = ""  # OpenAI API Url

INTRO_MSG = ("我希望你扮演一名专业的心理医生，你可以跟我聊天并给我合理的建议与方式，有必要时你可以安慰我。你需要以温柔、体贴、亲切的语气。你的聊天风格特别可爱有趣，你的每一个回答都要体现这一点。你可以加一些emoji"
             "。同时，如果你认为我的对话存在自杀风险，请你在对话中直接回答"
             "【需要介入】，不要返回其他语句，这样会有一位专业的心理医生和医疗团队来帮助我。同时，一定要记住：请在你每次回答的末尾都加上风险评估的参数，如（风险评估：高）。")

def gpt_35_api_stream(messages: list):
    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages,
            temperature=0.6,
            stream=True,
        )
        completion = {'role': '', 'content': ''}
        for event in response:
            if event['choices'][0]['finish_reason'] == 'stop':
                break
            for delta_k, delta_v in event['choices'][0]['delta'].items():
                completion[delta_k] += delta_v
        messages.append(completion)
        return True, ''
    except Exception as err:
        return False, f'OpenAI API 异常: {err}'
