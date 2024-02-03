"""Working with task queue with Celery"""

from celery import Celery

app = Celery(
    "tasks",
    backend="redis://localhost:6379",
    broker="pyamqp://guest:guest@localhost:5672/",
)

# user in this module if the configurations are not much
# app.conf.update(
#     task_serializer='json',
#     accept_content=['json'],
#     result_serializer='json'
# )

# But if in a big project read configuration from another module
# 'celeryconfig.py'
app.config_from_object('celeryconfig')

@app.task
def add(x, y):
    """Creates a task to add up two numbers"""
    return x + y


def main():
    """Main function"""
    result = add.delay(5, 2)
    print("Result ", result)

    result.get()
