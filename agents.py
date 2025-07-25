from langchain.schema import SystemMessage

ROLE_PROMPTS = {
    "司会者": "あなたは司会者です。50字程度で議論をまとめ、他者に発言を促してください。",
    "批判者": "あなたは批判者です。50字程度で意見の欠点や問題点を指摘してください。",
    "指導者": "あなたは指導者です。50字程度で経験と知識に基づいた実用的な提案をしてください。",
    "楽観的な提案者": "あなたは楽観的な提案者です。50字程度で前向きな意見や解決策を提示してください。",
    "批判的分析者": "あなたは批判的分析者です。50字程度で意見を構造的に分析し、論理的な指摘をしてください。",
}

def get_agent_by_role(role, model): #このmodel引数に役割固有のLLMが渡される
    def agent_fn(history, topic):
        prompt = f"{ROLE_PROMPTS[role]}\n\n現在の議題: {topic}\n\n会話の履歴:\n"
        for msg in history:
            prompt += f"{msg.content}\n"
        prompt += f"\nあなた（{role}）の次の発言："
        # ここで渡された model インスタンスが使用される
        response = model([SystemMessage(content=prompt)]).content.strip()
        return response
    return agent_fn
