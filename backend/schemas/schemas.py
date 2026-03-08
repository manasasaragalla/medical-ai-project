from pydantic import BaseModel

class InteractionCreate(BaseModel):
    hcp_name: str
    material_used: str
    samples_given: int
    notes: str