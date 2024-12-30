def taskModel(item):
    return {
        '_id': str(item.get('_id')),
        'name': str(item.get('name')),
        'description': str(item.get('description')),
        'status': str(item.get('status')),
        'time': str(item.get('time')),
        'date': str(item.get('date')),
        'priority': str(item.get('priority'))
    }

def taskModelList(items):
    return [taskModel(item) for item in items]