"""Transparent, explainable candidate scoring (design doc §10). No ML.

score = 50·coverage + 20·proficiency + 15·experience + 10·domain + 5·availability

- coverage:    share of the project's required skills the candidate has at all
- proficiency: mean of min(user_level / required_level, 1) over covered skills
- experience:  overall experience level ordinal / 4
- domain:      1 if they have been on a team of a project sharing a domain, else 0
- availability Full-time 1, Part-time 0.6, Weekends 0.3, Unavailable 0

Each factor is rounded to 0.1 point and the score is the sum of the rounded
factors, so the breakdown shown in the UI always adds up exactly.
The score is indicative, not an objective measure of suitability.
"""
from dataclasses import dataclass

WEIGHTS = {"coverage": 50, "proficiency": 20, "experience": 15, "domain": 10, "availability": 5}
LEVEL = {"Beginner": 1, "Intermediate": 2, "Advanced": 3, "Expert": 4}
AVAILABILITY = {"Full-time": 1.0, "Part-time": 0.6, "Weekends": 0.3, "Unavailable": 0.0}


@dataclass(frozen=True)
class Requirement:
    s_id: int
    s_name: str
    level: int          # required ordinal 1..4


@dataclass
class Candidate:
    experience_level: str
    availability: str
    skills: dict[int, int]          # s_id -> ordinal 1..4
    domain_match: bool = False


def score(c: Candidate, requirements: list[Requirement]) -> dict:
    # A skill required for several roles counts once, at its highest required level.
    req: dict[int, Requirement] = {}
    for r in requirements:
        if r.s_id not in req or r.level > req[r.s_id].level:
            req[r.s_id] = r

    covered = [r for r in req.values() if c.skills.get(r.s_id)]
    coverage = len(covered) / len(req) if req else 0.0
    proficiency = (sum(min(c.skills[r.s_id] / r.level, 1.0) for r in covered) / len(covered)) if covered else 0.0
    factors = {
        "coverage": coverage,
        "proficiency": proficiency,
        "experience": LEVEL.get(c.experience_level, 0) / 4,
        "domain": 1.0 if c.domain_match else 0.0,
        "availability": AVAILABILITY.get(c.availability, 0.0),
    }
    breakdown = {k: round(WEIGHTS[k] * v, 1) for k, v in factors.items()}
    missing = sorted(r.s_name for r in req.values() if c.skills.get(r.s_id, 0) < r.level)
    return {
        "score": round(sum(breakdown.values()), 1),
        "breakdown": breakdown,
        "missing_skills": missing,
        "fully_qualified": not missing and bool(req),
    }
