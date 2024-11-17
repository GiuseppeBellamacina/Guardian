from langchain_core.prompts import (
    PromptTemplate,
    FewShotPromptTemplate
)
from langchain_community.graphs import Neo4jGraph
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, Runnable
from langchain_community.chains.graph_qa.cypher_utils import (
    CypherQueryCorrector,
    Schema,
)
from langchain_community.vectorstores import Neo4jVector
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings

CYPHER_EXAMPLES = [
    {
        "question": "Forniscimi i dati di Mario Rossi",
        "query": "MATCH (p:Person {{name: 'Mario', last_name: 'Rossi'}}) RETURN p",
    },
    {
        "question": "Chi è la moglie di Mario Rossi?",
        "query": "MATCH (p:Person {{name: 'Mario', last_name: 'Rossi'}})-[:PARTNER_OF]->(s:Person) RETURN s",
    },
    {
        "question": "Quanti crimini ha commesso Mario Rossi?",
        "query": "MATCH (p:Person {{name: 'Mario', last_name: 'Rossi'}})-[:HAS_COMMITTED]->(c:Crime) RETURN COUNT(DISTINCT c) AS number_of_crimes",
    },
    {
        "question": "Quanti figli ci sono nella famiglia di Mario Rossi?",
        "query": "MATCH (p:Person {{name: 'Mario', last_name: 'Rossi'}})<-[:CHILD_OF]-(p2:Person) RETURN COUNT(DISTINCT p2) AS number_of_children",
    },
    {
        "question": "Che auto guida Mario Rossi?",
        "query": "MATCH (p:Person {{name: 'Mario', last_name: 'Rossi'}})-[:DRIVES]->(c:Car) RETURN c",
    },
    {
        "question": "Che auto guida la moglie di Mario Rossi?",
        "query": "MATCH (p:Person {{name: 'Mario', last_name: 'Rossi'}})-[:PARTNER_OF]->(s:Person)-[:DRIVES]->(c:Car) RETURN c",
    },
    {
        "question": "Identifica la persona che guida l'auto che ha questa targa: 'AB123CD'",
        "query": "MATCH (p:Person)-[:DRIVES]->(c:Car {{plate: 'AB123CD'}}) RETURN p",
    },
    {
        "question": "Sai dirmi se Mario Rossi lavora con Luigi Verdi?",
        "query": "MATCH (p:Person {{name: 'Mario', last_name: 'Rossi'}})-[:WORK_AT]->(w:Workplace)<-[:WORK_AT]-(p2:Person {{name: 'Luigi', last_name: 'Verdi'}}) RETURN p2",
    },
    {
        "question": "Che auto guida la figlia di Mario Rossi di nome Giovanna?",
        "query": "MATCH (p:Person {{name: 'Mario', last_name: 'Rossi'}})<-[:CHILD_OF]-(p2:Person {{name: 'Giovanna'}})-[:DRIVES]->(c:Car) RETURN c",
    }
]

def create_query_generator(llm: Runnable, db: Neo4jGraph):    
    # Define the prompt template
    example_prompt = PromptTemplate.from_template(
        "User input: {question}\nCypher query: {query}"
    )

    # Define the example selector
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        CYPHER_EXAMPLES,
        OpenAIEmbeddings(),
        Neo4jVector,
        k=3,
        input_keys=["question"],
    )

    # Define the prompt which will be used to generate the Cypher query
    cypher_prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix="""Sei un esperto di Neo4j e Cypher. Data una lista di messaggi, crea una query Cypher sintatticamente corretta da eseguire.\n\nQuesto è lo schema del database\n{schema}.\n\nSotto ci sono alcuni esempi e le loro query corrispondenti. \
                Quando generi la query, non includere alcun preambolo, torna solo la query stessa. Quando usi le relazioni, fai molta attenzione a come inserire i versi delle frecce.""",
        suffix="User input: {question}\nCypher query: ",
        input_variables=["question", "schema"],
    )
    
    # Define the Cypher query corrector
    corrector_schema = [
        Schema(el["start"], el["type"], el["end"])
        for el in db.structured_schema.get("relationships")
    ]
    cypher_validation = CypherQueryCorrector(corrector_schema)

    # Define the Cypher query sanitization
    def sanitize_cypher(cypher: str):
        cypher = cypher.content
        replaced = cypher.strip().replace("```", "")
        
        dangerous_keywords = ["DELETE", "DETACH", "REMOVE", "DROP"]
        for keyword in dangerous_keywords:
            if keyword in replaced:
                return None
        
        return cypher_validation(replaced)

    cypher_query_generator = (
        RunnablePassthrough.assign(schema=lambda _: db.get_schema)
        | cypher_prompt
        | llm
        | RunnableLambda(sanitize_cypher)
    )
    
    return cypher_query_generator