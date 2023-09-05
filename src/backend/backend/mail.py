import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
# install package
# pip3 install

class api:
    def send_email(to_email, from_email, subject, body):
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body)
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY')) # replace this with your actual api key

            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)


message = Mail(
    from_email='from_email@example.com',
    to_emails='to@example.com',
    subject='Sending with Twilio SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
try:
    sg = SendGridAPIClient("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")
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)

if __name__ == "__main__":
    pass