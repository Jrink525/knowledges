# Internally generates 3 query variants, retrieves for each, deduplicates
docs = retriever.get_relevant_documents(query)
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={多查询检索}]
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI


retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    llm=ChatOpenAI(temperature=0.7),
    include_original=True,   # 同时为原始查询进行检索
)
