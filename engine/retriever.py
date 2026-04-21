import os
import json
import re
from typing import List, Dict
from collections import defaultdict, Counter

CHUNK_SIZE = 80  # số lượng từ mỗi chunk, có thể điều chỉnh

class Retriever:
    def __init__(self, docs_folder="data/docs", chunk_file="data/chunks.jsonl"):
        self.docs_folder = docs_folder
        self.chunk_file = chunk_file
        self.chunks = []
        self.id2chunk = {}
        if os.path.exists(chunk_file):
            self._load_chunks()
        else:
            self._ingest_and_chunk()

    def _ingest_and_chunk(self):
        chunk_id = 0
        for fname in os.listdir(self.docs_folder):
            if not fname.endswith(".txt"): continue
            doc_id = os.path.splitext(fname)[0]
            with open(os.path.join(self.docs_folder, fname), "r", encoding="utf-8") as f:
                text = f.read()
            # Tách đoạn theo dấu === hoặc xuống dòng kép, sau đó chunk nhỏ hơn nếu cần
            sections = re.split(r"(===+ .+ ===+|===+ .+ ===+|===+|\n\n+)", text)
            # Gộp lại các đoạn nhỏ thành chunk đủ size
            buffer = ""
            for s in sections:
                s = s.strip()
                if not s: continue
                words = s.split()
                while len(words) > CHUNK_SIZE:
                    chunk_text = " ".join(words[:CHUNK_SIZE])
                    chunk = {
                        "doc_id": doc_id,
                        "chunk_id": f"{doc_id}:chunk_{chunk_id:02d}",
                        "source_file": fname,
                        "text": chunk_text
                    }
                    self.chunks.append(chunk)
                    self.id2chunk[chunk["chunk_id"]] = chunk
                    chunk_id += 1
                    words = words[CHUNK_SIZE:]
                # phần còn lại
                if words:
                    chunk_text = " ".join(words)
                    chunk = {
                        "doc_id": doc_id,
                        "chunk_id": f"{doc_id}:chunk_{chunk_id:02d}",
                        "source_file": fname,
                        "text": chunk_text
                    }
                    self.chunks.append(chunk)
                    self.id2chunk[chunk["chunk_id"]] = chunk
                    chunk_id += 1
        # Lưu ra file
        with open(self.chunk_file, "w", encoding="utf-8") as f:
            for chunk in self.chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    def _load_chunks(self):
        with open(self.chunk_file, "r", encoding="utf-8") as f:
            for line in f:
                chunk = json.loads(line)
                self.chunks.append(chunk)
                self.id2chunk[chunk["chunk_id"]] = chunk

    def search(self, query: str, top_k: int = 3) -> Dict:
        # Đơn giản: keyword overlap
        query_words = set(re.findall(r"\w+", query.lower()))
        scores = []
        for chunk in self.chunks:
            chunk_words = set(re.findall(r"\w+", chunk["text"].lower()))
            overlap = len(query_words & chunk_words)
            if overlap > 0:
                scores.append((overlap, chunk["chunk_id"]))
        scores.sort(reverse=True)
        top_chunks = [cid for _, cid in scores[:top_k]]
        result = {
            "retrieved_ids": top_chunks,
            "contexts": [self.id2chunk[cid]["text"] for cid in top_chunks],
            "sources": [self.id2chunk[cid]["source_file"] for cid in top_chunks]
        }
        return result

if __name__ == "__main__":
    retriever = Retriever()
    q = input("Nhập query: ")
    print(json.dumps(retriever.search(q), ensure_ascii=False, indent=2))
