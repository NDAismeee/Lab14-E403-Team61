import asyncio
import os
from typing import Dict
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
from engine.retriever import Retriever

class MainAgentV2:
    """
    Version 2: Keyword RAG with Error Handling
    - Retrieval: Keyword Search (top-3).
    - Generation: Strict prompt (refuse if not found).
    """
    def __init__(self):
        self.name = "SupportAgent-v2"
        self.retriever = Retriever()
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def query(self, question: str) -> Dict:
        try:
            # 1. Retrieval: Lấy dữ liệu từ retriever.py
            search_results = self.retriever.search(question, top_k=3)
            contexts = search_results.get("contexts", [])
            sources = search_results.get("sources", [])

            if not contexts:
                context_str = "Không tìm thấy thông tin liên quan trong tài liệu."
            else:
                context_str = "\n\n".join(contexts)

            # 2. Generation: Tạo kết quả từ LLM
            system_prompt = f"Bạn là trợ lý hỗ trợ nội bộ. Hãy trả lời câu hỏi dựa trên ngữ cảnh: {context_str}. Nếu thông tin không có trong ngữ cảnh, hãy từ chối trả lời và nói bạn không biết."

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ]
            )

            return {
                "answer": response.choices[0].message.content,
                "contexts": contexts,
                "retrieved_ids": search_results.get("retrieved_ids", []),
                "metadata": {
                    "model": "gpt-4o-mini",
                    "tokens_used": response.usage.total_tokens,
                    "sources": list(set(sources)),
                }
            }
        except Exception as e:
            err_msg = str(e)
            print(f"❌ Error in MainAgent.query: {err_msg[:300]}{'...' if len(err_msg) > 300 else ''}")
            return {
                "answer": "Xin lỗi, đã có lỗi xảy ra trong quá trình xử lý yêu cầu của bạn.",
                "contexts": [],
                "retrieved_ids": [],
                "metadata": {
                    "error": str(e),
                    "model": "gpt-4o-mini",
                    "tokens_used": 0,
                    "sources": []
                }
            }

class MainAgentV1:
    """
    Version 1: Keyword RAG Baseline
    - Retrieval: Retriever (top-2).
    - Generation: Simple prompt.
    """
    def __init__(self):
        self.name = "SupportAgent-v1"
        self.retriever = Retriever()
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def query(self, question: str) -> Dict:
        try:
            # 1. Retrieval: Keyword Search - top-2
            search_results = self.retriever.search(question, top_k=2)
            contexts = search_results.get("contexts", [])
            retrieved_ids = search_results.get("retrieved_ids", [])
            sources = search_results.get("sources", [])

            context_str = "\n\n".join(contexts) if contexts else "Không có ngữ cảnh."

            # 2. Generation: Simple Prompt
            system_prompt = f"Dựa vào thông tin này: {context_str}. Hãy trả lời câu hỏi: {question}"

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": system_prompt}
                ]
            )

            return {
                "answer": response.choices[0].message.content,
                "contexts": contexts,
                "retrieved_ids": retrieved_ids,
                "metadata": {
                    "model": "gpt-4o-mini",
                    "tokens_used": response.usage.total_tokens,
                    "sources": list(set(sources)),
                }
            }
        except Exception as e:
            err_msg = str(e)
            print(f"❌ Error in MainAgentV1.query: {err_msg[:300]}{'...' if len(err_msg) > 300 else ''}")
            return {
                "answer": "Lỗi hệ thống trong phiên bản V1.",
                "contexts": [],
                "retrieved_ids": [],
                "metadata": {
                    "error": str(e),
                    "model": "gpt-4o-mini",
                    "tokens_used": 0,
                    "sources": []
                }
            }

if __name__ == "__main__":
    agent = MainAgentV2()
    async def test():
        resp = await agent.query("Làm thế nào để đổi mật khẩu?")
        print(resp)
    asyncio.run(test())
