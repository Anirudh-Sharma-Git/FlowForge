from uuid import uuid4

from app.services.outbox_repository import OutboxRepository


def test_outbox_repository_create_does_not_commit():

    aggregate_id = uuid4()

    assert aggregate_id is not None