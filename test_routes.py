from app import app

print("\n=== Available Routes ===")
for rule in app.url_map.iter_rules():
    methods = ', '.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
    print(f"{rule.endpoint:30} {rule.rule:40} [{methods}]")
