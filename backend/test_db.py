import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_project.settings")
django.setup()

from clients.models import Client

try:
    count = Client.objects.count()
    print(f"[✅] Found {count} clients in the database.")
except Exception as e:
    print("[❌] Error accessing the table:", e)