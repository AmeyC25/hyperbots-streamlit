import logging
from typing import List, Dict, Any, Optional
import re
import json
from langchain.schema import Document
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReActAgent:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            temperature=settings.temperature,
            model_name="gpt-3.5-turbo"
        )
        self.max_iterations = 5
        self.tools = {
            "search_documents": self._search_documents,
            "summarize_content": self._summarize_content,
            "answer_question": self._answer_question
        }
    
    def _search_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents."""
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            documents = []
            for doc, score in results:
                documents.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": float(score)
                })
            return documents
        except Exception as e:
            logger.error(f"Error in search_documents: {e}")
            return []
    
    def _summarize_content(self, content: str) -> str:
        """Summarize given content."""
        try:
            prompt = f"""
            Please provide a concise summary of the following content:
            
            {content}
            
            Summary:
            """
            response = self.llm([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            logger.error(f"Error in summarize_content: {e}")
            return "Error generating summary"
    
    def _answer_question(self, question: str, context: str) -> str:
        """Answer question based on provided context."""
        try:
            prompt = f"""
            Based on the following context, please answer the question accurately and concisely.
            If the answer is not available in the context, say so.
            
            Context: {context}
            
            Question: {question}
            
            Answer:
            """
            response = self.llm([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            logger.error(f"Error in answer_question: {e}")
            return "Error generating answer"
    
    def _parse_action(self, text: str) -> Optional[Dict[str, str]]:
        """Parse action from agent's response."""
        action_pattern = r"Action:\s*(\w+)"
        action_input_pattern = r"Action Input:\s*(.+?)(?=\n|$)"
        
        action_match = re.search(action_pattern, text)
        action_input_match = re.search(action_input_pattern, text, re.DOTALL)
        
        if action_match:
            action = action_match.group(1)
            action_input = action_input_match.group(1).strip() if action_input_match else ""
            return {"action": action, "action_input": action_input}
        
        return None
    
    def _execute_action(self, action: str, action_input: str) -> str:
        """Execute the specified action."""
        if action == "search_documents":
            results = self._search_documents(action_input)
            if results:
                return f"Found {len(results)} relevant documents:\n" + \
                       "\n".join([f"- {doc['content'][:200]}..." for doc in results[:3]])
            else:
                return "No relevant documents found."
        
        elif action == "summarize_content":
            return self._summarize_content(action_input)
        
        elif action == "answer_question":
            # For this action, we need both question and context
            # We'll use recent search results as context
            recent_search = self._search_documents(action_input, k=3)
            context = "\n".join([doc['content'] for doc in recent_search])
            return self._answer_question(action_input, context)
        
        else:
            return f"Unknown action: {action}"
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process query using ReAct methodology."""
        system_prompt = """
You are a helpful AI assistant that answers questions based on document content using the ReAct methodology.

Available tools:
- search_documents: Search for relevant documents (input: search query)
- summarize_content: Summarize given content (input: content to summarize)
- answer_question: Answer a question based on context (input: question)

For each step, follow this format:
Thought: [your reasoning about what to do next]
Action: [the action to take]
Action Input: [the input to the action]
Observation: [the result of the action]

Continue this cycle until you can provide a final answer.
When you have enough information, provide your final answer starting with "Final Answer:"
"""
        
        conversation_history = [SystemMessage(content=system_prompt)]
        conversation_history.append(HumanMessage(content=f"Question: {query}"))
        
        iteration = 0
        
        while iteration < self.max_iterations:
            try:
                # Get agent's response
                response = self.llm(conversation_history)
                agent_response = response.content
                
                logger.info(f"Agent response (iteration {iteration}): {agent_response}")
                
                # Check if agent provided final answer
                if "Final Answer:" in agent_response:
                    final_answer = agent_response.split("Final Answer:")[-1].strip()
                    return {
                        "answer": final_answer,
                        "iterations": iteration + 1,
                        "conversation": conversation_history
                    }
                
                # Parse and execute action
                action_info = self._parse_action(agent_response)
                if action_info:
                    action = action_info["action"]
                    action_input = action_info["action_input"]
                    
                    # Execute action
                    observation = self._execute_action(action, action_input)
                    
                    # Add observation to conversation
                    conversation_history.append(AIMessage(content=agent_response))
                    conversation_history.append(HumanMessage(content=f"Observation: {observation}"))
                else:
                    # If no action found, treat as final answer
                    return {
                        "answer": agent_response,
                        "iterations": iteration + 1,
                        "conversation": conversation_history
                    }
                
                iteration += 1
                
            except Exception as e:
                logger.error(f"Error in ReAct processing: {e}")
                return {
                    "answer": f"Error processing query: {str(e)}",
                    "iterations": iteration,
                    "conversation": conversation_history
                }
        
        return {
            "answer": "Maximum iterations reached. Unable to provide a complete answer.",
            "iterations": iteration,
            "conversation": conversation_history
        }