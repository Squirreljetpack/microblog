import os
from app import celery, create_app

app = create_app(config_name=os.getenv('FLASK_CONFIG'))
app.app_context().push()