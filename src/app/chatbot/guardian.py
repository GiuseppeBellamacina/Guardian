from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

class Guardian():
    def __init__(self, llm: ChatOpenAI, tools: list):
        self.llm = llm.bind_tools(tools)

    def _get_prompt(self) -> str:
        return ChatPromptTemplate.from_messages(
            [
                ("system", """
                              Tu sei Guardian, l'assistente che assiste le Forze dell'Ordine a ottenere dati rapidamente durante i posti di blocco.\n
                              Devi aiutare l'agente a ottenere informazioni sui veicoli e le persone fermate.\n
                              Rispondi alle domande dell'agente e fornisci i dati necessari.\n
                              Devi sempre rispondere in modo chiaro, preciso e con tono formale.\n
                              Se non hai i dati richiesti, allora cercali nel database.\n
                              Se il database non contiene i dati richiesti, allora informa l'agente che il database non contiene i dati richiesti.\n
                           """),
                MessagesPlaceholder("messages", optional=True)
            ]
        )
    
    def create_guardian(self):
        return (self._get_prompt() | self.llm).with_config(run_name="Guardian")

class PictureAnalyzer():
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
    
    def create_picture_analyzer(self):
        return (self.llm).with_config(run_name="Picture Analysis")