from fastapi import FastAPI
from pydantic import BaseModel
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

app = FastAPI()

# Request model
class ChatRequest(BaseModel):
    question: str

myEndpoint = "https://foundry112.services.ai.azure.com/api/projects/proj-default"

project_client = AIProjectClient(
    endpoint=myEndpoint,
    credential=DefaultAzureCredential(),
)

myAgent = "agent-test"
agent = project_client.agents.get(agent_name=myAgent)

openai_client = project_client.get_openai_client()

@app.post("/chat")
def chat(request: ChatRequest):
    response = openai_client.responses.create(
        input=[{"role": "user", "content": request.question}],
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )

    return {
        "question": request.question,
        "answer": response.output_text
    }
