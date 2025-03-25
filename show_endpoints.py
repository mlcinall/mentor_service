from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import json
from presentations.routers.mentor_router import mentor_router
from presentations.routers.student_router import student_router
from presentations.routers.mentor_time_router import mentor_time_router

# Create a simple FastAPI app with the routers
app = FastAPI(
    title="Микросервис для менторства ITAM",
    description="ИСАД — это не детский сад\n\n"
                "Отдельная благодарность Крюкову Александру Михайловичу (https://github.com/Auxxxxx)\n"
                "Без него этого микросервиса не было бы"
)

# Include all routers
app.include_router(student_router)
app.include_router(mentor_router)
app.include_router(mentor_time_router)

# Generate OpenAPI schema
openapi_schema = get_openapi(
    title=app.title,
    version="1.0.0",
    description=app.description,
    routes=app.routes,
)

# Print all endpoints with their methods and paths
print("API ENDPOINTS:")
print("-" * 80)

# Group endpoints by tag for better organization
endpoints_by_tag = {}

for route in app.routes:
    if hasattr(route, "methods") and hasattr(route, "path"):
        # Skip the /openapi.json and /docs routes
        if route.path in ["/openapi.json", "/docs", "/redoc"]:
            continue
            
        # Extract tags from route if available
        tags = getattr(route, "tags", ["Untagged"])
        if isinstance(tags, list) and tags:
            tag = tags[0]
        else:
            tag = "Untagged"
            
        if tag not in endpoints_by_tag:
            endpoints_by_tag[tag] = []
            
        for method in route.methods:
            endpoint_info = {
                "method": method,
                "path": route.path,
                "name": getattr(route, "name", "unnamed")
            }
            endpoints_by_tag[tag].append(endpoint_info)

# Print endpoints organized by tag
for tag, endpoints in endpoints_by_tag.items():
    print(f"\n🔹 {tag}")
    for endpoint in endpoints:
        print(f"  {endpoint['method']:<7} {endpoint['path']}")
        
print("\n" + "-" * 80)
print(f"Total: {sum(len(endpoints) for endpoints in endpoints_by_tag.values())} endpoints")
print("-" * 80)

print("\nTo access the full API documentation, you would normally visit:")
print("  http://localhost:8000/docs")
print("  http://localhost:8000/redoc") 