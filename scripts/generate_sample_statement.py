"""
Generates a realistic-looking dummy HDFC Bank statement PDF for testing NyayaSaathi.
All data is completely fictional.
"""

from fpdf import FPDF, XPos, YPos
import os

HDFC_BLUE = (0, 76, 151)
HDFC_LIGHT = (232, 241, 252)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
ROW_ALT = (245, 249, 255)


class HDFCStatement(FPDF):
    def header(self):
        # Blue top bar
        self.set_fill_color(*HDFC_BLUE)
        self.rect(0, 0, 210, 18, style="F")

        # HDFC BANK text in white
        self.set_y(4)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*WHITE)
        self.cell(80, 8, "HDFC BANK", new_x=XPos.RIGHT, new_y=YPos.TOP)

        # Right side: Statement of Account
        self.set_font("Helvetica", "B", 10)
        self.set_x(110)
        self.cell(90, 8, "Statement of Account", align="R",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_y(20)
        self.set_text_color(*BLACK)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*GRAY)
        self.set_fill_color(*HDFC_LIGHT)
        self.rect(0, self.get_y() - 1, 210, 16, style="F")
        self.cell(0, 5,
                  "HDFC Bank Ltd. | Regd. Office: HDFC Bank House, Senapati Bapat Marg, Lower Parel (W), Mumbai - 400013 | "
                  "CIN: L65920MH1994PLC080618",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 4,
                  f"Page {self.page_no()}  |  *THIS IS A DUMMY STATEMENT GENERATED FOR SOFTWARE TESTING PURPOSES ONLY*",
                  align="C")


def cell(pdf, w, h, txt, border=0, align="L", fill=False,
         bold=False, size=9, color=BLACK, new_x=XPos.RIGHT, new_y=YPos.TOP):
    pdf.set_font("Helvetica", "B" if bold else "", size)
    pdf.set_text_color(*color)
    pdf.cell(w, h, txt, border=border, align=align, fill=fill,
             new_x=new_x, new_y=new_y)


def generate():
    pdf = HDFCStatement(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)

    # ── Account Info Block ────────────────────────────────────────────────────
    pdf.set_fill_color(*HDFC_LIGHT)
    pdf.set_draw_color(*HDFC_BLUE)
    pdf.set_line_width(0.3)

    # Two-column account info
    left = [
        ("Account No.",      "50100234567892"),
        ("Customer ID",      "78342910"),
        ("Account Type",     "Regular Savings Account"),
        ("Branch",           "Connaught Place, New Delhi"),
        ("IFSC Code",        "HDFC0001234"),
        ("MICR Code",        "110240087"),
    ]
    right = [
        ("Account Holder",   "Mr. Ramesh Kumar Sharma"),
        ("Address",          "42, Sector-15, Rohini,"),
        ("",                 "New Delhi - 110085"),
        ("Nominee",          "Ms. Sunita Sharma"),
        ("Email",            "ramesh.sharma@gmail.com"),
        ("Mobile",           "+91-98765-XXXXX"),
    ]

    start_y = pdf.get_y()
    col_label_w, col_val_w, gap = 32, 60, 6

    for i, ((lk, lv), (rk, rv)) in enumerate(zip(left, right)):
        y = start_y + i * 6
        pdf.set_xy(10, y)
        cell(pdf, col_label_w, 5.5, lk + ":", bold=True, size=8, color=GRAY,
             border="B" if i == len(left)-1 else 0)
        cell(pdf, col_val_w, 5.5, lv, size=8,
             border="B" if i == len(left)-1 else 0)
        pdf.set_xy(10 + col_label_w + col_val_w + gap, y)
        cell(pdf, col_label_w, 5.5, rk + (":" if rk else ""), bold=True, size=8, color=GRAY,
             border="B" if i == len(right)-1 else 0)
        cell(pdf, 0, 5.5, rv, size=8,
             border="B" if i == len(right)-1 else 0,
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(3)

    # ── Statement Period + Balance Summary ────────────────────────────────────
    pdf.set_fill_color(*HDFC_BLUE)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(95, 6, "  Statement Period: 01-Apr-2025  To  30-Apr-2025",
             fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_fill_color(*HDFC_LIGHT)
    pdf.set_text_color(*BLACK)
    pdf.cell(50, 6, "Opening Bal: Rs.47,320.50", fill=True, align="C",
             new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_fill_color(0, 153, 76)
    pdf.set_text_color(*WHITE)
    pdf.cell(45, 6, "Closing Bal: Rs.69,525.75", fill=True, align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*BLACK)
    pdf.ln(3)

    # ── Transaction Table Header ──────────────────────────────────────────────
    COL = [22, 74, 28, 18, 22, 22, 24]  # widths — total ~210 with margins
    HEADERS = ["Date", "Narration", "Chq./Ref.No.", "Value Dt",
               "Withdrawal\nAmt.(Dr.)", "Deposit\nAmt.(Cr.)", "Closing\nBalance"]

    pdf.set_fill_color(*HDFC_BLUE)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.2)

    row_h = 8
    for i, h in enumerate(HEADERS):
        align = "R" if i >= 4 else "C"
        pdf.multi_cell(COL[i], row_h / 2, h, border=1, align=align,
                       fill=True, max_line_height=4,
                       new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.ln(row_h)

    # ── Transactions ─────────────────────────────────────────────────────────
    transactions = [
        # date, narration, ref, value_dt, dr, cr, balance
        ("01-04-2025", "Opening Balance B/F",                              "",              "",           "",           "",           "47,320.50"),
        ("01-04-2025", "UPI-PAYTM-BSES RAJDHANI POWER LTD-9876543210",    "UPI/25091/1234","01-04-2025", "1,450.00",  "",           "45,870.50"),
        ("03-04-2025", "NEFT CR-HDFC0000001-ABC PRIVATE LIMITED-SALARY",   "NEFT25093891",  "03-04-2025", "",          "55,000.00",  "1,00,870.50"),
        ("05-04-2025", "ATM-SBI ATM-CP INNER CIRCLE NEW DELHI",            "ATM/25095/8872","05-04-2025", "5,000.00",  "",           "95,870.50"),
        ("07-04-2025", "UPI-AMAZON-Amazon Seller Services-7654321098",     "UPI/25097/2341","07-04-2025", "2,349.00",  "",           "93,521.50"),
        ("09-04-2025", "NACH DR-LIC OF INDIA-LICINDIA-984321POLICY",       "NACH25099812",  "09-04-2025", "3,200.00",  "",           "90,321.50"),
        ("10-04-2025", "UPI-SWIGGY-Bundl Technologies-8765432109",         "UPI/25100/4512","10-04-2025", "485.00",    "",           "89,836.50"),
        ("12-04-2025", "IMPS-919912341234-VIJAY KUMAR-RENT APRIL",         "IMPS25124001",  "12-04-2025", "15,000.00", "",           "74,836.50"),
        ("14-04-2025", "UPI-PHONEPE-Vi Recharge-9988776655",               "UPI/25140/6712","14-04-2025", "399.00",    "",           "74,437.50"),
        ("15-04-2025", "NEFT CR-ICIC0001234-XYZ TECHNOLOGIES-FREELANCE",   "NEFT25154421",  "15-04-2025", "",          "8,000.00",   "82,437.50"),
        ("17-04-2025", "UPI-BOOKMYSHOW-Bigtree Entertainment-9876543211",  "UPI/25170/3312","17-04-2025", "700.00",    "",           "81,737.50"),
        ("18-04-2025", "POS-RELIANCE RETAIL LTD-NEW DELHI",                "POS/25183/3345","18-04-2025", "1,234.00",  "",           "80,503.50"),
        ("19-04-2025", "UPI-OLAMONEY-ANI Technologies Pvt Ltd-76543",      "UPI/25190/9812","19-04-2025", "320.00",    "",           "80,183.50"),
        ("20-04-2025", "UPI-ZEPTO-Kiranakart Technologies-87654",          "UPI/25200/1123","20-04-2025", "892.00",    "",           "79,291.50"),
        ("21-04-2025", "RTGS-HDFC0001234-SELF TRANSFER-FD BOOKING",        "RTGS25219001",  "21-04-2025", "15,000.00", "",           "64,291.50"),
        ("22-04-2025", "INT PAID ON SAVINGS A/C APR25",                    "INT/2504/SV",   "22-04-2025", "",          "312.25",     "64,603.75"),
        ("24-04-2025", "UPI-MEESHO-Fashnear Technologies-65432",           "UPI/25240/7823","24-04-2025", "1,450.00",  "",           "63,153.75"),
        ("25-04-2025", "NACH DR-HDFC BANK-HDFC HOME LOAN-LNXXXXXX4892",    "NACH25258801",  "25-04-2025", "12,000.00", "",           "51,153.75"),
        ("26-04-2025", "UPI-GPAY-MIRAE ASSET MF SIP-9876500001",           "UPI/25260/4451","26-04-2025", "5,000.00",  "",           "46,153.75"),
        ("27-04-2025", "NEFT CR-SBIN0001234-CLIENT B SOLUTIONS-INVOICE",   "NEFT25279901",  "27-04-2025", "",          "18,000.00",  "64,153.75"),
        ("28-04-2025", "UPI-BIGBASKET-Supermarket Grocery Supplies-543",   "UPI/25280/6612","28-04-2025", "987.00",    "",           "63,166.75"),
        ("29-04-2025", "CASH DEP-CDM-HDFC BANK-CP BRANCH",                 "CDM/25299/0123","29-04-2025", "",          "1,500.00",   "64,666.75"),
        ("30-04-2025", "CHRG-SMS ALERT CHARGES Q1 FY2526",                 "CHG/2504/SMS",  "30-04-2025", "121.00",    "",           "64,545.75"),
        ("30-04-2025", "CGST+SGST ON BANK CHARGES @18%",                   "GST/2504/BC",   "30-04-2025", "21.78",     "",           "64,523.97"),
        ("30-04-2025", "REVERSAL-UPI DISPUTE-REF UPI/25070/1234",          "REV/2504/001",  "30-04-2025", "",          "2,000.00",   "66,523.97"),
        ("30-04-2025", "INT PAID ON SAVINGS BALANCE-APR25 FINAL",          "INT/2504/FIN",  "30-04-2025", "",          "3,001.78",   "69,525.75"),
        ("30-04-2025", "Closing Balance C/F",                              "",              "",           "",           "",           "69,525.75"),
    ]

    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_draw_color(210, 210, 210)

    for idx, row in enumerate(transactions):
        is_header_row = row[1] in ("Opening Balance B/F", "Closing Balance C/F")
        is_cr = row[5] != "" and row[4] == ""

        if is_header_row:
            pdf.set_fill_color(*HDFC_LIGHT)
        elif idx % 2 == 0:
            pdf.set_fill_color(250, 252, 255)
        else:
            pdf.set_fill_color(*WHITE)

        pdf.set_text_color(*BLACK)
        for i, val in enumerate(row):
            align = "R" if i >= 4 else "L"
            bold = is_header_row or (i == 5 and is_cr)
            color = (0, 120, 50) if (i == 5 and is_cr and not is_header_row) else \
                    (180, 0, 0)   if (i == 4 and row[4] != "" and not is_header_row) else BLACK
            pdf.set_font("Helvetica", "B" if bold else "", 7.5)
            pdf.set_text_color(*color)
            pdf.cell(COL[i], 5.5, val, border=1, align=align, fill=True,
                     new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.ln(5.5)

    pdf.ln(4)

    # ── Summary ───────────────────────────────────────────────────────────────
    pdf.set_fill_color(*HDFC_LIGHT)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*HDFC_BLUE)
    pdf.cell(0, 6, "  Transaction Summary for the Period", fill=True,
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*BLACK)
    summary = [
        ("Total Credits (Dr.):", "Rs. 84,814.03", "Total Debits (Cr.):", "Rs. 62,608.78"),
        ("No. of Credit Transactions:", "8", "No. of Debit Transactions:", "18"),
    ]
    for lk, lv, rk, rv in summary:
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(55, 5.5, lk)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(45, 5.5, lv, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(60, 5.5, rk)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(0, 5.5, rv, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(4)

    # ── Notes ─────────────────────────────────────────────────────────────────
    pdf.set_draw_color(*HDFC_BLUE)
    pdf.set_line_width(0.3)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(*HDFC_BLUE)
    pdf.cell(0, 4.5, "Important Notes:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*GRAY)
    notes = [
        "1. Kindly verify this statement and report any discrepancy to your branch within 30 days of receipt.",
        "2. ** THIS IS A SAMPLE/DUMMY STATEMENT GENERATED FOR SOFTWARE TESTING. ALL DATA IS FICTIONAL. **",
        "3. For queries, contact HDFC Customer Care: 1800-202-6161 (Toll Free) | customerservice@hdfcbank.com",
        "4. Interest on Savings Account is calculated on daily closing balance and credited quarterly.",
        "5. Minimum Average Balance (MAB): Rs.10,000 (Urban). Non-maintenance charges apply if balance falls below MAB.",
        "6. This statement is digitally generated and does not require a signature.",
    ]
    for note in notes:
        pdf.cell(0, 4, note, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_hdfc_statement.pdf")
    pdf.output(out_path)
    print(f"Generated: {out_path}")


if __name__ == "__main__":
    generate()
