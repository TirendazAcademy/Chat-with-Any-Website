from langchain_community.document_loaders import WebBaseLoader 

loader = WebBaseLoader("https://openai.com/blog/new-embedding-models-and-api-updates")

data = loader.load()

print(data)