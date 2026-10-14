import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env immediately before importing local modules
load_dotenv()

from langgraph.graph import END, START, StateGraph
from agents import cv_optimizer_node, human_review_node, job_analyzer_node, submitter_node
from state import AgentState


def build_graph():
    """Costruisce e compila il grafo LangGraph per la pipeline di candidatura."""
    workflow = StateGraph(AgentState)

    # Aggiunta dei nodi
    workflow.add_node("analyzer", job_analyzer_node)
    workflow.add_node("optimizer", cv_optimizer_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("submitter", submitter_node)

    # Routing condizionale dopo la revisione umana:
    # - se l'utente ha annullato (submission_status = CANCELLED_BY_USER) -> END
    # - altrimenti -> submitter
    def route_after_review(state: AgentState) -> str:
        if state.get("submission_status") == "CANCELLED_BY_USER":
            return "__end__"
        return "submitter"

    # Edge lineari: START -> analyzer -> optimizer -> human_review
    workflow.add_edge(START, "analyzer")
    workflow.add_edge("analyzer", "optimizer")
    workflow.add_edge("optimizer", "human_review")

    # Edge condizionale: human_review -> submitter | END
    workflow.add_conditional_edges(
        "human_review",
        route_after_review,
        {"submitter": "submitter", "__end__": END},
    )
    workflow.add_edge("submitter", END)

    return workflow.compile()


def load_or_create_dummy_profile(filepath: str = "profile.json") -> dict:
    """Carica il file profile.json oppure ne crea uno fittizio di test se non esiste."""
    path = Path(filepath)
    if not path.exists():
        dummy_profile = {
            "personal_info": {
                "first_name": "Mario",
                "last_name": "Rossi",
                "email": "mario.rossi@example.com",
                "phone": "+39 333 1234567",
                "linkedin": "https://linkedin.com/in/mariorossi",
                "github": "https://github.com/mariorossi"
            },
            "experiences": [
                {
                    "role": "AI & Data Engineering Intern",
                    "company": "DataLab Srl",
                    "period": "2025 - 2026",
                    "description": "Sviluppo di pipeline dati distribuite in PySpark e modelli ML in Python."
                }
            ],
            "education": [
                {
                    "degree": "M.Sc. in Computer Engineering - AI & Data Analytics",
                    "institution": "Politecnico di Torino",
                    "year": "2026"
                }
            ],
            "skills": ["Python", "PySpark", "Machine Learning", "Docker", "SQL"]
        }
        path.write_text(json.dumps(dummy_profile, indent=2, ensure_ascii=False), encoding="utf-8")
    return json.loads(path.read_text(encoding="utf-8"))


async def main():
    app = build_graph()

    user_profile = load_or_create_dummy_profile("profile.json")
    test_job_url = "https://example.com/jobs/ai-data-engineer-123"

    initial_state: AgentState = {
        "job_url": test_job_url,
        "user_profile": user_profile,
        "analysis_result": {},
        "cv_pdf_path": "",
        "submission_status": "PENDING",
    }

    # Essendo submitter_node una funzione asincrona (async def), usiamo ainvoke
    final_state = await app.ainvoke(initial_state)

    print("=== STATO FINALE DEL GRAFO ===")
    print(json.dumps(final_state, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
