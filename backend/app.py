from fastapi import FastAPI
from pydantic import BaseModel
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# -------- FastAPI App --------
app = FastAPI()

# -------- Request Model --------
class ChatRequest(BaseModel):
    question: str

# -------- Azure AI Setup --------
myEndpoint = "https://foundry112.services.ai.azure.com/api/projects/proj-default"

project_client = AIProjectClient(
    endpoint=myEndpoint,
    credential=DefaultAzureCredential(),
)

myAgent = "agent-test"

# Fetch agent once at startup
agent = project_client.agents.get(agent_name=myAgent)
openai_client = project_client.get_openai_client()


# -------- Helper: Extract Final Text Properly (Handles MCP) --------
def extract_answer(response):
    try:
        if hasattr(response, "output") and response.output:
            for item in response.output:
                # Look for assistant message
                if item.type == "message":
                    for content in item.content:
                        if content.type == "output_text":
                            return content.text
        # Fallback
        if hasattr(response, "output_text"):
            return response.output_text
    except Exception as e:
        print("Error extracting answer:", str(e))

    return ""


# -------- Chat Endpoint --------
@app.post("/chat")
def chat(request: ChatRequest):

    response = openai_client.responses.create(
        input=[{"role": "user", "content": request.question}],
        extra_body={
            "agent": {
                "name": agent.name,
                "type": "agent_reference"
            }
        },
    )

    answer = extract_answer(response)

    return {
        "question": request.question,
        "answer": answer
    }
