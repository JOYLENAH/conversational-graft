from fastapi.testclient import TestClient

from api.main import app
from graft.memory import MemoryTracker
from graft.metrics import faithfulness
from graft.pipeline import GraftPipeline


def make():
    return GraftPipeline.from_policy_file(), MemoryTracker()


def test_memory_extracts_age_and_dependent():
    m = MemoryTracker()
    m.update("My daughter is 9 years old")
    assert m.state.age == 9
    assert m.state.is_dependent is True


def test_age_retained_across_turns():
    p, m = make()
    p.chat(m, "My son is 20 years old and a full-time student")
    r = p.chat(m, "Is dental covered?")
    assert r["memory_state"]["age"] == 20
    assert "20" in r["answer"]  # the remembered age shaped the answer
    assert r["scores"]["constraint_retention"] == 1.0


def test_waiting_period_is_grounded():
    p, m = make()
    r = p.chat(m, "What is the waiting period for dental care? My child is 8")
    assert "90-day" in r["answer"]
    assert "C8" in r["citations"]
    assert r["scores"]["faithfulness"] == 1.0


def test_follow_up_uses_last_benefit():
    p, m = make()
    p.chat(m, "Tell me about optical cover for my child, she is 6")
    r = p.chat(m, "And what is the waiting period?")
    assert "Optical care has a 90-day waiting period" in r["answer"]


def test_turn_count_counts_only_user_messages():
    p, m = make()
    p.chat(m, "My son is 9 years old")
    r = p.chat(m, "Is dental covered?")
    assert r["memory_state"]["turn_count"] == 2


def test_evidence_lists_used_and_unused_clauses():
    p, m = make()
    r = p.chat(m, "What is the waiting period for dental care? My child is 8")
    used = {e["clause_id"] for e in r["evidence"] if e["used"]}
    assert "C8" in used
    assert all(e["text"] for e in r["evidence"])  # every item carries its clause text
    assert used == set(r["citations"])


def test_unknown_gives_safe_answer():
    p, m = make()
    r = p.chat(m, "Hello")
    assert "enough information" in r["answer"]
    # nothing to verify and nothing remembered: no empty 100% scores
    assert r["scores"]["faithfulness"] is None
    assert r["scores"]["constraint_retention"] is None


def test_faithfulness_flags_invented_numbers():
    assert faithfulness("Waiting period is 60 days", ["A 90-day waiting period applies"]) < 1.0


def test_home_page_serves_the_chat_ui():
    c = TestClient(app)
    r = c.get("/")
    assert r.status_code == 200
    assert "Conversational GRAFT" in r.text


def test_api_session_memory():
    c = TestClient(app)
    c.post("/chat", json={"session_id": "t1", "message": "My child is 5 years old"})
    r = c.post("/chat", json={"session_id": "t1", "message": "Is inpatient care covered?"}).json()
    assert r["memory_state"]["age"] == 5
