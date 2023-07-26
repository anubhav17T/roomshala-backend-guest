import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from src.utils.logger.logger import logger
from src.utils.templates.welcome_email_templates import USER_BOOKING_CONFIRMED

SUPPORT_EMAIL = "support@roomshala.com"


def send_welcome_mail(to_email, subject, details):
    message = Mail(
        from_email=SUPPORT_EMAIL,
        to_emails=[to_email,"reservations@roomshala.com",details["hotel_email"]],
        subject=subject,
        html_content=USER_BOOKING_CONFIRMED.format(details["hotel_name"], details["booking_id"],
                                                   details["checkin_date"],
                                                   details["checkout_date"], details["num_rooms"], details["num_guests"],
                                                   details["booking_amount"],details["gst_amount"],details["total_amount"],
                                                   details["hotel_name"],details["hotel_address"],details["hotel_email"],
                                                   details["hotel_phone_number"],details["guest_name"],
                                                   details["guest_phone_number"],
                                                   details["guest_email_id"]
                                                   ))
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        if response.status_code == 200 or 202:
            logger.info("##### EMAIL HAS BEEN SENT TO THE EMAIL {} #########".format(to_email))
            return True
    except Exception as e:
        logger.error("####### UNABLE TO SEND THE EMAIL WITH EXCEPTION {} ###########".format(e))
        return False
