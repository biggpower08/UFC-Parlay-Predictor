from ufc_predictor.data.sync import get_sync_status, record_sync_run, sync_lock


def test_sync_status_includes_last_run_and_active_lock():
    record_sync_run(
        "ufcstats",
        "succeeded",
        False,
        {"events": 1, "fights": 2, "fighters": 3, "inserted": 6, "updated": 0, "skipped": 0, "failed": 0},
        "test run",
    )

    with sync_lock(lock_name="test_sync_lock", ttl_minutes=5):
        status = get_sync_status("ufcstats")
        assert status["last_sync_run"]["status"] == "succeeded"
        assert status["active_lock"] is not None

    status = get_sync_status("ufcstats")
    assert status["active_lock"] is None or status["active_lock"].get("lock_name") != "test_sync_lock"
