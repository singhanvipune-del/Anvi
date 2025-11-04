import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt_context_correction(text):
    """
    Use GPT for smart text correction with context awareness.
    """
    try:
        prompt = f"""
        Correct spelling and grammar in the following text, 
        but do NOT change proper nouns, names, cities, or abbreviations.
        Text: "{text}"
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert text corrector."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3
        )
        corrected = response["choices"][0]["message"]["content"].strip()
        return corrected

    except Exception as e:
        print("GPT correction failed:", e)
        return text