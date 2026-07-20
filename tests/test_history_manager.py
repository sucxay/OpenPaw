import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from history.history_manager import HistoryManager


def test_new_session_has_expected_shape(tmp_path):
    mgr = HistoryManager(history_dir=tmp_path)
    session = mgr.new_session(model="test-model")
    assert session.model == "test-model"
    assert session.messages == []
    assert len(session.session_id) == 12


def test_save_and_load_round_trip(tmp_path):
    mgr = HistoryManager(history_dir=tmp_path)
    session = mgr.new_session(model="test-model")
    session.messages.append({"role": "user", "content": "hi"})
    mgr.save(session)

    loaded = mgr.load(session.session_id)
    assert loaded is not None
    assert loaded.messages == [{"role": "user", "content": "hi"}]


def test_load_missing_session_returns_none(tmp_path):
    mgr = HistoryManager(history_dir=tmp_path)
    assert mgr.load("does-not-exist") is None


def test_list_sessions_sorted_by_recency(tmp_path):
    mgr = HistoryManager(history_dir=tmp_path)
    s1 = mgr.new_session(model="m1")
    mgr.save(s1)
    s2 = mgr.new_session(model="m2")
    mgr.save(s2)

    sessions = mgr.list_sessions()
    assert [s.session_id for s in sessions][0] == s2.session_id


def test_clear_all_removes_every_session(tmp_path):
    mgr = HistoryManager(history_dir=tmp_path)
    for _ in range(3):
        mgr.save(mgr.new_session(model="m"))

    count = mgr.clear_all()
    assert count == 3
    assert mgr.list_sessions() == []


def test_corrupt_session_file_is_skipped(tmp_path):
    mgr = HistoryManager(history_dir=tmp_path)
    (tmp_path / "bad.json").write_text("not json", encoding="utf-8")
    good = mgr.new_session(model="m")
    mgr.save(good)

    sessions = mgr.list_sessions()
    assert len(sessions) == 1
    assert sessions[0].session_id == good.session_id
