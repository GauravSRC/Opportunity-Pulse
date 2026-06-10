"""Service layer: business logic between API routers and the data/agent layers.

Keep routers thin — they validate I/O and delegate here. Services call into the
``ranking``, ``dedup``, ``deadline_parser``, ``email_agent``, and ``ingestion``
packages and persist results via SQLAlchemy.

TODO(phase-1+): add profile_service, search_service, outreach_service, etc.
"""
