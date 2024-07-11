
""" 
    #* Descrição das Funções:

        - researchAgent(query, llm): Realiza uma pesquisa usando ferramentas externas e o modelo de linguagem.
        - loadData(): Carrega dados da web, divide em segmentos e cria um repositório vetorial.
        - getRelevantDocs(query): Recupera documentos relevantes com base em uma consulta.
        - supervisorAgent(query, llm, webContext, relevant_documents): Supervisiona a criação do roteiro de viagem com base nos dados fornecidos.
        - getResponse(query, llm): Obtém a resposta final combinando todos os agentes e ferramentas.
        - lambda_handler(event, context): Manipulador Lambda para receber eventos e retornar a resposta.
"""
import os
import bs4
import json
#from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter



OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

# Cria o cliente OpenAI passando a chave de API
llm = ChatOpenAI(model='gpt-3.5-turbo')

# query= """
#  Vou viajar para Londres em agosto de 2024.
#  Quero que faça para um roteiro de viagem para mim com eventos que irão ocorrer na data da viagem e com o preço de passagem de São Paulo para Londres.
# """

def researchAgent(query, llm):
    """
    Realiza uma pesquisa usando ferramentas externas e o modelo de linguagem.

    Parâmetros:
    query (str): Consulta de pesquisa fornecida pelo usuário.
    llm (ChatOpenAI): Cliente OpenAI configurado com a chave de API.

    Retorna:
    str: Contexto da web obtido a partir da pesquisa.
    """
    # Carrega ferramentas de pesquisa e define o prompt
    tools = load_tools(['ddg-search', 'wikipedia'], llm=llm)
    prompt = hub.pull('hwchase17/react')
    agent = create_react_agent(llm, tools, prompt)
    
    # Executa o agente com as ferramentas e o prompt
    agent_executor = AgentExecutor(agent=agent, tools=tools, prompt=prompt)
    webContext = agent_executor.invoke({'input': query})
    
    return webContext['output']

def loadData():
    """
    Carrega dados da web, divide em segmentos e cria um repositório vetorial.

    Retorna:
    retriever (Retriever): Objeto capaz de recuperar documentos relevantes.
    """
    # Carrega dados da web usando um carregador baseado na web
    loader = WebBaseLoader(
        web_paths=('https://www.dicasdeviagem.com/inglaterra/',),
        bs_kwargs=dict(
            parse_only=bs4.SoupStrainer(
                class_=(
                    'postcontentwrap',
                    'pagetitleloading background-imaged loading-dark',
                )
            )
        ),
    )
    docs = loader.load()
    
    # Divide os documentos em segmentos menores
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)
    
    # Cria um repositório vetorial a partir dos documentos segmentados
    vectorstore = Chroma.from_documents(
        documents=splits, embedding=OpenAIEmbeddings()
    )
    retriever = vectorstore.as_retriever()
    
    return retriever

def getRelevantDocs(query):
    """
    Recupera documentos relevantes com base em uma consulta.

    Parâmetros:
    query (str): Consulta de pesquisa fornecida pelo usuário.

    Retorna:
    list: Lista de documentos relevantes.
    """
    retriever = loadData()
    relevant_documents = retriever.invoke(query)
    return relevant_documents

def supervisorAgent(query, llm, webContext, relevant_documents):
    """
    Supervisiona a criação do roteiro de viagem com base nos dados fornecidos.

    Parâmetros:
    query (str): Consulta de pesquisa fornecida pelo usuário.
    llm (ChatOpenAI): Cliente OpenAI configurado com a chave de API.
    webContext (str): Contexto da web obtido a partir da pesquisa.
    relevant_documents (list): Lista de documentos relevantes.

    Retorna:
    str: Roteiro de viagem completo e detalhado.
    """
    prompt_template = """
    Você é um gerente de uma agência de viagens. Sua resposta final deverá ser um roteiro de viagem completo e detalhado. 
    Utilize o contexto de eventos e preços de passagens, o input do usuário e também os documentos relevantes para elaborar o roteiro.
    Contexto: {webContext}
    Documento relevante: {relevant_documents}
    Usuário: {query}
    Assistente:
    """

    # Cria um template de prompt e define a sequência de execução
    prompt = PromptTemplate(
        input_variables=['webContext', 'relevant_documents', 'query'],
        template=prompt_template,
    )
    sequence = RunnableSequence(prompt | llm)
    
    # Executa a sequência com os dados fornecidos
    response = sequence.invoke(
        {
            'webContext': webContext,
            'relevant_documents': relevant_documents,
            'query': query,
        }
    )
    return response

def getResponse(query, llm):
    """
    Obtém a resposta final combinando todos os agentes e ferramentas.

    Parâmetros:
    query (str): Consulta de pesquisa fornecida pelo usuário.
    llm (ChatOpenAI): Cliente OpenAI configurado com a chave de API.

    Retorna:
    str: Resposta final com o roteiro de viagem.
    """
    webContext = researchAgent(query, llm)
    relevant_documents = getRelevantDocs(query)
    response = supervisorAgent(query, llm, webContext, relevant_documents)
    return response

def lambda_handler(event, context):
    """
    Manipulador Lambda para receber eventos e retornar a resposta.

    Parâmetros:
    event (dict): Evento contendo a consulta do usuário.
    context (dict): Contexto de execução do Lambda.

    Retorna:
    dict: Resposta com o corpo contendo o roteiro de viagem e o status HTTP.
    """
    #query = event.get("question")
    body = json.loads(event.get('body', {}))
    query = body.get('question', 'Parametro question não fornecido')
    response = getResponse(query, llm).content
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps({
            "message": "Tarefa concluída com sucesso",
            "details": response,
        })        
        }
