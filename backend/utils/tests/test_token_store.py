from unittest.mock import MagicMock

import pytest

from backend.utils import token_store

TASK_UID = "abc123"


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, bytes] = {}

    def setex(self, key: str, ttl: int, value: str) -> None:
        self.store[key] = value.encode() if isinstance(value, str) else value

    def get(self, key: str) -> bytes | None:
        return self.store.get(key)

    def delete(self, key: str) -> None:
        self.store.pop(key, None)

    def exists(self, key: str) -> int:
        return 1 if key in self.store else 0


@pytest.fixture
def fake_redis(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(token_store, "_redis", fake)
    return fake


def test_generate_cancel_token_returns_non_empty_string(fake_redis):
    token = token_store.generate_cancel_token(TASK_UID)

    assert isinstance(token, str)
    assert len(token) > 0
    assert fake_redis.store[f"cancel_token:{TASK_UID}"] == token.encode()


def test_generate_cancel_token_is_unique_per_call(fake_redis):
    token1 = token_store.generate_cancel_token(TASK_UID)
    token2 = token_store.generate_cancel_token("other-uid")

    assert token1 != token2


def test_verify_and_consume_cancel_token_success(fake_redis):
    token = token_store.generate_cancel_token(TASK_UID)

    assert token_store.verify_and_consume_cancel_token(TASK_UID, token) is True


def test_verify_and_consume_cancel_token_is_one_shot(fake_redis):
    token = token_store.generate_cancel_token(TASK_UID)

    assert token_store.verify_and_consume_cancel_token(TASK_UID, token) is True
    assert token_store.verify_and_consume_cancel_token(TASK_UID, token) is False


def test_verify_and_consume_cancel_token_wrong_value(fake_redis):
    token_store.generate_cancel_token(TASK_UID)

    assert token_store.verify_and_consume_cancel_token(TASK_UID, "bad-token") is False
    assert fake_redis.store.get(f"cancel_token:{TASK_UID}") is not None


def test_verify_and_consume_cancel_token_unknown_uid(fake_redis):
    assert token_store.verify_and_consume_cancel_token("nope", "any-token") is False


def test_mark_task_completed_invalidates_cancel_token(fake_redis):
    token = token_store.generate_cancel_token(TASK_UID)

    token_store.mark_task_completed(TASK_UID)

    assert token_store.verify_and_consume_cancel_token(TASK_UID, token) is False


def test_mark_task_completed_sets_completion_marker(fake_redis):
    token_store.mark_task_completed(TASK_UID)

    assert token_store.is_task_completed(TASK_UID) is True


def test_is_task_completed_false_when_not_marked(fake_redis):
    assert token_store.is_task_completed(TASK_UID) is False


def test_uses_correct_redis_keys(monkeypatch):
    fake = MagicMock()
    fake.get.return_value = None
    fake.exists.return_value = 0
    monkeypatch.setattr(token_store, "_redis", fake)

    token_store.generate_cancel_token(TASK_UID)
    assert fake.setex.call_args.args[0] == f"cancel_token:{TASK_UID}"

    token_store.mark_task_completed(TASK_UID)
    keys_touched = {call.args[0] for call in fake.delete.call_args_list} | {
        call.args[0] for call in fake.setex.call_args_list
    }
    assert f"task_completed:{TASK_UID}" in keys_touched
    assert f"cancel_token:{TASK_UID}" in keys_touched

    token_store.is_task_completed(TASK_UID)
    fake.exists.assert_called_with(f"task_completed:{TASK_UID}")
