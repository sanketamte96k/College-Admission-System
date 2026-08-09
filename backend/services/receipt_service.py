import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from models import db, Student, Payment
from .payment_service import PaymentService

def number_to_words_indian(amount):
    amount = round(float(amount or 0.0), 2)
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
             "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    def convert_below_thousand(n):
        res = []
        if n >= 100:
            res.append(units[n // 100] + " Hundred")
            n %= 100
        if n >= 20:
            res.append(tens[n // 10])
            if n % 10 > 0:
                res.append(units[n % 10])
        elif n > 0:
            res.append(units[n])
        return " ".join(res)

    int_part = int(amount)
    paise_part = int(round((amount - int_part) * 100))

    if int_part == 0:
        words = "Zero Rupees"
    else:
        parts = []
        crores = int_part // 10000000
        int_part %= 10000000
        if crores > 0:
            parts.append(convert_below_thousand(crores) + " Crore")

        lakhs = int_part // 100000
        int_part %= 100000
        if lakhs > 0:
            parts.append(convert_below_thousand(lakhs) + " Lakh")

        thousands = int_part // 1000
        int_part %= 1000
        if thousands > 0:
            parts.append(convert_below_thousand(thousands) + " Thousand")

        if int_part > 0:
            parts.append(convert_below_thousand(int_part))

        words = "Rupees " + " ".join(parts)

    if paise_part > 0:
        words += " and " + convert_below_thousand(paise_part) + " Paise"

    return words + " Only"


class ReceiptService:
    @staticmethod
    def get_or_create_receipt_number(payment):
        if payment.receipt_number:
            return payment.receipt_number

        yr = payment.payment_date.year if payment.payment_date else (payment.created_at.year if payment.created_at else datetime.utcnow().year)
        receipt_no = f"ZCFR-{yr}-{payment.id:06d}"
        try:
            payment.receipt_number = receipt_no
            db.session.commit()
        except Exception:
            db.session.rollback()
        return receipt_no

    @staticmethod
    def calculate_reconciliation_data(payment, student):
        _, total_fee = PaymentService.get_fee_breakdown_for_student(student)

        # Get all successful payments for this student ordered by id
        all_payments = Payment.query.filter_by(student_id=student.id).order_by(Payment.id.asc()).all()
        successful_payments = [p for p in all_payments if getattr(p, "status", "SUCCESS") in ["SUCCESS", "Paid"]]

        previously_paid = sum(float(p.amount) for p in successful_payments if p.id < payment.id)
        current_amount = float(payment.amount)
        cumulative_paid = previously_paid + current_amount
        remaining_balance = max(0.0, round(total_fee - cumulative_paid, 2))

        return {
            "total_fee": round(total_fee, 2),
            "previously_paid": round(previously_paid, 2),
            "current_payment": round(current_amount, 2),
            "cumulative_paid": round(cumulative_paid, 2),
            "remaining_balance": remaining_balance
        }

    @staticmethod
    def generate_fee_receipt_pdf(payment_id):
        payment = Payment.query.get(payment_id)
        if not payment:
            return None, "Payment record not found"

        student = Student.query.get(payment.student_id)
        if not student:
            return None, "Associated student record not found"

        receipt_no = ReceiptService.get_or_create_receipt_number(payment)
        recon = ReceiptService.calculate_reconciliation_data(payment, student)
        amount_words = number_to_words_indian(payment.amount)

        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            leftMargin=15 * mm,
            rightMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm
        )

        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]

        title_style = ParagraphStyle(
            "CollegeHeaderTitle",
            parent=normal_style,
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            alignment=1,
            textColor=colors.HexColor("#1e3a8a")
        )

        sub_style = ParagraphStyle(
            "CollegeHeaderSub",
            parent=normal_style,
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            alignment=1,
            textColor=colors.HexColor("#475569")
        )

        banner_style = ParagraphStyle(
            "BannerStyle",
            parent=normal_style,
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=13,
            alignment=1,
            textColor=colors.white
        )

        table_header_style = ParagraphStyle(
            "TableHeader",
            parent=normal_style,
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=10,
            textColor=colors.HexColor("#1e3a8a")
        )

        cell_style = ParagraphStyle(
            "CellText",
            parent=normal_style,
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#1e293b")
        )

        cell_bold = ParagraphStyle(
            "CellTextBold",
            parent=normal_style,
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#0f172a")
        )

        elements = []

        # 1. College Header
        elements.append(Paragraph("ZEAL COLLEGE OF ENGINEERING AND RESEARCH", title_style))
        elements.append(Paragraph("Approved by AICTE, Affiliated to Savitribai Phule Pune University (SPPU)", sub_style))
        elements.append(Paragraph("Accredited by NAAC with 'A' Grade | NBA Accredited Programs", sub_style))
        elements.append(Paragraph("Survey No. 39, Narhe, Pune - 411041, Maharashtra, India | Helpline: +91 9921518878", sub_style))
        elements.append(Spacer(1, 4 * mm))

        # 2. Receipt Banner
        banner_table = Table(
            [[Paragraph("OFFICIAL STUDENT FEE PAYMENT RECEIPT", banner_style)]],
            colWidths=[180 * mm]
        )
        banner_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1e3a8a")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(banner_table)
        elements.append(Spacer(1, 4 * mm))

        # 3. Receipt Metadata & Student Information
        pay_date_str = payment.payment_date.strftime("%d-%b-%Y %I:%M %p") if payment.payment_date else (payment.created_at.strftime("%d-%b-%Y") if payment.created_at else "-")

        info_data = [
            [
                Paragraph("<b>Receipt Number:</b>", cell_style),
                Paragraph(f"<b><font color=\"#1e3a8a\">{receipt_no}</font></b>", cell_bold),
                Paragraph("<b>Application ID:</b>", cell_style),
                Paragraph(f"<b>#{student.id}</b>", cell_bold)
            ],
            [
                Paragraph("<b>Payment Date:</b>", cell_style),
                Paragraph(pay_date_str, cell_style),
                Paragraph("<b>Academic Year:</b>", cell_style),
                Paragraph(f"{datetime.utcnow().year}-{datetime.utcnow().year + 1}", cell_style)
            ],
            [
                Paragraph("<b>Candidate Name:</b>", cell_style),
                Paragraph(f"<b>{student.fullName}</b>", cell_bold),
                Paragraph("<b>Department:</b>", cell_style),
                Paragraph(student.department or "-", cell_style)
            ],
            [
                Paragraph("<b>Admission Quota:</b>", cell_style),
                Paragraph(student.admissionType or "CAP", cell_style),
                Paragraph("<b>Contact Mobile:</b>", cell_style),
                Paragraph(student.mobile or "-", cell_style)
            ]
        ]

        info_table = Table(info_data, colWidths=[38 * mm, 52 * mm, 38 * mm, 52 * mm])
        info_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 4 * mm))

        # 4. Payment Particulars Table
        method_str = payment.payment_method or payment.payment_mode or "UPI / Online"
        items_data = [
            [
                Paragraph("<b>#</b>", table_header_style),
                Paragraph("<b>Fee Particulars</b>", table_header_style),
                Paragraph("<b>Payment Method</b>", table_header_style),
                Paragraph("<b>Transaction / Ref ID</b>", table_header_style),
                Paragraph("<b>Status</b>", table_header_style),
                Paragraph("<b>Amount (INR)</b>", table_header_style)
            ],
            [
                Paragraph("1", cell_style),
                Paragraph(f"<b>{payment.fee_type or 'Tuition Fee'}</b>", cell_style),
                Paragraph(method_str, cell_style),
                Paragraph(payment.transaction_id or "-", cell_style),
                Paragraph(f"<font color=\"#059669\"><b>{payment.status or 'SUCCESS'}</b></font>", cell_style),
                Paragraph(f"<b>Rs. {float(payment.amount):,.2f}</b>", cell_bold)
            ]
        ]

        items_table = Table(items_data, colWidths=[10 * mm, 45 * mm, 32 * mm, 45 * mm, 20 * mm, 28 * mm])
        items_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ALIGN", (0, 0), (-1, 0), "LEFT"),
            ("ALIGN", (-1, 0), (-1, -1), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 4 * mm))

        # 5. Financial Reconciliation & Amount in Words
        fee_summary_data = [
            [Paragraph("<b>Prescribed Total Fee:</b>", cell_style), Paragraph(f"Rs. {recon['total_fee']:,.2f}", cell_style)],
            [Paragraph("<b>Previously Paid Amount:</b>", cell_style), Paragraph(f"Rs. {recon['previously_paid']:,.2f}", cell_style)],
            [Paragraph("<b>Current Payment Received:</b>", cell_style), Paragraph(f"<b><font color=\"#059669\">Rs. {recon['current_payment']:,.2f}</font></b>", cell_bold)],
            [Paragraph("<b>Total Cumulative Paid:</b>", cell_style), Paragraph(f"<b>Rs. {recon['cumulative_paid']:,.2f}</b>", cell_bold)],
            [Paragraph("<b>Remaining Balance Dues:</b>", cell_style), Paragraph(f"<b><font color=\"#dc2626\">Rs. {recon['remaining_balance']:,.2f}</font></b>", cell_bold)]
        ]

        fee_sum_table = Table(fee_summary_data, colWidths=[90 * mm, 90 * mm])
        fee_sum_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(fee_sum_table)
        elements.append(Spacer(1, 3.5 * mm))

        # 6. Amount in Words Box
        words_data = [[
            Paragraph(f"<b>Amount Received in Words:</b> {amount_words}", cell_style)
        ]]
        words_table = Table(words_data, colWidths=[180 * mm])
        words_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#bfdbfe")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(words_table)
        elements.append(Spacer(1, 3 * mm))

        # 7. Remarks if available
        if payment.remarks:
            remarks_data = [[
                Paragraph(f"<b>Officer Remarks:</b> {payment.remarks}", cell_style)
            ]]
            remarks_table = Table(remarks_data, colWidths=[180 * mm])
            remarks_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(remarks_table)
            elements.append(Spacer(1, 4 * mm))

        # 8. Signatures & Verification Area
        sig_data = [
            [
                Paragraph("<b>Authorized By:</b><br/>" + (payment.recorded_by or "Accounts Admin"), cell_style),
                Paragraph("<b>Verification Seal / Stamp:</b><br/><font color=\"#64748b\">[Digitally Verified - Zeal ERP]</font>", cell_style),
                Paragraph("<b>Accounts Officer:</b><br/><br/>_______________________", cell_style)
            ]
        ]
        sig_table = Table(sig_data, colWidths=[60 * mm, 60 * mm, 60 * mm])
        sig_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(KeepTogether([
            Spacer(1, 2 * mm),
            sig_table,
            Spacer(1, 4 * mm),
            HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceBefore=2, spaceAfter=2),
            Paragraph("<font size=\"7\" color=\"#64748b\">This is a computer-generated fee receipt issued by Zeal College of Engineering & Research ERP System. For any discrepancies, please contact accounts@zeal.edu.in within 7 days.</font>", sub_style)
        ]))

        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer, receipt_no
