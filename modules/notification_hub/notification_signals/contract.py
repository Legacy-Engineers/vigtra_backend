from django_eventstream import send_event

# send_event(<channel>, <event_type>, <event_data>)
send_event("notification-hub", "message", {"text": "hello world"})
