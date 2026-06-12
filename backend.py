
from langgraph.graph import START,END,StateGraph
from typing import TypedDict,Annotated
from langchain_core.messages import HumanMessage,BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os
from dotenv import load_dotenv 

load_dotenv()

class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]



llm = ChatGoogleGenerativeAI(
    model='gemini-3-flash-preview',
    google_api_key=os.getenv('GEMINI_API_KEY')
)

def chatenode(state:ChatState):
    message=state['messages']
    response=llm.invoke(message)
    return {'messages':[response]}

conn=sqlite3.connect(database='chatbot.db',check_same_thread=False)
checkpointer=SqliteSaver(conn)
graph=StateGraph(ChatState)
graph.add_node('chatenode',chatenode)

graph.add_edge(START,'chatenode')
graph.add_edge('chatenode',END)
workflow=graph.compile(checkpointer=checkpointer)



def retrive_all_theards():
    all_threads=set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)