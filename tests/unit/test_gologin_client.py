from gologin_automation.api.gologin_client import GoLoginClient
from gologin_automation.browser.selenium_wrapper import SeleniumWrapper


def test_gologin_profile_lifecycle():
    client = GoLoginClient()
    profile = client.create_profile("test-profile")
    assert profile["status"] == "stopped"
    pid = profile["id"]

    client.start_profile(pid)
    p2 = client.list_profiles()[0]
    assert p2["status"] == "running"

    # Simulate browser actions
    sw = SeleniumWrapper(p2)
    r = sw.open("https://www.tiktok.com")
    assert r["status"] == "ok"
    assert sw.screenshot().startswith(b"\x89PNG")

    client.stop_profile(pid)
    p3 = client.list_profiles()[0]
    assert p3["status"] == "stopped"
