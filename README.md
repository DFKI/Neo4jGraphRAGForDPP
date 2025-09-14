# Neo4jGraphRAGForDPP


## About the Paper
### Title
Enhancing Digital Product Passports for the Circular Economy with Generative AI
### Abstract
The transition from a linear “take--make--dispose” model to a Circular Economy (CE) is central to the European Green Deal. Achieving CE goals requires transparent, reliable access to product information across all life cycle phases, so stakeholders can make informed decisions. The European Union’s Digital Product Passport (DPP) addresses current gaps by standardizing life cycle data exchange. Yet integrating detailed product data into DPPs remains challenging due to heterogeneous, distributed sources, which are often a combination of structured and unstructured formats, making efficient information retrieval difficult. This paper proposes a Generative AI-based approach that enhances an existing Asset Administration Shell (AAS)-based DPP with graph-structured Retrieval-Augmented Generation (GraphRAG) on Neo4j and the Model Context Protocol (MCP). Two interaction paths for end users are implemented: (i) a pipeline that converts natural-language questions to Cypher queries and (ii) an MCP-based variant that leverages schema-aware tools (server \& client) to constrain and validate queries against complex AAS schemas. A use case from a dynamic production demonstration living lab is employed to demonstrate and evaluate the approach. Results provide initial proof that integrating Neo4j GraphRAG with MCP improves transparency and clarity, reduces retrieval time, and supports product-related decision-making during the use phase. The contribution is a scalable AI method that enhances data accessibility for diverse actors and advances CE objectives through more effective DPP utilization.

### Conference
33rd CIRP Conference on Life Cycle Engineering (LCE 2026)
https://cirp-lce2026.jspe.or.jp/


### Architecture and Methodology
The Figures from Paper, with better quality, can be found in the provided folder of **Architecture and Methodology** Folder. 

## Installation
- First install and run the Neo4j AAS plugin locally from here https://github.com/dfkibasys/aas_neo4j_integration.
- Copy the aasx file from Truck into the aas folder of Neo4j AAS plugin \aas_neo4j_integration\aasx
- Install and run Neo4j MCP Server https://pypi.org/project/mcp-neo4j-cypher/
- Install Claude Desktop https://claude.ai/download
- Follow this toturial https://youtu.be/JNqePt5USf0 to configure the Claude with the MCP server and the Neo4j 

## Usage
- Start interacting with DPP 

## Support
In case of question contact the authors. name.surname@dfki.de

## Authors and acknowledgment
Monireh Pourjafarian, Christiane Plociennik, Peter Stein, Nastaran Moarefvand, Martin Ruskowski

This paper is funded by the European Union – NextGenerationEU and BMBF Guideline for Funding Projects to Establish Data Competence Centers in Science within the framework of the DACE project (16DKZ2056E). The findings and opinions stated in this paper reflect the opinion of the authors and not the opinion of the European Union nor the BMBF.

AAS Neo4j Integration Tool is built under the Twin4Trucks https://www.twin4trucks.de/ Project.\\

## License
Open source projects, can be found here: https://github.com/DFKI/Neo4jGraphRAGForDPP
