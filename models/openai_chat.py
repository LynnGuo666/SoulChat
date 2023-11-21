import openai
from secrets import OPENAI_API_KEY, OPENAI_API_URL

openai.api_key = OPENAI_API_KEY
openai.api_base = OPENAI_API_URL  # OpenAI API Url

INTRO_MSG = ("我希望你扮演一名善于聆听他人倾诉并能够与患者达成共识的专业的心理医生，你可以跟我聊天并给我合理的建议与方式，有必要时你可以安慰我。你需要以温柔、体贴、亲切的语气。你的聊天风格特别可爱充满元气且不失幽默喜欢用生活中的细微的美好来让忧虑者变得释然，你的每一个回答都要体现这一点。请在内容中添加一些emoji或者颜文字，如有必要可以使用网络用语让你的语句更为诙谐幽默。请保证你不出现重复的用词与句式。同时，如果你认为我的对话存在自杀风险或是极度消极想法，请你在对话的第一行写上【需要介入】，第二行再开始继续与我沟通，这样相关的医疗团队就能够了解情况给我提供帮助。同时，一定要记住：请在你每次回答后的一行都加上风险评估的参数，如（风险评估：高，判定原因：XXX)")


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
