from monitoring.alerts.alert_manager import AlertManager
from monitoring.alerts.discord_notifier import DiscordNotifier
from monitoring.health.account_health import run_health_checks


def test_alert_flow():
    am = AlertManager()
    dn = DiscordNotifier()
    am.register_notifier(dn.send)

    metrics = run_health_checks(am)
    # We can't assert exact alerts (randomized), but if any alert created, notifier should have last_message
    alerts = am.recent()
    if alerts:
        assert dn.last_message is not None
    else:
        # No alerts is also acceptable; ensure no exception raised
        assert isinstance(metrics, dict)
