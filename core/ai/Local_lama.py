from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
from langchain.schema import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

class ChatbotService:
    def __init__(self, topic="default", user_id="guest", chat_id=None):
        self.topic = topic
        self.user_id = user_id
        self.chat_id = chat_id or "default"
        
        # Initialize Ollama chat model
        try:
            self.llm = ChatOllama(
                model="llama3.2:3b",
                base_url="http://127.0.0.1:11434",
                temperature=0.7,  # Controls randomness (0.0 to 2.0, lower is more deterministic)
                num_predict=2048,  # Maximum number of tokens to generate
                top_p=0.9,  # Nucleus sampling parameter (0.0 to 1.0)
                repeat_penalty=1.1,  # Penalty for repeating tokens
                top_k=40  # Number of highest probability tokens to consider
            )
            self.output_parser = StrOutputParser()
        except Exception as e:
            raise Exception(f"Error initializing Ollama model: {str(e)}. Please ensure Ollama is running and the model is available.")

        # Embeddings using HuggingFace local model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Vector store using Chroma for sports knowledge
        self.vectorstore = Chroma(
            embedding_function=self.embeddings,
            collection_name=f"{self.topic}_knowledge",
            persist_directory=f"./chroma_db/{self.topic}"
        )
        self.chat_history_file = f"chat_history_{self.user_id}_{self.chat_id}.json"
        self.prompt_template = """You are a helpful AI assistant. Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}

Question: {question}
Helpful Answer:"""
        
        self.QA_PROMPT = ChatPromptTemplate.from_template(self.prompt_template)
        
    def get_chat_filename(self):
        return f"chat_history_{self.user_id}_{self.topic}.json"

    def get_response(self, question: str, chat_history: List[Dict[str, str]]) -> Dict[str, Any]:
        # Get context from vector store
        docs = self.vectorstore.similarity_search(question, k=3)
        context = "\n".join([doc.page_content for doc in docs])
        
        # Format the prompt
        prompt = self.QA_PROMPT.format_messages(
            context=context,
            question=question
        )
        
        # Get response from Ollama
        try:
            # Format the prompt with context and question
            formatted_prompt = self.QA_PROMPT.format_messages(
                context=context,
                question=question
            )
            print("=== Prompt sent to Ollama ===")
            print(formatted_prompt[0].content)
            # Get the response from the model
            response = self.llm.invoke(formatted_prompt[0].content)
            
            return {
                "answer": response.content,
                "source_documents": docs
            }
        except Exception as e:
            raise Exception(f"Error getting response from Ollama: {str(e)}")

    def add_knowledge(self, text: str, metadata: Dict[str, Any] = None) -> None:
        if metadata is None:
            metadata = {}
        document = Document(
            page_content=text,
            metadata={
                "created_at": datetime.now().isoformat(),
                **metadata
            }
        )
        self.vectorstore.add_documents([document])
        self.vectorstore.persist()

    def search_knowledge(self, query: str, k: int = 3) -> List[Document]:
        return self.vectorstore.similarity_search(query, k=k)

    def clear_knowledge(self) -> None:
        self.vectorstore.delete_collection()
        self.vectorstore = Chroma(
            embedding_function=self.embeddings,
            collection_name="coaching_knowledge",
            persist_directory="./chroma_db"
        )

    def save_chat_history(self, chat_history: List[Dict[str, str]]) -> None:
        """Save chat history to a JSON file.
        
        Args:
            chat_history: List of message dictionaries
            filename: Name of the file to save the history to
        """
        try:
            filename = self.get_chat_filename()
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(chat_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save chat history: {e}")

    def load_chat_history(self) -> List[Dict[str, str]]:
        """Load chat history from a JSON file.
        
        Args:
            filename: Name of the file to load the history from
            
        Returns:
            List of message dictionaries
        """
        filename = self.get_chat_filename()
        if not os.path.exists(self.chat_history_file):
            return []
            
        try:
            
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load chat history: {e}")
            return []
