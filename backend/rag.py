import os
from typing import List, Dict
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq

class RAGSystem:
    def __init__(self, knowledge_dir: str = None):
        # Set GROQ_API_KEY in environment
        os.environ["GROQ_API_KEY"] = "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"

        # Set up paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.knowledge_dir = knowledge_dir or os.path.join(self.base_dir, "data")
        self.chroma_dir = os.path.join(self.base_dir, "backend", "chroma_db")

        # Create directories if they don't exist
        os.makedirs(self.knowledge_dir, exist_ok=True)
        os.makedirs(self.chroma_dir, exist_ok=True)

        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        self.vector_store = None
        self.qa_chain = None
        self.initialize_knowledge_base()

    def initialize_knowledge_base(self):
        """Initialize the knowledge base from text files."""
        documents = []
        
        # Load all text files from the knowledge directory
        if os.path.exists(self.knowledge_dir):
            for filename in os.listdir(self.knowledge_dir):
                if filename.endswith(".txt"):
                    file_path = os.path.join(self.knowledge_dir, filename)
                    loader = TextLoader(file_path)
                    documents.extend(loader.load())
        else:
            raise ValueError(f"Knowledge directory not found: {self.knowledge_dir}")

        if not documents:
            raise ValueError(f"No text files found in {self.knowledge_dir}")

        # Split documents into chunks
        texts = self.text_splitter.split_documents(documents)

        # Create vector store
        self.vector_store = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            persist_directory=self.chroma_dir
        )

        # Create custom prompt template
        prompt_template = """You are an expert on the biodiversity of Islamabad and Margalla Hills National Park.
        Use the following pieces of context to answer the question. If you don't know the answer, just say that 
        you don't know, don't try to make up an answer. Keep the answer concise and relevant to Islamabad's biodiversity.

        Context: {context}

        Question: {question}
        Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        # Initialize Groq LLM with llama-3-8b model
        llm = ChatGroq(
            model_name="llama3-70b-8192",  # Using llama2-70b as it's more stable
            temperature=0.3,
            max_tokens=2048,
            top_p=0.9
        )

        # Initialize QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": PROMPT}
        )

    def ask_question(self, question: str) -> Dict:
        """Ask a question and get an answer with relevant sources."""
        if not self.qa_chain:
            print("Error: QA chain not initialized")  # Debug print
            return {"error": "Knowledge base not initialized"}

        try:
            print(f"Processing question: {question}")  # Debug print
            print("QA chain status:", self.qa_chain)  # Debug print
            
            # Get answer from QA chain using invoke instead of __call__
            result = self.qa_chain.invoke({"query": question})
            print(f"Raw QA chain result: {result}")  # Debug print
            
            if not isinstance(result, dict) or "result" not in result:
                print(f"Unexpected result format: {result}")  # Debug print
                return {"error": f"Unexpected response format from QA chain: {result}"}
            
            # Get relevant documents for context
            docs = self.vector_store.similarity_search(question, k=2)
            sources = [{"text": doc.page_content, "source": doc.metadata.get("source", "unknown")} 
                      for doc in docs]

            return {
                "answer": result["result"],
                "sources": sources
            }
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            error_msg = f"Error in RAG system: {str(e)}\nTrace:\n{error_trace}"
            print(error_msg)  # Debug print
            return {"error": error_msg} 