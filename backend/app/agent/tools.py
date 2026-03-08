from langchain_groq import ChatGroq
from langchain.tools import tool
from sqlalchemy.orm import Session
from app.models.interaction import Interaction
from app.database import SessionLocal
from dotenv import load_dotenv
import os, json

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile"
)

@tool
def log_interaction(interaction_text: str) -> str:
    """Logs a new HCP interaction from natural language. Uses LLM to extract
    structured data: HCP name, type, sentiment, topics, outcomes, follow-ups."""
    extraction_prompt = f"""
    Extract structured interaction data from this text and return ONLY valid JSON.
    Text: "{interaction_text}"

    Return this exact JSON format:
    {{
        "hcp_name": "doctor name or empty string",
        "interaction_type": "Meeting or Call or Email or Conference",
        "attendees": "names mentioned",
        "topics_discussed": "topics discussed",
        "materials_shared": "any materials or brochures mentioned",
        "samples_distributed": "any samples mentioned",
        "sentiment": "Positive or Neutral or Negative",
        "outcomes": "key outcomes",
        "follow_up_actions": "next steps mentioned",
        "ai_summary": "one sentence summary of the interaction"
    }}
    """
    response = llm.invoke(extraction_prompt)
    raw = response.content.strip()
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    extracted = json.loads(raw)
    db: Session = SessionLocal()
    try:
        new_interaction = Interaction(
            hcp_name=extracted.get("hcp_name", "Unknown"),
            interaction_type=extracted.get("interaction_type", "Meeting"),
            attendees=extracted.get("attendees", ""),
            topics_discussed=extracted.get("topics_discussed", ""),
            materials_shared=extracted.get("materials_shared", ""),
            samples_distributed=extracted.get("samples_distributed", ""),
            sentiment=extracted.get("sentiment", "Neutral"),
            outcomes=extracted.get("outcomes", ""),
            follow_up_actions=extracted.get("follow_up_actions", ""),
            ai_summary=extracted.get("ai_summary", ""),
            source="chat"
        )
        db.add(new_interaction)
        db.commit()
        db.refresh(new_interaction)
        return json.dumps({
            "status": "success",
            "id": new_interaction.id,
            "message": f"Interaction with {new_interaction.hcp_name} logged successfully.",
            "extracted_data": extracted
        })
    finally:
        db.close()

@tool
def edit_interaction(interaction_id: int, updates_text: str) -> str:
    """Edits an existing HCP interaction by ID using natural language updates."""
    db: Session = SessionLocal()
    try:
        interaction = db.query(Interaction).filter(
            Interaction.id == interaction_id
        ).first()
        if not interaction:
            return json.dumps({"status": "error", "message": f"Interaction ID {interaction_id} not found."})

        update_prompt = f"""
        Current interaction data:
        - HCP: {interaction.hcp_name}
        - Type: {interaction.interaction_type}
        - Topics: {interaction.topics_discussed}
        - Sentiment: {interaction.sentiment}
        - Outcomes: {interaction.outcomes}
        - Follow-up: {interaction.follow_up_actions}

        User wants to update: "{updates_text}"

        Return ONLY valid JSON with fields to update (use null for unchanged):
        {{
            "hcp_name": null,
            "interaction_type": null,
            "topics_discussed": null,
            "sentiment": null,
            "outcomes": null,
            "follow_up_actions": null
        }}
        """
        response = llm.invoke(update_prompt)
        raw = response.content.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        updates = json.loads(raw)
        for field, value in updates.items():
            if value and value != "null":
                setattr(interaction, field, value)
        db.commit()
        return json.dumps({
            "status": "success",
            "message": f"Interaction {interaction_id} updated successfully."
        })
    finally:
        db.close()

@tool
def get_interaction_history(hcp_name: str) -> str:
    """Retrieves all past interactions with a specific HCP by name."""
    db: Session = SessionLocal()
    try:
        interactions = db.query(Interaction).filter(
            Interaction.hcp_name.ilike(f"%{hcp_name}%")
        ).order_by(Interaction.created_at.desc()).limit(10).all()

        if not interactions:
            return json.dumps({"status": "not_found", "message": f"No interactions found for {hcp_name}."})

        history = [
            {"id": i.id, "date": str(i.date), "type": i.interaction_type,
             "topics": i.topics_discussed, "sentiment": i.sentiment, "summary": i.ai_summary}
            for i in interactions
        ]
        return json.dumps({"status": "success", "hcp_name": hcp_name,
                           "total": len(history), "history": history})
    finally:
        db.close()

@tool
def suggest_followup_actions(hcp_name: str, last_interaction_summary: str) -> str:
    """Suggests intelligent follow-up actions for a sales rep based on last HCP interaction."""
    prompt = f"""
    You are an expert pharmaceutical sales coach.
    Sales rep just met with {hcp_name}.
    Summary: {last_interaction_summary}

    Suggest 3 specific follow-up tasks. Return ONLY valid JSON:
    {{
        "suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"],
        "priority": "High or Medium or Low",
        "reasoning": "brief reason"
    }}
    """
    response = llm.invoke(prompt)
    raw = response.content.strip()
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    result = json.loads(raw)
    return json.dumps({"status": "success", "hcp_name": hcp_name, **result})

@tool
def analyze_sentiment_trend(hcp_name: str) -> str:
    """Analyzes sentiment trends across all interactions with an HCP."""
    db: Session = SessionLocal()
    try:
        interactions = db.query(Interaction).filter(
            Interaction.hcp_name.ilike(f"%{hcp_name}%")
        ).order_by(Interaction.created_at.asc()).all()

        if not interactions:
            return json.dumps({"status": "not_found", "message": f"No data for {hcp_name}."})

        sentiment_map = {"Positive": 1, "Neutral": 0, "Negative": -1}
        sentiments = [sentiment_map.get(i.sentiment, 0) for i in interactions]
        avg = sum(sentiments) / len(sentiments)
        trend = "Improving 📈" if avg > 0.3 else ("Declining 📉" if avg < -0.3 else "Stable ➡️")

        return json.dumps({
            "status": "success",
            "hcp_name": hcp_name,
            "total_interactions": len(interactions),
            "sentiment_trend": trend,
            "average_score": round(avg, 2)
        })
    finally:
        db.close()

all_tools = [
    log_interaction,
    edit_interaction,
    get_interaction_history,
    suggest_followup_actions,
    analyze_sentiment_trend
]