from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from pydantic import BaseModel
from typing import List, Type, Dict, Any

from ..core.config import OPENAI_API_KEY

class LLMService:
    """
    Class to encapsulate interactions with LLMs.
    """
    
    async def invoke_text(
        self,
        messages: List[BaseMessage],
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.5
    ) -> str:
        """
        Invokes the LLM to get a plain text response.
        """
        print(f"--- Invoking LLM for text (Model: {model_name}, Temp: {temperature}) ---")
        
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set.")

        print(f"--- Invoking LLM for text (Model: {model_name}) ---")
        
        llm_runner = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=model_name,
            temperature=temperature
        )
        
        response = await llm_runner.ainvoke(messages)
        return response.content


    async def invoke_json(
        self,
        messages: List[BaseMessage],
        output_schema: Type[BaseModel],
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.5
    ) -> dict:
        """
        Invokes the LLM with a structured output schema.
        """
        print(f"--- Invoking LLM for JSON (Model: {model_name}, Schema: {output_schema.__name__}) ---")
        
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set.")

        print(f"--- Invoking LLM for JSON (Model: {model_name}) ---")

        llm_runner = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=model_name,
            temperature=temperature
        )
        
        structured_llm_runner = llm_runner.with_structured_output(
            schema=output_schema
        )
        
        response_pydantic_object = await structured_llm_runner.ainvoke(messages)
        return response_pydantic_object.dict()
    
    
    async def invoke_agent_with_tools(
        self,
        messages: List[BaseMessage],
        tools: list,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.5
    ) -> str:
        """
        Invokes the LLM with integrated tools and a configuration context.
        """
        print(f"--- Invoking Agent (Model: {model_name} ---")

        llm_runner = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=model_name,
            temperature=temperature
        )
        
        llm_with_tools = llm_runner.bind_tools(tools)
        
        response = await llm_with_tools.ainvoke(messages)
        return response

# --- Instancia Única de Servicio (Patrón Singleton) ---
# Se crea una sola instancia que se importará en todos los demás archivos.
llm_service = LLMService()