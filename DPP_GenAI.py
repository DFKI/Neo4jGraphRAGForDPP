import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
# Natrual Language Processing with Graphs
# This code is used to connect to a Neo4j database and set up a LangChain
from langchain_openai import ChatOpenAI
#from langchain.chains import RetrievalQA
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                 model="gpt-4.1-mini"
                )

#messages = [
 #   SystemMessage("You are an AI assistant design to support End of life actors of a product in their decision making process. The actors are Manufacturer, Recyclers, Waste collectors. You will answer questions related to the end of life of a product, such as what can be done with the product at the current stage based on the curerct status of it, how to recycle it, how to dispose of it, and what the environmental impact is."),
  #  HumanMessage("What can I do with a 3D-printed product with plastic material that is not in a good condition? Can I recycle it or should I dispose of it? What is the environmental impact of my decision?"),
#]
#response = llm.invoke(messages)
#print(response.content)

prompt_template = PromptTemplate.from_template(
    "Tell me about possible next lifecycle phases of the {Product} which is in its current lifecycle phase of {Lifecycle_Phase}.",
)
prompt_template.format(Product="3D-printed product with plastic material", Lifecycle_Phase="Produced in a bad condition")

system_message_str = ''' You are an AI assistant design to support End of life actors of a product in their decision making process. The actors are Manufacturer, Recyclers, Waste collectors. You will answer questions related to the end of life of a product, such as what can be done with the product at the current stage based on the curerct status of it, how to recycle it, how to dispose of it, and what the environmental impact is.
Context: {context}'''
system_message_promt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["context"],
        template=system_message_str,
    )
)
#human_message_str = '''What can I do with a {Product} with {Material} material that is not in a good condition? Can I recycle it or should I dispose of it? What is the environmental impact of my decision?'''
human_message_str = '''Can you provide details on: {question}'''
human_message_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["question"],
        template=human_message_str,
    )
)
messages = [system_message_promt, human_message_prompt]
chatbot_prompt_template = ChatPromptTemplate(
    messages=messages,
    input_variables=["context", "question"],
)
question = "What can I do with a 3D-printed product with plastic material that is not in a good condition? Can I recycle it or should I dispose of it? What is the environmental impact of my decision?"
context = "The product is a 3D-printed item made of plastic, currently in a bad condition, which limits its usability and recyclability."
#chatbot_prompt_template.format(context=context, question=question)

#response = llm.invoke(
#    chatbot_prompt_template.format(context=context, question=question)
#)
#print(response.content)

#Working With Message Types
# This code is used to create a chat prompt template with system and human messages

# Connect to NEO4J
#NEO4J_URI = os.getenv("NEO4J_URI")
#NEO4J_USER = os.getenv("NEO4J_USERNAME")
#NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
#AUTH = (NEO4J_USER, NEO4J_PASSWORD)
#try:
#    with GraphDatabase.driver(NEO4J_URI, auth=None) as driver:
#        driver.verify_connectivity()
#        print("✅ Successfully connected to Neo4j!")
#except Exception as e:
#    print("❌ Connection failed:", e)



#Embeddings
# This code is used to create embeddings for the documents in the Neo4j database    
#neo4j_graph_vector_index = Neo4jVector.from_existing_graph(
#    embedding=OpenAIEmbeddings(),
#    url=os.getenv("NEO4J_URI"),
#    #username=os.getenv("NEO4J_USERNAME"),
#    username=None,
#    password=None,
#    index_name="AssetAdministrationShell",
#    node_label="AssetAdministrationShell",
#    text_node_properties=[
#        "idShort",
#        "id",
#        "sourceUrl",
#        "registrationTime",        
#    ],
#    embedding_node_property="embedding",
#)
#result = neo4j_graph_vector_index.similarity_search("Semitrailer", filter={ "idShort": {"$ne": ""} })
#print("Search Result:", result)
#for doc in result:
 #   print(doc.page_content)
#print(result[0].metadata)


Neo4j_graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    refresh_schema=True,  # # let it call apoc.meta.data()
)

# Run a test query
try:
    result = Neo4j_graph.query("RETURN 1 AS ok")
    if result and result[0].get("ok") == 1:
        print("✅ Neo4j connection successful!")
    else:
        print("⚠️ Connected but unexpected response:", result)
except Exception as e:
    print("❌ Neo4j connection failed:", str(e))


cypher_generation_template = """
Task:
Generate Cypher query for a Neo4j graph database.Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}
Note:
Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything other than
for you to construct a Cypher statement. Do not include any text except
the generated Cypher statement. Make sure the direction of the relationship is
correct in your queries. Make sure you alias both entities and relationships
properly. Do not run any queries that would add to or delete from
the database. Make sure to alias all statements that follow as with
statement (e.g. WITH aas as AssetAdministrationShell, aas.idShort as idShort).
Consider the word "Parts" as "Entity" in the schema.
If you need to divide numbers, make sure to
filter the denominator to be non-zero.
Examples:
# Retrieve all the AssetAdministrationShell nodes with a non-empty idShort.
MATCH (aas:AssetAdministrationShell) WHERE aas.idShort IS NOT NULL AND aas.idShort <> "" RETURN n LIMIT 25;
# List all Submodels associated with a specific AssetAdministrationShell.
MATCH (aas:AssetAdministrationShell)-[:HAS_SUBMODEL]->(s:Submodel)
WHERE aas.idShort = "Truck" 
RETURN aas, s LIMIT 25;
# List all Entities within a BillOfMaterial Submodel of an AssetAdministrationShell.
MATCH (aas:AssetAdministrationShell)-[:HAS_SUBMODEL]->(s:Submodel)
WHERE aas.idShort = "Truck" 
MATCH (s)-[:HAS_ELEMENT]->(e1:Entity)
WHERE s.idShort = "BillOfMaterial" 
MATCH (e1)-[:HAS_ELEMENT]->(e2:Entity)
RETURN aas, s, e1, e2 LIMIT 25;
String category values:
Use existing strings and values from the schema provided. 
The question is:
{question}
"""
#Generate the prompt using prompt template
cypher_generation_prompt = PromptTemplate(
    input_variables=["schema", "question"], template=cypher_generation_template
)

#Generate he question-answer prompt template
qa_generation_template_str = """
You are an assistant that takes the results from a Neo4j Cypher query and forms a human-readable response. 
The query results section contains the results of a Cypher query that was generated based on a user's natural language question. 
The provided information is authoritative; you must never question it or use your internal knowledge to alter it. Make the answer sound like a response to the question.
Query Results:
{context}
Question:
{question}
If the provided information is empty, respond by stating that you don't know the answer. Empty information is indicated by: []
If the information is not empty, you must provide an answer using the results. If the question involves a time duration, assume the query results are in units of days unless specified otherwise.
When idShort are provided in the query results, such as submodel idShort, be cautious of any idShort containing commas or other punctuation. Ensure that any list of idShort is presented clearly to avoid ambiguity and make the full names easily identifiable.
Never state that you lack sufficient information if data is present in the query results. Always utilize the data provided.
Helpful Answer:
"""
qa_generation_prompt = PromptTemplate(
    input_variables=["context", "question"], template=qa_generation_template_str
)

#Generating the Cypher chain

cypher_chain = GraphCypherQAChain.from_llm(
    top_k=100, # Number of results to return, top_k: Specifies the number of query results to include in the qa_prompt
    graph=Neo4j_graph, # The Neo4jGraph instance to use for the chain
    verbose=True, # Whether to print the Cypher query and results, Determines whether the intermediate steps performed by your chain are displayed.
    validate_cypher=True, # Whether to validate the generated Cypher query, validate_cypher: Specifies whether to validate the generated Cypher query.
    allow_dangerous_requests=True, # Whether to allow potentially dangerous requests, allow_dangerous_requests: Specifies whether to allow potentially dangerous requests.
    qa_prompt=qa_generation_prompt, # The prompt template for generating the question-answering response
    cypher_prompt=cypher_generation_prompt, # The prompt template for generating the Cypher query
    qa_llm=ChatOpenAI(model="gpt-4.1-mini", temperature=0), # The language model to use for generating the question-answering response
    cypher_llm=ChatOpenAI(model="gpt-4.1-mini", temperature=0), # The language model to use for generating the Cypher query
    #cypher_return_type="dataframe", # The format in which to return the Cypher
)

question = "What are the Entities inside of the BillofMetrials of a Truck and the entities inside those entities?"
response = cypher_chain.invoke(question)
print("Cypher Query:", response["query"])
print("Cypher Results:", response["result"])