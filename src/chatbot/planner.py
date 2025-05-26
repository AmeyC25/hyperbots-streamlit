import logging
from typing import List, Dict, Any
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from config.settings import settings
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryPlanner:
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            temperature=0.3,
            model_name="gpt-3.5-turbo"
        )
    
    def decompose_query(self, query: str) -> Dict[str, Any]:
        """Break down complex query into sub-questions and plan."""
        system_prompt = """
You are a query planning assistant. Your job is to analyze user questions and break them down into actionable steps.

For each query, provide:
1. Query type (simple, complex, multi-part, comparative, etc.)
2. Sub-questions (if the query is complex)
3. Execution plan with steps
4. Required information sources

Return your response in JSON format with the following structure:
{
    "query_type": "simple|complex|multi-part|comparative|analytical",
    "complexity_score": 1-5,
    "sub_questions": ["question1", "question2", ...],
    "execution_plan": [
        {"step": 1, "action": "search", "target": "search terms", "purpose": "why this step"},
        {"step": 2, "action": "analyze", "target": "what to analyze", "purpose": "why this step"}
    ],
    "expected_sources": ["type of documents/sections needed"]
}
"""
        
        user_prompt = f"""
Analyze this query and create an execution plan:

Query: {query}

Please provide a detailed breakdown following the JSON format specified.
"""
        
        try:
            response = self.llm([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Try to parse JSON response
            try:
                plan = json.loads(response.content)
                logger.info(f"Successfully created plan for query: {query}")
                return plan
            except json.JSONDecodeError:
                # If JSON parsing fails, create a basic plan
                logger.warning("Failed to parse JSON plan, creating basic plan")
                return self._create_basic_plan(query)
                
        except Exception as e:
            logger.error(f"Error in query planning: {e}")
            return self._create_basic_plan(query)
    
    def _create_basic_plan(self, query: str) -> Dict[str, Any]:
        """Create a basic execution plan for simple queries."""
        return {
            "query_type": "simple",
            "complexity_score": 1,
            "sub_questions": [query],
            "execution_plan": [
                {
                    "step": 1,
                    "action": "search",
                    "target": query,
                    "purpose": "Find relevant information"
                },
                {
                    "step": 2,
                    "action": "answer",
                    "target": query,
                    "purpose": "Provide answer based on found information"
                }
            ],
            "expected_sources": ["any relevant documents"]
        }
    
    def prioritize_steps(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize execution steps based on dependencies and importance."""
        execution_plan = plan.get("execution_plan", [])
        
        # Simple prioritization - could be enhanced with dependency analysis
        prioritized_steps = sorted(execution_plan, key=lambda x: x.get("step", 0))
        
        # Add priority scores
        for i, step in enumerate(prioritized_steps):
            step["priority"] = len(prioritized_steps) - i
        
        return prioritized_steps