import streamlit as st 
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.document_loaders import WebBaseLoader 
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
from dotenv import load_dotenv 


load_dotenv()

def get_response(user_input):
	return "I don't know!"

def get_vectorstore_from_url(url):
	loader = WebBaseLoader(url)
	document = loader.load()

	text_splitter = RecursiveCharacterTextSplitter()
	document_chunks = text_splitter.split_documents(document)

	vector_store = Chroma.from_documents(document_chunks, OpenAIEmbeddings())

	return vector_store

def get_context_retriever_chain(vector_store):
	llm = ChatOpenAI()

	retriever = vector_store.as_retriever()

	prompt = ChatPromptTemplate.from_messages([
		MessagesPlaceholder(variable_name="chat_history"),
		("user","{input}"),
		("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation"),	
	])

	retriever_chain = create_history_aware_retriever(llm, retriever,prompt)

	return retriever_chain 

st.set_page_config(page_title="Chat with websites", page_icon="🚀")
st.title("Chat with Website")

if "chat_history" not in st.session_state: 
	st.session_state.chat_history = [
		AIMessage(content="Hello, I am a bot. How can I help you?"),
	]

with st.sidebar:
    st.header("Settings")
    website_url = st.text_input("Website URL")

if website_url is None or website_url == "":
	st.info("Please enter a website URL")

else:
	vector_store = get_vectorstore_from_url(website_url)

	retriever_chain = get_context_retriever_chain(vector_store)

	user_query = st.chat_input("Type something here...")

	if user_query is not None and user_query != "":
		response = get_response(user_query)
		st.session_state.chat_history.append(HumanMessage(content=user_query))
		st.session_state.chat_history.append(AIMessage(content=response))    

		retrieved_document = retriever_chain.invoke(
			{"chat_history": st.session_state.chat_history,
			"input": user_query,}
			)
		st.write(retrieved_document)

	for message in st.session_state.chat_history:
		if isinstance(message, AIMessage):
			with st.chat_message("AI"):
				st.write(message.content)
		elif isinstance(message, HumanMessage):
			with st.chat_message("Human"):
				st.write(message.content)
	

