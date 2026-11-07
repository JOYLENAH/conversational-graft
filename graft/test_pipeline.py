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
    r = p.chat(m, "What is the waiting period for inpatient care? My child is 8")
    assert "3 months (90 days)" in r["answer"]
    assert "C14" in r["citations"]
    assert r["scores"]["faithfulness"] == 1.0


def test_follow_up_uses_last_benefit():
    p, m = make()
    p.chat(m, "Tell me about optical cover for my child, she is 6")
    r = p.chat(m, "And what is the waiting period?")
    assert "couldn't find that detail" in r["answer"]
    assert r["citations"] == []
    dental = p.chat(m, "What is the waiting period for dental care?")
    assert "couldn't find that detail" in dental["answer"]
    assert dental["citations"] == []


def test_turn_count_counts_only_user_messages():
    p, m = make()
    p.chat(m, "My son is 9 years old")
    r = p.chat(m, "Is dental covered?")
    assert r["memory_state"]["turn_count"] == 2


def test_evidence_lists_used_and_unused_clauses():
    p, m = make()
    r = p.chat(m, "What is the waiting period for inpatient care? My child is 8")
    used = {e["clause_id"] for e in r["evidence"] if e["used"]}
    assert "C14" in used
    assert all(e["text"] for e in r["evidence"])  # every item carries its clause text
    assert used == set(r["citations"])


def test_unknown_gives_safe_answer():
    p, m = make()
    r = p.chat(m, "Hello")
    assert "check with the insurer" in r["answer"]
    # nothing to verify and nothing remembered: no empty 100% scores
    assert r["scores"]["faithfulness"] is None
    assert r["scores"]["constraint_retention"] is None


def test_faithfulness_flags_invented_numbers():
    assert faithfulness("Waiting period is 60 days", ["A 90-day waiting period applies"]) < 1.0


def test_child_over_25_is_not_eligible():
    # C3 is the entry age for principal members and spouses; it must not decide a child's age.
    p, m = make()
    r = p.chat(m, "My son is 26 and a full-time student")
    assert "not eligible" in r["answer"]
    assert r["citations"] == ["C2"]
    r = p.chat(m, "Can he be covered?")
    assert "not eligible" in r["answer"]
    assert "C3" not in r["citations"]


def test_student_age_answer_states_the_conditions():
    p, m = make()
    r = p.chat(m, "My daughter is 20 and a full-time student")
    assert r["citations"] == ["C2"]
    assert "residing with parents" in r["answer"]
    assert "not aged above 25" in r["answer"]


def test_young_child_uses_the_child_rule():
    p, m = make()
    r = p.chat(m, "My daughter is 12")
    assert r["citations"] == ["C1"]


def test_unrelated_topic_is_not_answered_with_the_age_rule():
    p, m = make()
    p.chat(m, "My daughter is 20 and a full-time student")
    r = p.chat(m, "Is acupuncture covered?")
    assert "couldn't find that detail" in r["answer"]
    assert r["citations"] == []


def test_ivf_question_finds_the_exclusion():
    p, m = make()
    r = p.chat(m, "Is IVF covered?")
    assert "C21" in r["citations"]
    assert "excluded" in r["answer"]


def test_retention_is_not_scored_when_age_does_not_matter():
    p, m = make()
    p.chat(m, "My daughter is 20 and a full-time student")
    r = p.chat(m, "What is the waiting period for maternity?")
    assert r["scores"]["constraint_retention"] is None
    assert r["scores"]["faithfulness"] == 1.0


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
