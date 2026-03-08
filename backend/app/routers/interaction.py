from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.interaction import Interaction
from app.schemas.interaction import (
    InteractionCreate, InteractionUpdate,
    InteractionResponse, ChatRequest, ChatResponse
)
from app.agent.graph import run_agent
from typing import List

router = APIRouter()

@router.post("/log", response_model=InteractionResponse)
def log_interaction_form(data: InteractionCreate, db: Session = Depends(get_db)):
    interaction = Interaction(**data.dict())
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction

@router.post("/chat", response_model=ChatResponse)
def chat_with_agent(request: ChatRequest):
    try:
        result = run_agent(request.message, request.conversation_history)
        return ChatResponse(
            message=result["message"],
            extracted_data=result.get("extracted_data")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[InteractionResponse])
def get_all_interactions(db: Session = Depends(get_db)):
    return db.query(Interaction).order_by(Interaction.created_at.desc()).all()

@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = db.query(Interaction).filter(
        Interaction.id == interaction_id
    ).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction

@router.put("/{interaction_id}", response_model=InteractionResponse)
def update_interaction(
    interaction_id: int,
    updates: InteractionUpdate,
    db: Session = Depends(get_db)
):
    interaction = db.query(Interaction).filter(
        Interaction.id == interaction_id
    ).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    for field, value in updates.dict(exclude_none=True).items():
        setattr(interaction, field, value)
    db.commit()
    db.refresh(interaction)
    return interaction

@router.delete("/{interaction_id}")
def delete_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = db.query(Interaction).filter(
        Interaction.id == interaction_id
    ).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    db.delete(interaction)
    db.commit()
    return {"message": f"Interaction {interaction_id} deleted."}