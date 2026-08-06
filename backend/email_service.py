import os
import logging
from flask_mail import Mail, Message

logger = logging.getLogger(__name__)

def init_mail_config(app):
    """
    Initialize Flask-Mail configuration with SMTP credentials from environment variables.
    """
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "admin@zeal.edu.in")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
        "MAIL_DEFAULT_SENDER",
        ("Zeal College Admission System", "admin@zeal.edu.in")
    )
    app.config["MAIL_SUPPRESS_SEND"] = os.getenv("MAIL_SUPPRESS_SEND", "False").lower() == "true" or app.config.get("TESTING", False)
    
    mail = Mail(app)
    return mail

def send_student_confirmation_email(mail, student):
    """
    Send HTML confirmation email to the student upon successful admission submission.
    """
    student_email = student.get("email")
    if not student_email:
        logger.warning("No student email provided; skipping confirmation email.")
        return False, "No student email provided"

    try:
        subject = "Admission Application Received - Zeal College of Engineering"
        msg = Message(subject=subject, recipients=[student_email])

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f1f5f9; margin: 0; padding: 20px; }}
                .email-card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }}
                .email-header {{ background: #1e3a8a; color: #ffffff; padding: 25px 30px; text-align: center; }}
                .email-header h1 {{ margin: 0; font-size: 22px; font-weight: 700; }}
                .email-header p {{ margin: 5px 0 0 0; font-size: 13px; color: #cbd5e1; }}
                .email-body {{ padding: 30px; color: #334155; line-height: 1.6; }}
                .status-badge {{ display: inline-block; background: #fef3c7; color: #92400e; font-weight: 600; padding: 6px 14px; border-radius: 20px; font-size: 13px; margin: 10px 0; }}
                .info-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .info-table td {{ padding: 10px 12px; border-bottom: 1px solid #f1f5f9; font-size: 14px; }}
                .info-table td.label {{ font-weight: 600; color: #1e3a8a; width: 40%; }}
                .email-footer {{ background: #f8fafc; padding: 20px 30px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0; }}
            </style>
        </head>
        <body>
            <div class="email-card">
                <div class="email-header">
                    <h1>🎓 Zeal College of Engineering</h1>
                    <p>Online Admission Management System</p>
                </div>
                <div class="email-body">
                    <h2>Application Confirmation</h2>
                    <p>Dear <strong>{student.get('fullName', 'Student')}</strong>,</p>
                    <p>Thank you for submitting your admission application to Zeal College of Engineering. We have successfully received your application details.</p>
                    
                    <div style="text-align: center;">
                        <span class="status-badge">Application Status: Pending Verification</span>
                    </div>

                    <table class="info-table">
                        <tr>
                            <td class="label">Application ID:</td>
                            <td>#{student.get('id', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td class="label">Full Name:</td>
                            <td>{student.get('fullName', '-')}</td>
                        </tr>
                        <tr>
                            <td class="label">Department:</td>
                            <td>{student.get('department', '-')}</td>
                        </tr>
                        <tr>
                            <td class="label">Admission Type:</td>
                            <td>{student.get('admissionType', '-')}</td>
                        </tr>
                        <tr>
                            <td class="label">Submission Date:</td>
                            <td>{student.get('created_at', '-')}</td>
                        </tr>
                    </table>

                    <p>Our admission team is currently reviewing your application and submitted documents. You will receive further updates regarding your verification status via email.</p>
                    <p>If you have any questions, please contact our admission desk at <a href="mailto:admin@zeal.edu.in" style="color: #2563eb;">admin@zeal.edu.in</a>.</p>
                </div>
                <div class="email-footer">
                    <p>© 2026 Zeal College of Engineering. All rights reserved.</p>
                    <p>This is an automated confirmation email. Please do not reply directly to this message.</p>
                </div>
            </div>
        </body>
        </html>
        """
        msg.html = html_content
        mail.send(msg)
        logger.info(f"Student confirmation email sent to {student_email}")
        return True, "Email sent successfully"
    except Exception as e:
        logger.warning(f"Failed to send student confirmation email: {e}")
        return False, str(e)

def send_admin_notification_email(mail, student):
    """
    Send notification email to administrator when a new admission is submitted.
    """
    admin_email = os.getenv("ADMIN_EMAIL", "admin@zeal.edu.in")
    try:
        subject = f"New Admission Received - #{student.get('id')} ({student.get('fullName')})"
        msg = Message(subject=subject, recipients=[admin_email])

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: sans-serif; background: #f8fafc; padding: 20px; }}
                .card {{ max-width: 550px; background: white; padding: 25px; border-radius: 10px; border: 1px solid #e2e8f0; }}
                h2 {{ color: #1e3a8a; margin-top: 0; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                td {{ padding: 8px 10px; border-bottom: 1px solid #f1f5f9; }}
                .label {{ font-weight: bold; color: #475569; width: 40%; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>🚨 New Student Admission Alert</h2>
                <p>A new admission application has been registered in the system:</p>
                <table>
                    <tr><td class="label">Application ID:</td><td>#{student.get('id')}</td></tr>
                    <tr><td class="label">Student Name:</td><td>{student.get('fullName')}</td></tr>
                    <tr><td class="label">Department:</td><td>{student.get('department')}</td></tr>
                    <tr><td class="label">Email:</td><td>{student.get('email')}</td></tr>
                    <tr><td class="label">Mobile:</td><td>{student.get('mobile')}</td></tr>
                    <tr><td class="label">Admission Type:</td><td>{student.get('admissionType')}</td></tr>
                </table>
                <p style="margin-top: 20px;"><a href="http://localhost:5000/view.html" style="background: #1e3a8a; color: white; text-decoration: none; padding: 10px 18px; border-radius: 6px; display: inline-block;">View in Admin Portal</a></p>
            </div>
        </body>
        </html>
        """
        msg.html = html_content
        mail.send(msg)
        logger.info(f"Admin notification email sent for student #{student.get('id')}")
        return True, "Admin email sent"
    except Exception as e:
        logger.warning(f"Failed to send admin notification email: {e}")
        return False, str(e)
