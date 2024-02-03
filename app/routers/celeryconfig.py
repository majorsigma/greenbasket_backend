
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Africa/Lagos'
enable_utc = True

task_routes = {
    'task.add': 'low-priority'
}