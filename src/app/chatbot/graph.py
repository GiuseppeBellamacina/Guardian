from typing import Annotated, Literal
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage, AIMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from typing import List, Optional, Dict, Any
from datetime import date
from neo4j.time import DateTime
from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages
from langchain_core.runnables.config import RunnableConfig

class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    data: Optional[Any]
    is_picture: Optional[bool]

def serialize_neo4l_datetime(datetime: DateTime) -> str:
    return datetime.strftime("%Y-%m-%d")

def serialize_dict(data: Any) -> Any:
    if isinstance(data, list):
        return [serialize_dict(item) for item in data]
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, DateTime):
                data[key] = serialize_neo4l_datetime(value)
            elif isinstance(value, dict):
                data[key] = serialize_dict(value)
        return data
    else:
        return data

def searcher(state: State, config: RunnableConfig) -> List:
    """
    Crea una query Cypher in base alla conversazione e cerca nel database Neo4j.
    """
    try:
        db = config['configurable']['db']
        cypher_query_generator = config['configurable']['cypher']
        messages = '\n'.join(m.content for m in state['messages'])
        query = cypher_query_generator.invoke({"question": messages})
        print("\33[1;34mSearcher query\33[0m:", query)
        if query:
            result = db.query(query)
            if result:
                data = serialize_dict(result)
                old_data = state.get("data", [])
                old_data.extend(data)
                return {**state,
                    "messages": [AIMessage(content=str(result))],
                    "data": old_data
                }
            else:
                return {**state,
                    "messages": [AIMessage(content="NO DATA")],
                }
        else:
            result = "Non sei autorizzato a eseguire questa azione."
            return {**state,
                "messages": [AIMessage(content=result)]
            }
    except Exception as e:
        print(f"Errore nella ricerca: {e}")
        return {}

def chatbot(state: State, config: RunnableConfig) -> dict:
    try:
        messages = state['messages']
        chatbot_chain = config['configurable']['guardian']
        response = chatbot_chain.invoke({"messages": messages})
        return {**state,
            "messages": [response]
        }
    except Exception as e:
        print(f"Errore nel chatbot: {e}")
        return {}

def picture_analysis(state: State, config: RunnableConfig) -> dict:
    """
    Analizza un'immagine e restituisce i dati estratti.
    """
    try:
        image = state['messages'][-1].content
        picture_chain = config['configurable']['picture']
        message = HumanMessage(
            content=[
                {"type": "text", "text": "Analizza l'immagine dell'auto seguente e fornisci i dati estratti in un JSON, fai attenzione a non includere spazi o trattini nel testo della targa. Esempio: ABC123"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                    },
                ],
            )
        response = picture_chain.invoke([message])
        state["messages"][-1].content = "Effettua una ricerca in base ai dati estratti dall'immagine."
        return {**state,
            "messages": [response]
        }
    except Exception as e:
        print(f"Errore nell'analisi dell'immagine: {e}")
        return {}

def picture_or_not(state: State, config: RunnableConfig) -> Literal["picture_analysis", "guardian"]:
    """
    Controlla se l'ultimo messaggio è un'immagine.
    """
    is_picture = state.get("is_picture", False)
    if is_picture:
        return "picture_analysis"
    return "guardian"

@tool
def go_to_searcher(state: State, config: RunnableConfig) -> Literal["search"]:
    """
    Vai al nodo che esegue la ricerca nel database.
    """
    return "search"

@tool
def calculate_risk_coefficients(state: State, config: RunnableConfig, cf: str) -> dict:
    """
    Calcola i coefficienti di rischio di una persona basati sui crimini diretti e indiretti.

    Args:
        db (Neo4jGraph): Connessione al database Neo4j.
        cf (str): Codice fiscale della persona di cui calcolare i coefficienti.

    Returns:
        dict: Un dizionario contenente i punteggi di rischio per ciascuna categoria.
    """
    db = config['configurable']['db']
    query = f"""
    MATCH (p:Person {{cf: '{cf}'}})
    OPTIONAL MATCH (p)-[:HAS_COMMITTED]->(c:Crime)
    OPTIONAL MATCH (p)-[:PARTNER_OF]->(p1:Person)-[:HAS_COMMITTED]->(c1:Crime)
    OPTIONAL MATCH (p)-[:CHILD_OF]->(p2:Person)-[:HAS_COMMITTED]->(c2:Crime)
    OPTIONAL MATCH (p)<-[:CHILD_OF]-(p3:Person)-[:HAS_COMMITTED]->(c3:Crime)
    OPTIONAL MATCH (p)-[:WORK_AT]->(w:Workplace)<-[:WORK_AT]-(p4:Person)-[:HAS_COMMITTED]->(c4:Crime)
    OPTIONAL MATCH (p)-[:CHILD_OF]->(p2:Person)<-[:CHILD_OF]-(sibling:Person)-[:HAS_COMMITTED]->(c5:Crime)
    RETURN 
        COALESCE(SUM(DISTINCT c.severity_score), 0) AS score_reati_diretti, 
        COALESCE(SUM(DISTINCT c1.severity_score), 0) AS score_reati_partner,
        COALESCE(SUM(DISTINCT c2.severity_score), 0) AS score_reati_genitori, 
        COALESCE(SUM(DISTINCT c3.severity_score), 0) AS score_reati_figli,
        COALESCE(SUM(DISTINCT c4.severity_score), 0) AS score_reati_colleghi
        COALESCE(SUM(DISTINCT c5.severity_score), 0) AS score_reati_fratelli
    """
    try:
        result = db.query(query)
    
        if result:
            record = result[0]
            total_score = (
                record["score_reati_diretti"] * 0.45 +
                record["score_reati_partner"] * 0.2 +
                record["score_reati_genitori"] * 0.1 +
                record["score_reati_figli"] * 0.1 +
                record["score_reati_colleghi"] * 0.05 +
                record["score_reati_fratelli"] * 0.1
            )
            return {
                    "score_reati_diretti": record["score_reati_diretti"],
                    "score_reati_partner": record["score_reati_partner"],
                    "score_reati_genitori": record["score_reati_genitori"],
                    "score_reati_figli": record["score_reati_figli"],
                    "score_reati_colleghi": record["score_reati_colleghi"],
                    "score_reati_fratelli": record["score_reati_fratelli"],
                    "score_ponderato": total_score
                }
        else:
            return {
                "score_reati_diretti": 0,
                "score_reati_partner": 0,
                "score_reati_genitori": 0,
                "score_reati_figli": 0,
                "score_reati_colleghi": 0,
                "score_reati_fratelli": 0,
                "score_ponderato": 0
                }
    except Exception as e:
        print(f"Errore nel calcolo del coefficiente di rischio: {e}")
        return {
            "score_reati_diretti": 0,
            "score_reati_partner": 0,
            "score_reati_genitori": 0,
            "score_reati_figli": 0,
            "score_reati_colleghi": 0,
            "score_reati_fratelli": 0,
            "score_ponderato": 0
            }

def date_conversion(DateTime):
    return date(DateTime.year,DateTime.month,DateTime.day)

@tool
def car_analysis(state: State, config: RunnableConfig, plate: str) -> dict:
    """
    Analizza lo stato di una macchina basata sulla sua targa.
    """
    db = config['configurable']['db']
    try:
        car_data = db.query(f"MATCH (c:Car {{plate: '{plate}'}}) RETURN c.is_stolen AS is_stolen, c.last_revision AS last_revision, c.insurance_expiration AS insurance_expiration")
        car_data = car_data[0]
        current_date =  date.today()
        revision_date = date_conversion(car_data["last_revision"])
        insurance_expiration_date = date_conversion(car_data["insurance_expiration"])

        if revision_date.year < current_date.year - 2 and revision_date.month < current_date.month and revision_date.day < current_date.day:
            revision_status = 'expired'
        else: 
            revision_status = 'ok'
        if insurance_expiration_date < current_date:
            insurance_status = 'expired'
        else:
            insurance_status = 'ok'
        
        return {"revision_status": revision_status, "insurance_status": insurance_status, "is_stolen": car_data["is_stolen"]}
    except Exception as e:
        print(f"Errore nell'analisi del veicolo: {e}")
        return {"error": "Non ci sono dati disponibili per questa vettura."}

def chatbot_to_searcher(state: State) -> Literal["search_node", END]:
    messages = state["messages"]
    last_message = messages[-1]
    
    if last_message.tool_calls:
        return "search_node"
    return END

def should_call(state: State) -> Literal["tool_caller", "guardian"]:
    messages = state["messages"]
    data = messages[-1].content
    if data and data != "NO DATA":
        return "tool_caller"
    return "guardian"

def call(state: State, config: RunnableConfig) -> dict:
    messages = state['messages'][-3:]
    caller_chain = config['configurable']['caller']
    response = caller_chain.invoke({"messages": messages})
    return {**state,
            "messages": [response]
        }

def n(state: State, config: RunnableConfig):
    return state

def compile_graph(graph: StateGraph, memory: MemorySaver, search_node, tool_node):
    graph.add_node("router", n)
    graph.add_node("picture_analysis", picture_analysis)
    graph.add_node("guardian", chatbot)
    graph.add_node("search_node", search_node)
    graph.add_node("searcher", searcher)
    graph.add_node("tool_caller", call)
    graph.add_node("tool_node", tool_node)

    graph.add_edge(START, "router")
    graph.add_conditional_edges("router", picture_or_not)
    graph.add_edge("picture_analysis", "guardian")
    graph.add_conditional_edges("guardian", chatbot_to_searcher)
    graph.add_edge("search_node", "searcher")
    graph.add_conditional_edges("searcher", should_call)
    graph.add_edge("tool_caller", "tool_node")
    graph.add_edge("tool_node", "guardian")
    
    app = graph.compile(checkpointer=memory, debug=False)
    return app