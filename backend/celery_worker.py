"""
Celery Worker Setup
This file creates the Celery application instance that runs background tasks.
It connects Flask with Celery so our tasks can access the database.

Student Project - MAD-II
"""

from celery import Celery
from app import create_app

def make_celery(app):
    """
    Creates and configures a Celery instance that works with Flask
    """
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    
    # Update Celery config with Flask config
    celery.conf.update(app.config)

    # This magic class ensures that Celery tasks run inside a Flask app context
    # This is needed so tasks can access the database (db.session)
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Create the Flask app instance
flask_app = create_app()

# Create the Celery app instance
celery = make_celery(flask_app)

# Import tasks so Celery knows about them
# (We will create this file next)
import tasks
