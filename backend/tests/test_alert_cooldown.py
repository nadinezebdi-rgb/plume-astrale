"""Tests services/alert_cooldown — lock Mongo-backed pour alertes Slack."""
import os
import pytest
from datetime import datetime, timedelta, timezone

pytestmark = pytest.mark.asyncio


async def test_fail_open_without_mongo(monkeypatch):
    """Sans Mongo → try_acquire retourne True (préserve l'alerte)."""
    import services.mongo as mongo
    monkeypatch.setattr(mongo, '_DB', None)
    monkeypatch.setattr(mongo, '_CLIENT', None)
    monkeypatch.delenv('MONGO_URL', raising=False)   # empêche get_db() de reconnecter
    from services import alert_cooldown
    r = await alert_cooldown.try_acquire('test_ch', 'test_key')
    assert r is True


async def _setup_mongo():
    """Setup Mongo client in-test (évite 'Event loop is closed' entre tests).
    Retourne (db, teardown_fn)."""
    from dotenv import load_dotenv
    load_dotenv('/app/backend/.env')
    import services.mongo as mongo
    from motor.motor_asyncio import AsyncIOMotorClient
    url = os.environ.get('MONGO_URL')
    if not url:
        pytest.skip('MONGO_URL absent')
    client = AsyncIOMotorClient(url)
    mongo._CLIENT = client
    mongo._DB = client[os.environ.get('DB_NAME', 'plume_astrale')]
    from services import alert_cooldown
    alert_cooldown._INDEX_READY = False

    def teardown():
        client.close()
        mongo._CLIENT = None
        mongo._DB = None
    return mongo._DB, teardown


async def test_first_acquire_true():
    db, teardown = await _setup_mongo()
    try:
        from services import alert_cooldown
        await alert_cooldown.release('test_ch_first', 'k1')
        r = await alert_cooldown.try_acquire('test_ch_first', 'k1', ttl_hours=1)
        assert r is True
        await alert_cooldown.release('test_ch_first', 'k1')
    finally:
        teardown()


async def test_second_acquire_false_within_ttl():
    db, teardown = await _setup_mongo()
    try:
        from services import alert_cooldown
        await alert_cooldown.release('test_ch_second', 'k2')
        r1 = await alert_cooldown.try_acquire('test_ch_second', 'k2', ttl_hours=1)
        r2 = await alert_cooldown.try_acquire('test_ch_second', 'k2', ttl_hours=1)
        assert r1 is True
        assert r2 is False
        await alert_cooldown.release('test_ch_second', 'k2')
    finally:
        teardown()


async def test_expired_lock_can_be_reacquired():
    db, teardown = await _setup_mongo()
    try:
        from services import alert_cooldown
        await alert_cooldown.release('test_ch_expired', 'k3')
        r1 = await alert_cooldown.try_acquire('test_ch_expired', 'k3', ttl_hours=1)
        assert r1 is True
        await db['alert_cooldowns'].update_one(
            {'_id': 'test_ch_expired:k3'},
            {'$set': {'expires_at': datetime.now(timezone.utc) - timedelta(hours=1)}},
        )
        r2 = await alert_cooldown.try_acquire('test_ch_expired', 'k3', ttl_hours=1)
        assert r2 is True
        await alert_cooldown.release('test_ch_expired', 'k3')
    finally:
        teardown()


async def test_different_channels_independent():
    db, teardown = await _setup_mongo()
    try:
        from services import alert_cooldown
        await alert_cooldown.release('ch_a', 'same_key')
        await alert_cooldown.release('ch_b', 'same_key')
        r1 = await alert_cooldown.try_acquire('ch_a', 'same_key', ttl_hours=1)
        r2 = await alert_cooldown.try_acquire('ch_b', 'same_key', ttl_hours=1)
        assert r1 is True
        assert r2 is True
        await alert_cooldown.release('ch_a', 'same_key')
        await alert_cooldown.release('ch_b', 'same_key')
    finally:
        teardown()
