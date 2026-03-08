from fastapi import APIRouter
from schemas.schemas import InteractionCreate

router = APIRouter()

interactions_db = []

@router.post("/interactions")
def create_interaction(data: InteractionCreate):

    interaction = {
        "hcp_name": data.hcp_name,
        "material_used": data.material_used,
        "samples_given": data.samples_given,
        "notes": data.notes
    }

    interactions_db.append(interaction)

    return {
        "message": "Interaction saved",
        "data": interaction
    }