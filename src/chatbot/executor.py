import logging
from typing import List, Dict, Any, Optional
from .react_agent import ReActAgent
from .planner import QueryPlanner
from .vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryExecutor:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.planner = QueryPlanner()
        self.react_agent = ReActAgent(vector_store)
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """Execute a query using planning and ReAct methodology."""
        try:
            # Step 1: Plan the query
            logger.info(f"Planning query: {query}")
            plan = self.planner.decompose_query(query)
            
            # Step 2: Execute based on complexity
            if plan["complexity_score"] <= 2:
                # Simple query - use ReAct directly
                logger.info("Executing simple query with ReAct")
                result = self.react_agent.process_query(query)
                
                return {
                    "query": query,
                    "plan": plan,
                    "execution_type": "simple",
                    "answer": result["answer"],
                    "metadata": {
                        "iterations": result["iterations"],
                        "complexity_score": plan["complexity_score"]
                    }
                }
            else:
                # Complex query - execute step by step
                logger.info("Executing complex query with multi-step approach")
                return self._execute_complex_query(query, plan)
                
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {
                "query": query,
                "answer": f"Error executing query: {str(e)}",
                "error": True
            }
    
    def _execute_complex_query(self, query: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complex queries with multiple steps."""
        sub_answers = []
        all_evidence = []
        
        # Execute each sub-question
        for i, sub_question in enumerate(plan.get("sub_questions", [query])):
            logger.info(f"Executing sub-question {i+1}: {sub_question}")
            
            sub_result = self.react_agent.process_query(sub_question)
            sub_answers.append({
                "question": sub_question,
                "answer": sub_result["answer"],
                "iterations": sub_result["iterations"]
            })
            
            # Collect evidence from searches
            evidence = self._extract_evidence(sub_result)
            all_evidence.extend(evidence)
        
        # Synthesize final answer
        final_answer = self._synthesize_answers(query, sub_answers, all_evidence)
        
        return {
            "query": query,
            "plan": plan,
            "execution_type": "complex",
            "sub_answers": sub_answers,
            "answer": final_answer,
            "evidence": all_evidence,
            "metadata": {
                "sub_questions_count": len(sub_answers),
                "complexity_score": plan["complexity_score"]
            }
        }
    
    def _extract_evidence(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract evidence/sources from ReAct result."""
        evidence = []
        
        # This is a simplified extraction - in a real implementation,
        # you'd parse the conversation history for document references
        conversation = result.get("conversation", [])
        
        for message in conversation:
            content = getattr(message, 'content', '')
            if "Found" in content and "documents" in content:
                evidence.append({
                    "type": "document_search",
                    "content": content,
                    "source": "vector_search"
                })
        
        return evidence
    
    def _synthesize_answers(self, original_query: str, sub_answers: List[Dict], evidence: List[Dict]) -> str:
        """Synthesize final answer from sub-answers and evidence."""
        try:
            synthesis_prompt = f"""
Based on the following sub-questions and their answers, provide a comprehensive answer to the original question.

Original Question: {original_query}

Sub-questions and Answers:
"""
            for i, sub_answer in enumerate(sub_answers, 1):
                synthesis_prompt += f"\n{i}. Q: {sub_answer['question']}\n   A: {sub_answer['answer']}\n"
            
            synthesis_prompt += "\nPlease provide a well-structured, comprehensive answer that integrates the information from all sub-answers:"
            
            from langchain.schema import HumanMessage
            response = self.react_agent.llm([HumanMessage(content=synthesis_prompt)])
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error synthesizing answers: {e}")
            # Fallback: combine sub-answers
            combined = f"Based on the analysis:\n\n"
            for i, sub_answer in enumerate(sub_answers, 1):
                combined += f"{i}. {sub_answer['answer']}\n\n"
            
            return combined