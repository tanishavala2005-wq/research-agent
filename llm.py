import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_llm(temperature=0.3):
    return ChatGoogleGenerativeAI(
        model=os.getenv("MODEL_NAME", "gemini-2.0-flash"),
        temperature=temperature,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

def ask(llm, prompt):
    response = llm.invoke(prompt)
    content = response.content
    if isinstance(content, str):
        return content
    return "".join(
        part.get("text", "") for part in content if isinstance(part, dict)
    )
