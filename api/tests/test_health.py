async def test_health_reports_both_databases(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "mysql": "ok", "neo4j": "ok"}
