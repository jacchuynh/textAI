"""
Langchain memory integration for AI GM Brain system
"""

from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory, VectorStoreRetrieverMemory
from langchain.memory.chat_message_histories import BaseChatMessageHistory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationChain
from langchain.llms.base import LLM
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from database.services import DatabaseService
from database.models import ConversationMemory

class PostgreSQLChatMessageHistory(BaseChatMessageHistory):
    """Custom chat message history using PostgreSQL backend"""
    
    def __init__(self, session_id: str, conversation_id: str, db_service: DatabaseService):
        self.session_id = session_id
        self.conversation_id = conversation_id
        self.db_service = db_service
        self._messages: List[BaseMessage] = []
        self._load_messages()
    
    def _load_messages(self):
        """Load messages from database"""
        memory_record = self.db_service.get_conversation_memory(
            self.session_id, self.conversation_id
        )
        
        if memory_record and memory_record.memory_data:
            messages_data = memory_record.memory_data.get('messages', [])
            self._messages = [self._dict_to_message(msg) for msg in messages_data]
    
    def _dict_to_message(self, msg_dict: Dict) -> BaseMessage:
        """Convert dict to message object"""
        if msg_dict['type'] == 'human':
            return HumanMessage(content=msg_dict['content'])
        elif msg_dict['type'] == 'ai':
            return AIMessage(content=msg_dict['content'])
        else:
            raise ValueError(f"Unknown message type: {msg_dict['type']}")
    
    def _message_to_dict(self, message: BaseMessage) -> Dict:
        """Convert message object to dict"""
        return {
            'type': 'human' if isinstance(message, HumanMessage) else 'ai',
            'content': message.content,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def add_message(self, message: BaseMessage) -> None:
        """Add message to history"""
        self._messages.append(message)
        self._save_messages()
    
    def clear(self) -> None:
        """Clear message history"""
        self._messages = []
        self._save_messages()
    
    def _save_messages(self):
        """Save messages to database"""
        messages_data = [self._message_to_dict(msg) for msg in self._messages]
        
        memory_record = self.db_service.get_conversation_memory(
            self.session_id, self.conversation_id
        )
        
        memory_data = {
            'messages': messages_data,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if memory_record:
            self.db_service.update_conversation_memory(
                str(memory_record.id), memory_data
            )
        else:
            self.db_service.save_conversation_memory({
                'session_id': self.session_id,
                'conversation_id': self.conversation_id,
                'memory_type': 'chat_history',
                'memory_data': memory_data,
                'context_type': 'dialogue'
            })
    
    @property
    def messages(self) -> List[BaseMessage]:
        """Get all messages"""
        return self._messages

class LangchainMemoryManager:
    """Manages different types of Langchain memory for the AI GM system"""
    
    def __init__(self, db_service: DatabaseService, embeddings_model=None):
        self.db_service = db_service
        self.embeddings_model = embeddings_model or OpenAIEmbeddings()
        self._memory_instances: Dict[str, Any] = {}
    
    def get_conversation_memory(self, 
                              session_id: str, 
                              conversation_id: str,
                              memory_type: str = "buffer") -> Any:
        """Get or create conversation memory"""
        memory_key = f"{session_id}_{conversation_id}_{memory_type}"
        
        if memory_key not in self._memory_instances:
            chat_history = PostgreSQLChatMessageHistory(
                session_id, conversation_id, self.db_service
            )
            
            if memory_type == "buffer":
                memory = ConversationBufferMemory(
                    chat_memory=chat_history,
                    return_messages=True,
                    memory_key="chat_history"
                )
            elif memory_type == "summary":
                memory = ConversationSummaryMemory(
                    chat_memory=chat_history,
                    return_messages=True,
                    memory_key="chat_history"
                )
            elif memory_type == "vector":
                # Create vector store for this conversation
                vectorstore = self._get_or_create_vectorstore(session_id, conversation_id)
                retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
                
                memory = VectorStoreRetrieverMemory(
                    retriever=retriever,
                    memory_key="relevant_context"
                )
            else:
                raise ValueError(f"Unsupported memory type: {memory_type}")
            
            self._memory_instances[memory_key] = memory
        
        return self._memory_instances[memory_key]
    
    def _get_or_create_vectorstore(self, session_id: str, conversation_id: str):
        """Get or create vector store for conversation"""
        # This would typically use a persistent vector store like Chroma or Pinecone
        # For now, using in-memory Chroma
        vectorstore = Chroma(
            collection_name=f"conversation_{conversation_id}",
            embedding_function=self.embeddings_model
        )
        return vectorstore
    
    def save_to_vector_memory(self, 
                            session_id: str, 
                            content: str, 
                            content_type: str,
                            metadata: Dict[str, Any] = None):
        """Save content to vector memory for retrieval"""
        # Generate embedding
        embedding = self.embeddings_model.embed_query(content)
        
        # Save to database
        embedding_data = {
            'session_id': session_id,
            'content_type': content_type,
            'content_id': f"{content_type}_{datetime.utcnow().timestamp()}",
            'content_text': content,
            'embedding': embedding,
            'embedding_model': 'openai',
            'metadata': metadata or {}
        }
        
        self.db_service.save_embedding(embedding_data)
    
    def retrieve_relevant_context(self, 
                                query: str, 
                                session_id: str,
                                content_types: List[str] = None,
                                limit: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant context using vector similarity"""
        # Generate query embedding
        query_embedding = self.embeddings_model.embed_query(query)
        
        # Search for similar embeddings
        results = self.db_service.search_similar_embeddings(
            query_embedding, session_id, content_types, limit
        )
        
        return [
            {
                'content': embedding.content_text,
                'content_type': embedding.content_type,
                'similarity': similarity,
                'metadata': embedding.metadata
            }
            for embedding, similarity in results
        ]
    
    def create_conversation_chain(self, 
                                llm: LLM, 
                                session_id: str,
                                conversation_id: str,
                                memory_type: str = "buffer") -> ConversationChain:
        """Create a conversation chain with persistent memory"""
        memory = self.get_conversation_memory(session_id, conversation_id, memory_type)
        
        chain = ConversationChain(
            llm=llm,
            memory=memory,
            verbose=True
        )
        
        return chain