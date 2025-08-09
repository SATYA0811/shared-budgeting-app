from fpdf import FPDF

class PDFPlan(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Shared Budgeting App - Architecture & Development Plan", ln=True, align="C")
        self.ln(5)

    def chapter_title(self, num, label):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, f"{num}. {label}", ln=True)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 8, body)
        self.ln()

pdf = PDFPlan()
pdf.add_page()

# Title
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "Shared Budgeting App: Full Architecture and Step-by-Step Plan", ln=True, align="C")
pdf.ln(10)

# 1. Full Model Architecture
pdf.chapter_title(1, "Full Model Architecture")

architecture_text = (
    "Entities & Data Models:\n\n"
    "- User: id, name, email, password_hash, created_at\n"
    "- Household: id, name, created_at\n"
    "- HouseholdUser: household_id, user_id, role (owner/admin/member)\n"
    "- Account: id, household_id, name, type (bank/card), last4, currency\n"
    "- Transaction: id, account_id, date, description, amount, category_id, user_id, source_file_id\n"
    "- Category: id, name, parent_id, default_budget\n"
    "- Income: id, user_id, date, amount, source, notes\n"
    "- Goal: id, user_id, name, target_amount, current_amount, target_date, recurrence\n"
    "- File: id, household_id, user_id, s3_key, parsed_json_key, status\n\n"

    "High-Level System Components:\n\n"
    "- Frontend UI: React + Tailwind CSS, dashboard, forms, file upload, analytics.\n"
    "- Backend API: FastAPI, authentication, file upload, parsing orchestration, CRUD.\n"
    "- File Storage: AWS S3 or local dev storage.\n"
    "- Database: PostgreSQL (prod), SQLite (dev).\n"
    "- Parsing Worker: Async jobs for PDF parsing, OCR, normalization.\n"
    "- ML Classification: Auto categorization and anomaly detection.\n"
    "- Analytics Engine: Aggregations and suggestions.\n"
    "- Authentication: OAuth/JWT, household sharing.\n"
)

pdf.chapter_body(architecture_text)

# 2. What is Already Done
pdf.chapter_title(2, "What is Already Done")

done_text = (
    "- React dashboard mockup with combined views and transaction layout.\n"
    "- FastAPI backend starter with /upload-statement endpoint for raw PDF text extraction.\n"
    "- Basic database model skeleton (users, transactions).\n"
)

pdf.chapter_body(done_text)

# 3. Next Steps: Detailed Plan to Build
pdf.chapter_title(3, "Next Steps: Detailed Plan to Build")

next_steps_text = (
    "Step 1: Set Up Database & Authentication\n"
    "- Implement full DB schema, user registration/login with JWT.\n"
    "- Household sharing with roles and invites.\n\n"

    "Step 2: File Upload & Parsing Pipeline\n"
    "- Extend file type support, async job queue for parsing.\n"
    "- PDF parsing with pdfplumber and OCR fallback.\n"
    "- Normalize transactions and store parsed data.\n\n"

    "Step 3: Categorization & Transaction Management\n"
    "- Rule-based and ML-based categorization.\n"
    "- CRUD for transactions and user assignments.\n\n"

    "Step 4: Income & Expenses Tracking\n"
    "- Income entry, automatic balance calculation, historical trends.\n\n"

    "Step 5: Goals & Investment Tracking\n"
    "- Create and track savings/investment goals with progress visualization.\n\n"

    "Step 6: Analytics & Insights\n"
    "- Aggregated spending data, alerts, suggestions.\n\n"

    "Step 7: Polish, Security & Deployment\n"
    "- Add security measures, CI/CD, deploy backend/frontend.\n"
)

pdf.chapter_body(next_steps_text)

# 4. Timeline Suggestion
pdf.chapter_title(4, "Timeline Suggestion")

timeline_text = (
    "Week 1: Database, Authentication, Household Sharing\n"
    "Week 2: File Upload & Parsing Worker\n"
    "Week 3: Categorization & Transactions CRUD\n"
    "Week 4: Income & Expenses Tracking UI\n"
    "Week 5: Goals Tracking & Progress UI\n"
    "Week 6: Analytics, Alerts, Suggestions\n"
    "Week 7: Testing, Security, Deployment\n"
)

pdf.chapter_body(timeline_text)

# 5. Tools & Libraries
pdf.chapter_title(5, "Tools & Libraries")

tools_text = (
    "- Frontend: React, Tailwind CSS, Chart.js/Recharts\n"
    "- Backend: FastAPI, SQLAlchemy, Alembic, RQ/Celery, pdfplumber, pytesseract\n"
    "- Database: PostgreSQL (production), SQLite (development)\n"
    "- Storage: AWS S3 or local\n"
    "- ML: Python scikit-learn or LightGBM\n"
    "- Authentication: OAuth2 / JWT\n"
)

pdf.chapter_body(tools_text)

# Save PDF file
pdf.output("shared_budgeting_app_plan.pdf")
print("PDF generated: shared_budgeting_app_plan.pdf")
