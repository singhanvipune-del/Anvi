import openai

# Context-based text correction using GPT
def gpt_context_correction(text):
    if not text or not isinstance(text, str):
        return text

    prompt = f"Clean and correct the following text while keeping meaning intact:\n\n{text}"

    try:
        from openai import OpenAI
        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a smart AI text corrector."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"⚠️ GPT correction failed: {e}")
        return text