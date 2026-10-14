from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


class JobTitle(BaseModel):
    """Modello per la posizione lavorativa ricercata."""
    value: str = Field(..., description="Position sought")


class Company(BaseModel):
    """Modello per il nome dell'azienda."""
    value: str = Field(..., description="Company name")


class HardSkills(BaseModel):
    """Modello per le competenze tecniche essenziali."""
    items: List[str] = Field(
        default_factory=list,
        description="List of essential technical skills"
    )


class SoftSkills(BaseModel):
    """Modello per le competenze trasversali (soft skills)."""
    items: List[str] = Field(
        default_factory=list,
        description="List of soft skills"
    )


class MatchPoints(BaseModel):
    """Modello per i punti di contatto tra requisiti aziendali ed esperienze del candidato."""
    items: List[str] = Field(
        default_factory=list,
        description=(
            "Mapping between company requirements and real user experiences from the base profile. "
            "Specifically highlight which projects or experiences the candidate should emphasize."
        )
    )


class JobAnalysisOutput(BaseModel):
    """
    Modello Pydantic principale per l'output strutturato dell'Agente Analizzatore (Job Analyzer Agent).
    Rispecchia esattamente lo schema JSON definito in architecture.md e può essere usato direttamente
    con `.with_structured_output(JobAnalysisOutput)`.
    """
    job_title: str = Field(
        ...,
        description="Position sought"
    )
    company: str = Field(
        ...,
        description="Company name"
    )
    required_hard_skills: List[str] = Field(
        default_factory=list,
        description="List of essential technical skills"
    )
    required_soft_skills: List[str] = Field(
        default_factory=list,
        description="List of soft skills"
    )
    match_points: List[str] = Field(
        default_factory=list,
        description=(
            "Mapping between company requirements and real user experiences from the base profile. "
            "Specifically highlight which projects or experiences the candidate should emphasize."
        )
    )


class AgentState(TypedDict, total=False):
    """
    Stato condiviso del grafo LangGraph che passa tra i nodi:
    Job Analyzer Agent -> CV Optimizer Agent -> Executor / Submitter Agent.
    """
    job_url: str
    user_profile: Dict[str, Any]
    analysis_result: Dict[str, Any]
    cv_pdf_path: str
    submission_status: str
    job_text: Optional[str]