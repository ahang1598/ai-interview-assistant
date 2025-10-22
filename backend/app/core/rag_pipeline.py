from langchain_community.vectorstores import Chroma
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    from langchain_community.embeddings import FakeEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.llms import Tongyi
from langchain.prompts import PromptTemplate
from typing import List, Dict, Any
import os
import warnings


class RAGPipeline:
    """
    RAG (Retrieval-Augmented Generation) 知识库管道
    """

    def __init__(self, tongyi_api_key: str = None):
        """
        初始化RAG管道
        """
        # 初始化语言模型
        api_key = tongyi_api_key or os.getenv("TONGYI_API_KEY")
        if not api_key:
            raise ValueError("需要阿里云API密钥")

        self.llm = Tongyi(
            dashscope_api_key=api_key,
            model_name="qwen-plus"
        )

        # 初始化嵌入模型
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
            except Exception as e:
                warnings.warn(f"无法从HuggingFace加载嵌入模型: {e}. 使用默认嵌入模型.")
                # 使用不依赖网络的默认嵌入模型
                self.embedding_model = FakeEmbeddings(size=1024)
        else:
            warnings.warn("SentenceTransformer不可用，使用FakeEmbeddings作为后备方案.")
            self.embedding_model = FakeEmbeddings(size=1024)

        # 初始化向量数据库
        try:
            self.vectorstore = Chroma(
                persist_directory="./chroma_db",
                embedding_function=self.embedding_model
            )
        except Exception as e:
            warnings.warn(f"无法初始化向量数据库: {e}")
            # 创建一个空的向量存储作为后备
            self.vectorstore = None

        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        # 定义QA提示模板
        self.qa_template = """你是一个专业的技术面试官。基于以下已知信息，回答用户的问题。
        如果已知信息中没有答案，请说明您不知道，不要编造答案。

        已知内容:
        {context}

        问题:
        {question}

        请给出详细且专业的回答:
        """

        self.qa_prompt = PromptTemplate(
            template=self.qa_template,
            input_variables=["context", "question"]
        )

    def add_documents(self, documents: List[str], metadatas: List[Dict] = None) -> None:
        """
        向知识库中添加文档

        Args:
            documents: 文档列表
            metadatas: 元数据列表
        """
        if self.vectorstore is None:
            warnings.warn("向量数据库未初始化，无法添加文档")
            return
            
        # 分割文档
        split_docs = []
        split_metadatas = []

        for i, doc in enumerate(documents):
            splits = self.text_splitter.create_documents([doc])
            split_docs.extend(splits)

            # 为每个分割的文档添加元数据
            if metadatas and i < len(metadatas):
                for _ in splits:
                    split_metadatas.append(metadatas[i])
            else:
                for _ in splits:
                    split_metadatas.append({})

        # 添加到向量数据库
        self.vectorstore.add_documents(split_docs, metadatas=split_metadatas)

    def query(self, question: str) -> str:
        """
        查询知识库并生成回答

        Args:
            question: 用户问题

        Returns:
            生成的回答
        """
        if self.vectorstore is None:
            return "知识库不可用"
            
        # 创建检索QA链
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": self.qa_prompt},
            return_source_documents=True
        )

        # 执行查询
        result = qa_chain({"query": question})
        return result["result"]

    def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        在向量数据库中进行相似性搜索

        Args:
            query: 查询文本
            k: 返回结果数量

        Returns:
            相似文档列表
        """
        if self.vectorstore is None:
            return []
            
        docs = self.vectorstore.similarity_search_with_score(query, k=k)
        results = []
        for doc, score in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            })
        return results

    def delete_collection(self) -> None:
        """
        删除整个向量数据库集合
        """
        if self.vectorstore is None:
            warnings.warn("向量数据库未初始化，无法删除集合")
            return
        self.vectorstore.delete_collection()