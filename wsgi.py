import os
import re
from pathlib import Path

# Optional: load .env locally; harmless in production if absent
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Try to auto-detect settings from manage.py if DJANGO_SETTINGS_MODULE not provided
if not os.environ.get("DJANGO_SETTINGS_MODULE"):
    manage_py = Path(__file__).with_name("manage.py")
    if manage_py.exists():
        m = re.search(r"DJANGO_SETTINGS_MODULE',\s*'([^']+)'", manage_py.read_text())
        if m:
            os.environ["DJANGO_SETTINGS_MODULE"] = m.group(1)

if not os.environ.get("DJANGO_SETTINGS_MODULE"):
    raise RuntimeError(
        "DJANGO_SETTINGS_MODULE not set. Set it in your environment "
        "(e.g., 'myproject.settings') or ensure manage.py contains setdefault."
    )

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
