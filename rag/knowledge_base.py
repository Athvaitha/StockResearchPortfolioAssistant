import json
import os
import re

GLOSSARY_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "financial_glossary.json")

class KnowledgeBase:
    def __init__(self, data_path: str = GLOSSARY_PATH):
        self.documents = []
        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                self.documents = json.load(f)

    def search(self, query: str, top_k: int = 3):
        """
        Simple TF-IDF / term overlap matching for financial glossary and SEBI concepts.
        """
        query_words = set(re.findall(r'\w+', query.lower()))
        results = []

        for doc in self.documents:
            text = f"{doc.get('topic', '')} {doc.get('category', '')} {doc.get('content', '')}".lower()
            doc_words = set(re.findall(r'\w+', text))
            
            overlap = query_words.intersection(doc_words)
            # Give extra weight to topic phrase matches
            topic_lower = doc.get("topic", "").lower()
            bonus = 0.0
            for word in query_words:
                if len(word) > 2 and word in topic_lower:
                    bonus += 2.0

            score = len(overlap) + bonus
            if score > 0:
                results.append((score, doc))

        results.sort(key=lambda x: x[0], reverse=True)
        matched_docs = [item[1] for item in results[:top_k]]

        if not matched_docs and self.documents:
            # Fallback if no exact keyword match
            matched_docs = self.documents[:top_k]

        return matched_docs

    def format_rag_context(self, docs) -> str:
        formatted = []
        for d in docs:
            formatted.append(f"**Topic**: {d['topic']} ({d['category']})\n**Explanation**: {d['content']}\n**Source**: {d['source']}")
        return "\n\n".join(formatted)

# Global singleton
kb_instance = KnowledgeBase()

def get_rag_context(query: str, top_k: int = 3) -> str:
    docs = kb_instance.search(query, top_k=top_k)
    return kb_instance.format_rag_context(docs)
