import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
# Natrual Language Processing with Graphs
# This code is used to connect to a Neo4j database and set up a LangChain
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
# Initialize the LLM with your OpenAI API key
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                 model="gpt-4.1-mini"
                )



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
properly. Do not run any queries that would add to or delete from the database. 

The database contains Asset Administration Shells (AAS) and Submodels. 
Each Asset Administration Shell can have multiple Submodels associated with it via the "HAS_SUBMODEL" relationship.
Each Submodel can have multiple Submodel Elements associated with it via the "HAS_ELEMENT" relationship.
Each Submodel Element can be of different types such as Property, MultiLanguageProperty, SubmodelElementCollection, Entity, etc.
Each SubmodelElementCollection can have multiple Submodel Elements associated with it via the "HAS_ELEMENT" relationship.
Each Entity can have multiple Sub-Entities associated with it via the "HAS_ELEMENT" relationship.

Make sure to alias all statements that follow as with statement (e.g. WITH aas as AssetAdministrationShell, aas.idShort as idShort).
Consider the word "Parts" as "Entity" in the schema.
The "GeneralInformation" submodel collection inside the "TechnicalData" submodel contains the basic information about the product such as Manufacturer Name, Product Name, YearOfConstruction, and other relevant attributes. Use this information to answer the relevant questions. Also questions regarding sending broken parts for remanufacturing can be answered using the manufacturer information inside the "TechnicalData" submodel or inside "Nameplate" submodel.
Address Information and location details of a manufacturer can be found in the "NamePlate" submodel of each Asset Administration Shell. Look for SubmodelElementCollection of "AddressInformation" within "NamePlate" submodel, and list all the MultiLanguageProperty inside it to find relevant address information.
You can retrieve Part od truck and its sub-parts by traversing from HAS_SUBMODEL to "BillOfMaterial" Submodel, then to its Entities and their sub-Entities.
Then to retrive information regarding each parts of the truck, you can traverse from the "BillOfMaterial" Submodel to each Entity representing a part of the truck, then to the AssetAdministrationShell associated with that Entity via the "HAS_ELEMENT" relationship. Then the idShort of the Entity will give you the name of the part. Considering that each part can have its own AssetAdministrationShell and Submodels, you can look to the Submodels of each part's AssetAdministrationShell to find relevant information about that part.
To retrieve the disassembly information, you can look for the "Modularity" and "Detachable" in "Circularity Sustainability Principles" HAS_ELEMENT SubmodelElementCollection within the "TechnicalData" Submodel of the AssetAdministrationShell representing the Truck as well as in the AssetAdministrationShell of its parts.
Each Asset Administration Shell contains the Circularity Sustainability Principles which are listed as properties inside submodel collection of "CircularitySustainabilityPrinciples" of "TechnicalData" submodel. Use them to answer the relavant questions.
The Carbon Footprint information is listed in "CarbonFootprint" Submodel of each Asset Administration Shell. The value of Carbon Footprint short as "PCF" can be reached via "HAS_ELEMENT" Submodel Collection with idShort of "ProductCarbonFootprint*", where '*' represent the life cycle phase of the product or, then the value of PCF is stored in Property Element of the submodel collection with the idShort of "PCFCO2eq". Inside each AssetAdministrationShell of prodcut parts such information can be found as explained. Use them to answer the relavant questions.
If you need to divide numbers, make sure to filter the denominator to be non-zero.
Provide query for extracting the grouping/aggregation expressions into a preceding WITH clause.
All sub queries in an UNION must have the same return column names.

The user should be able to have information regarding the cost of R-strategies decisions.
R-strategies consider in this context are Refurbish, Remanufacture, Reuse, Repair, Recycle.
The cost of R-strategies can be found in the "CostOfRStrategies" Submodel of each Asset Administration Shell. The cost values of R-strategies can be reached via "HAS_ELEMENT" Submodel Collection with idShort of "Refurbish", "Remanufacture", "Reuse", "Repair", and "Recycle", then the value of cost is stored in a Property Element of the submodel collection with the idShort of "cost". the value of "Cost" is a sum up of the two of the Property Element with the idShort of "TotalServiceCost" and "ShippingCost".
All cost value are in Euro, which is represented by the Euro sign "€" and stored in database as "xs:string" data type.
For the clarification of the user, the definition of each R-strategy can be found in the "description" attribute of each R-strategy Submodel Collection. 
The "IndividualServices" Submodel Collection of each R-strategy Submodel Collection contains the list of all the services that have been perfomred during each R-strategy. The services can be reached via "HAS_ELEMENT" Property Element inside "IndividualServices" Submodel Collection.

Use the following examples as a guide.
# Few-shot Prompting Methodology
# Provide several examples of natural language questions and their corresponding Cypher queries to guide the model in generating accurate queries.
Examples:
# Retrieve all the AssetAdministrationShell nodes with a non-empty idShort.
MATCH (aas:AssetAdministrationShell) WHERE aas.idShort IS NOT NULL AND aas.idShort <> "" RETURN n LIMIT 25;
# List all Submodels associated with a specific AssetAdministrationShell.
MATCH (aas:AssetAdministrationShell)-[:HAS_SUBMODEL]->(s:Submodel)
WHERE aas.idShort = "Truck" 
RETURN aas, s LIMIT 25;
# List all Entities within a BillOfMaterial Submodel of an AssetAdministrationShell.
#MATCH (aas:AssetAdministrationShell)-[:HAS_SUBMODEL]->(s:Submodel)
MATCH (aas:AssetAdministrationShell)-[:HAS_SUBMODEL]->(s:Submodel)
WHERE aas.idShort = "Truck" 
MATCH (s)-[:HAS_ELEMENT]->(e1:Entity)
WHERE s.idShort = "BillOfMaterial" 
MATCH (e1)-[:HAS_ELEMENT]->(e2:Entity)
WITH collect(DISTINCT e2.idShort) AS truckParts
MATCH (aas1:AssetAdministrationShell)
WHERE aas1.idShort IN truckParts
RETURN DISTINCT aas1;

# Get the manufacturer name of the Truck and its parts.
MATCH (aas:AssetAdministrationShell)-[:HAS_SUBMODEL]->(s:Submodel)
WHERE aas.idShort = "Truck" 
MATCH (s)-[:HAS_ELEMENT]->(e1:Entity)
WHERE s.idShort = "BillOfMaterial" 
MATCH (e1)-[:HAS_ELEMENT]->(e2:Entity)
WITH collect(DISTINCT e2.idShort) AS truckParts
MATCH (aas1:AssetAdministrationShell)
WHERE aas1.idShort IN truckParts
MATCH (aas1)-[:HAS_SUBMODEL]->(smTechData:Submodel)-[:HAS_ELEMENT]->(smc:SubmodelElementCollection)-[:HAS_ELEMENT]->(propManufacturer:Property)
WHERE smTechData.idShort = "TechnicalData" AND propManufacturer.idShort="ManufacturerName"
RETURN DISTINCT aas1, propManufacturer.idShort, propManufacturer.value;

To Get the Carbon Footprint value of the Truck and its parts.
# Get the Carbon Footprint value of the Truck and its parts.
MATCH (aas:AssetAdministrationShell)-[:HAS_SUBMODEL]->(s:Submodel)
WHERE aas.idShort = "Truck" 
MATCH (s)-[:HAS_ELEMENT]->(e1:Entity)
WHERE s.idShort = "BillOfMaterial" 
MATCH (e1)-[:HAS_ELEMENT]->(e2:Entity)
WITH collect(DISTINCT e2.idShort) AS truckParts
MATCH (aas1:AssetAdministrationShell)
WHERE aas1.idShort IN truckParts
MATCH (aas1)-[:HAS_SUBMODEL]->(spcf:Submodel)-[:HAS_ELEMENT]->(smc:SubmodelElementCollection)-[:HAS_ELEMENT]->(pcf:Property)
WHERE spcf.idShort = "CarbonFootprint" and pcf.idShort="PCFCO2eq"
RETURN DISTINCT aas1, spcf, pcf;

#Provide the manufacturer name and Address Information.
MATCH (aas:AssetAdministrationShell)-[:HAS_SUBMODEL]->(nameplate:Submodel idShort:'Nameplate')
MATCH (nameplate)-[:HAS_ELEMENT]->(addressInfo:SubmodelElementCollection idShort:'AddressInformation')
OPTIONAL MATCH (addressInfo)-[:HAS_ELEMENT]->(mlp:SubmodelElement)
OPTIONAL MATCH (nameplate)-[:HAS_ELEMENT]->(manufacturer:SubmodelElement idShort:'ManufacturerName')
RETURN
  aas.idShort AS AssetAdministrationShellIdShort,
  manufacturer.value AS ManufacturerName,
  collect(DISTINCT idShort: mlp.idShort, value: mlp.value) AS AddressInformation;

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

#question = "What are the Entities inside of the BillOfMaterials of a Truck and the entities inside those entities?"
#question = "Can the parts of a Truck be disassembled into their sub-parts?"
#question = "What is the Carbon Footprint value of the Truck?"
#question = "What is the Carbon Footprint value of the Truck for each life cycle phase?"
#question = "What are the manufacturer name of the Truck and its parts?"
#question = "List the Circularity Sustainability Principles of the Truck?"
#question = "provide the manufacturer name and Address Information."
#question = "What is the Carbon Footprint value of the Truck and its parts?"
#question = "What is the Carbon Footprint value of the Truck for each life cycle phase?"

question = "What is the cost of each R-strategy and what are the services performed during each R-strategy?"

response = cypher_chain.invoke(question)
print("User Question:", response["query"])
print("Generated Answer from Cypher Results:", response["result"])

