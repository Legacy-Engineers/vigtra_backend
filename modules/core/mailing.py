from .celery import app as celery_app


@celery_app.task
def send_plain_text_mail_task(to_email, subject, body):
    # Replace with actual email sending logic
    print(f"[Plain] To: {to_email}, Subject: {subject}, Body: {body}")


@celery_app.task
def send_html_mail_task(to_email, subject, body, html_file):
    # Replace with actual email sending logic
    print(f"[Plain] To: {to_email}, Subject: {subject}, Body: {body}")


class MailManagement:
    def send_plain_text_mail(to_email: list[str], subject: str, body: str):
        """Implement the function"""
        pass

    def send_html_mail():
        """Implement the function"""
        pass
