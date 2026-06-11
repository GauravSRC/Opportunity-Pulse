"""Notification graph.

eval_rules -> dedupe_alerts -> schedule -> dispatch -> record. Dispatch retried
x3 -> in-app fallback. See docs/agents.md#7-notification.

TODO(phase-3): implement over agents.state.NotificationState.
"""

from __future__ import annotations


def build_notification_graph():
    """Return a compiled LangGraph for notifications. TODO(phase-3)."""
    raise NotImplementedError("build_notification_graph")
