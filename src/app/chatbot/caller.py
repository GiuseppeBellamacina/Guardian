from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_openai import ChatOpenAI

class Caller():
    def __init__(self, llm: ChatOpenAI, tools: list):
        self.llm = llm.bind_tools(tools, tool_choice='required')

    def _get_prompt(self) -> str:
        return ChatPromptTemplate.from_messages(
            [
                ("system", "Tu sei un caller di tools, se hai ricevuto dei dati su di una persona, calcola il suo coefficiente di rischio. Se hai ricevuto dati su di un veicolo, analizzalo."),
                MessagesPlaceholder("messages", optional=True)
            ]
        )
    
    def create_caller(self):
        return (self._get_prompt() | self.llm).with_config(run_name="Router")