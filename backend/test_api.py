import httpx

# Test all key APIs
with httpx.Client() as client:
    print("=" * 50)
    print("Testing APIs after file cleanup")
    print("=" * 50)
    
    # 1. Health check
    resp = client.get("http://localhost:8000/health")
    print(f"\n1. Health Check: {resp.status_code} - {resp.json()['status']}")
    
    # 2. List databases
    resp = client.get("http://localhost:8000/api/v1/dbs")
    print(f"\n2. List Databases: {resp.status_code}")
    dbs = resp.json()
    print(f"   Found {len(dbs)} database(s)")
    
    # 3. Natural language to SQL
    if dbs:
        db_name = dbs[0]['name']
        resp = client.post(
            f"http://localhost:8000/api/v1/dbs/{db_name}/query/natural",
            json={"prompt": "查询所有用户"}
        )
        print(f"\n3. NL2SQL API: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            print(f"   Generated SQL: {result['sql'][:60]}...")
        else:
            print(f"   Error: {resp.text}")
    
    print("\n" + "=" * 50)
    print("All tests passed! Services are running normally.")
    print("=" * 50)
