import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-3.6-flash"

    def ask(self, question, data_context):
        prompt = f"""
You are RetailIQ, an AI sales and inventory copilot.

Answer the manager's question using ONLY the verified
retail data provided below.

Rules:
- Never invent numbers or facts.
- Use actual numbers from the data.
- Explain the evidence behind the answer.
- If the data cannot answer the question, say:
  "I don't have enough data to answer that."
- Give a practical recommendation when appropriate.
- Clearly state assumptions for predictions.

MANAGER QUESTION:
{question}

VERIFIED RETAIL DATA:
{data_context}

Give a concise, manager-friendly answer.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        return response.text


if __name__ == "__main__":
    service = GeminiService()

    result = service.ask(
        "Which product has the biggest sales spike?",
        """
        Product: Mechanical Keyboard
        Recent 7-day sales: 138 units
        Previous 7-day sales: 77 units
        Change: +79.22%
        Alert: Sales Spike
        """
    )

    print(result)