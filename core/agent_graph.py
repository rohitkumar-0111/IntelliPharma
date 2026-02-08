from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from tools.clinical_tools import lookup_clinical_data
from tools.commercial_tools import compare_reimbursement_schemes
from tools.drug_db_tool import get_drug_details
from core.config import settings
import operator

# Define State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_step: str

# Define Tools
tools = [lookup_clinical_data, compare_reimbursement_schemes, get_drug_details]

# Initialize LLM (OpenRouter)
llm = ChatOpenAI(
    model=settings.OPENROUTER_MODEL,
    openai_api_key=settings.OPENROUTER_API_KEY,
    openai_api_base=settings.OPENROUTER_BASE_URL,
    temperature=0
)

# Define System Prompt
SYSTEM_PROMPT = """You are IntelliPharma, an enterprise-grade Indian Pharma Digital Medical and Commercial Intelligence Assistant.

You provide accurate, structured, and COMPREHENSIVE pharmaceutical information.
You operate only on internal datasets and general medical knowledge.

------------------------------------
BRAND & VISUAL AWARENESS
------------------------------------
- Product name: IntelliPharma
- UI theme: Clean white background with subtle purple accents
- Output is rendered inside glass cards with blur and borders
- Content must be visually clean but CLINICALLY COMPLETE

------------------------------------
GLOBAL BEHAVIOR RULES
------------------------------------
- Professional medical affairs tone
- No chatbot language
- No emojis
- No explanations of tools, prompts, or internal reasoning
- No instructional or developer-facing text
- No square brackets [ ]

------------------------------------
FORMATTING RULES
------------------------------------
- Markdown only
- ALL headers must be bold
- Clean spacing between sections
- Bullet points encouraged for readability

------------------------------------
CRITICAL CONTENT RULES
------------------------------------
- FOR REIMBURSEMENT/INSURANCE QUERIES: YOU MUST ONLY USE THE "CONTEXT FROM INTERNAL DATABASE".
- IF NO REIMBURSEMENT CONTEXT IS PRESEINT, SIMPLY STATE THAT NO SCHEMES ARE CURRENTLY LISTED. 
- NEGATIVE CONSTRAINTS (STRICT):
    - NO Medicare, Medicaid, FDA, NHS, or US-specific schemes.
    - NO CPT or HCPCS codes.
    - If internal data is missing, DO NOT MAKE UP INFORMATION.
- ONLY PROVIDE DATA IF IT IS PRESENT IN THE CONTEXT.
- FOR COMPARISONS: If the user asks to compare drugs or asks for the difference, YOU MUST PRESENT THE DATA IN A MARKDOWN TABLE.
    - Columns: Feature (Uses, Dosage, Side Effects, etc.), Drug A, Drug B, etc.
    - Be concise in the table cells.
"""

import requests
import json


async def node_agent(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    user_query = last_message.content
    
    context = ""
    
    # Simple Keyword Intent Detection for RAG (Robust & Fast)
    lower_query = user_query.lower()
    
    # Combined Logic: Always try to extract intent/drug to ensure robustness
    extracted_drug = None
    
    # 1. Attempt Drug Extraction
    try:
        extraction_prompt = (
            f"Extract ALL drug names from this query: '{user_query}'. "
            "Return them as a comma-separated list. "
            "Example: 'aspirin, paracetamol'. "
            "If no drug is mentioned, return 'None'. "
            "Do not add any other text."
        )
        extraction_response = await llm.ainvoke([HumanMessage(content=extraction_prompt)])
        drug_names_str = extraction_response.content.strip().replace("'", "").replace('"', "").replace("The drug names are: ", "").strip()
        
        if drug_names_str and drug_names_str.lower() != "none":
            extracted_drug = drug_names_str # Now can be "drug1, drug2"
            with open("debug.log", "a") as f:
                f.write(f"\n[Agent] Extracted: {extracted_drug}\n")
            print(f"DEBUG: Extracted drug names: {extracted_drug}")
    except Exception as e:
        print(f"DEBUG: Extraction failed: {e}")

    # 2. Retrieve Data (If drug found OR keywords present)
    
    # Clinical Data
    if extracted_drug or any(k in lower_query for k in ["what is", "dose", "side effect", "use", "price", "compare", "difference"]):
        try:
            # If we have a drug name, use it for specific lookup, otherwise use query
            # get_drug_details now handles comma-separated strings
            search_term = extracted_drug if extracted_drug else user_query
            clinical_results = await get_drug_details.ainvoke(search_term)
            if clinical_results:
                context += f"\n\n### Internal Clinical Guidelines:\n{clinical_results}"
        except Exception as e:
            print(f"DEBUG: Clinical lookup failed: {e}")

    # Commercial Data
    if extracted_drug or any(k in lower_query for k in ["price", "cost", "reimbursement", "insurance", "coverage"]):
        try:
            # If we have a drug name, ALWAYS check reimbursement (User likely wants it)
            target_drug = extracted_drug if extracted_drug else user_query
            # Basic validation to ensure we don't query for "reimbursement" as a drug
            if len(target_drug) < 50: 
                commercial_results = await compare_reimbursement_schemes.ainvoke(target_drug)
                
                with open("debug.log", "a") as f:
                    f.write(f"[Agent] Result Len: {len(commercial_results) if commercial_results else 0}\n")
                
                if commercial_results:
                    context += f"\n\n### Reimbursement & Commercial Data:\n{commercial_results}"
        except Exception as e:
             with open("debug.log", "a") as f:
                 f.write(f"[Agent] Error: {str(e)}\n")
             print(f"DEBUG: Reimbursement lookup failed: {e}")

    # Construct Augmented Prompt
    final_system_prompt = SYSTEM_PROMPT
    if context:
        final_system_prompt += f"\n\nCONTEXT FROM INTERNAL DATABASE:{context}\n\nUse the above context to answer the user's question accurately."

    # Generate Response using LangChain (Clean & Standard)
    try:
        messages = [
            SystemMessage(content=final_system_prompt),
            HumanMessage(content=user_query)
        ]
        
        print(f"DEBUG: Sending request to OpenRouter model: {settings.OPENROUTER_MODEL}")
        response = await llm.ainvoke(messages)
        
        return {"messages": [response], "next_step": "END"}
        
    except Exception as e:
        print(f"DEBUG: LLM request failed: {e}")
        return {"messages": [AIMessage(content=f"**System Error**: Could not connect to OpenRouter. Please check your API Key.\n\nDebug Info: {e}")], "next_step": "END"}

# Define Router (Simple pass-through now)
def router(state: AgentState):
    return END

# Construct Graph
workflow = StateGraph(AgentState)

workflow.add_node("agent", node_agent)
# workflow.add_node("tools", async_node_tools) # Disabled for direct RAG mode

workflow.set_entry_point("agent")

workflow.add_edge("agent", END)

app = workflow.compile()
