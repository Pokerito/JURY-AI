"""Seed script — populate the database with demo data for instant demo readiness.

Usage:
    python -m scripts.seed

Creates:
    - 1 Organization ("Jury-AI Demo Corp")
    - 3 Users (admin, analyst, viewer)
    - 2 Documents (with pre-computed analysis results)
    - Risk analyses with clauses
    - Sample RAG queries
"""
import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.config import get_settings
from app.core.security import hash_password
from app.core.constants import UserRole, DocumentStatus, AnalysisType, RiskLevel

# ── Fixed UUIDs for consistent demo ──────────────────────────────────────────
ORG_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
ADMIN_ID = uuid.UUID("aaaa0001-0001-0001-0001-000000000001")
ANALYST_ID = uuid.UUID("aaaa0002-0002-0002-0002-000000000002")
VIEWER_ID = uuid.UUID("aaaa0003-0003-0003-0003-000000000003")
DOC1_ID = uuid.UUID("dddd0001-0001-0001-0001-000000000001")
DOC2_ID = uuid.UUID("dddd0002-0002-0002-0002-000000000002")
ANALYSIS1_ID = uuid.UUID("bbbb0001-0001-0001-0001-000000000001")
ANALYSIS2_ID = uuid.UUID("bbbb0002-0002-0002-0002-000000000002")
QUERY1_ID = uuid.UUID("cccc0001-0001-0001-0001-000000000001")

# ── Demo password (bcrypt hashed) ────────────────────────────────────────────
DEMO_PASSWORD = "DemoPass123!"
DEMO_PASSWORD_HASH = hash_password(DEMO_PASSWORD)

NOW = datetime.now(timezone.utc)


async def seed():
    """Seed the database with demo data."""
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    from app.models.base import Base
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.document import Document
    from app.models.analysis import Analysis, RiskClause
    from app.models.query import Query

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        # Check if already seeded
        from sqlalchemy import select
        existing_org = await session.execute(select(Organization).where(Organization.id == ORG_ID))
        if existing_org.scalar_one_or_none():
            print("ℹ️ Database is already seeded with demo data.")
            await engine.dispose()
            return
        # ── 1. Organization ──────────────────────────────────────────────
        from app.models.organization import Organization

        org = Organization(
            id=ORG_ID,
            name="Jury-AI Demo Corp",
            slug="jury-ai-demo",
            plan="pro",
        )
        session.add(org)
        await session.flush()
        print("[OK] Organization: Jury-AI Demo Corp")

        # ── 2. Users ─────────────────────────────────────────────────────
        from app.models.user import User

        users = [
            User(
                id=ADMIN_ID,
                org_id=ORG_ID,
                email="admin@juryai.demo",
                password_hash=DEMO_PASSWORD_HASH,
                full_name="Gaurav Jha",
                role=UserRole.ADMIN.value,
                is_active=True,
            ),
            User(
                id=ANALYST_ID,
                org_id=ORG_ID,
                email="analyst@juryai.demo",
                password_hash=DEMO_PASSWORD_HASH,
                full_name="Kalash Verma",
                role=UserRole.ANALYST.value,
                is_active=True,
            ),
            User(
                id=VIEWER_ID,
                org_id=ORG_ID,
                email="viewer@juryai.demo",
                password_hash=DEMO_PASSWORD_HASH,
                full_name="Komal Raj",
                role=UserRole.VIEWER.value,
                is_active=True,
            ),
        ]
        session.add_all(users)
        await session.flush()
        print("[OK] Users: admin, analyst, viewer (password: DemoPass123!)")

        # ── 3. Documents ─────────────────────────────────────────────────
        from app.models.document import Document

        doc1 = Document(
            id=DOC1_ID,
            user_id=ADMIN_ID,
            org_id=ORG_ID,
            filename="software_development_agreement.pdf",
            file_type="pdf",
            file_size_bytes=245_760,
            storage_key=f"{ORG_ID}/{DOC1_ID}/software_development_agreement.pdf",
            status=DocumentStatus.ANALYZED.value,
            raw_text_preview=(
                "SOFTWARE DEVELOPMENT AGREEMENT\n\n"
                "This Software Development Agreement (the 'Agreement') is entered into as of "
                "January 15, 2024, by and between TechCorp Inc., a Delaware corporation "
                "('Client'), and DevStudio LLC, a California limited liability company "
                "('Developer'). The Developer agrees to design, develop, and deliver the "
                "software application described in Exhibit A..."
            ),
            chunk_count=12,
            is_deleted=False,
        )
        doc2 = Document(
            id=DOC2_ID,
            user_id=ANALYST_ID,
            org_id=ORG_ID,
            filename="employment_nda_contract.docx",
            file_type="docx",
            file_size_bytes=128_000,
            storage_key=f"{ORG_ID}/{DOC2_ID}/employment_nda_contract.docx",
            status=DocumentStatus.ANALYZED.value,
            raw_text_preview=(
                "NON-DISCLOSURE AGREEMENT\n\n"
                "This Non-Disclosure Agreement ('NDA') is made effective as of March 1, 2024, "
                "between GlobalFinance Corp. ('Disclosing Party') and Jane Smith ('Receiving "
                "Party'). The Receiving Party agrees to protect all Confidential Information "
                "shared during the course of employment..."
            ),
            chunk_count=8,
            is_deleted=False,
        )
        session.add_all([doc1, doc2])
        await session.flush()
        print("[OK] Documents: software_development_agreement.pdf, employment_nda_contract.docx")

        # ── 4. Analyses + Risk Clauses ───────────────────────────────────
        from app.models.analysis import Analysis, RiskClause

        # Analysis for Doc 1 (Software Dev Agreement) — Score: 45/100
        analysis1 = Analysis(
            id=ANALYSIS1_ID,
            document_id=DOC1_ID,
            analysis_type=AnalysisType.RISK_SCORE.value,
            result={
                "summary": "Software development agreement with several high-risk clauses around IP assignment and liability.",
            },
            safety_score=45,
            processing_time_ms=3420,
            model_used="gemini-2.5-flash",
            idempotency_key="seed-analysis-doc1",
        )
        session.add(analysis1)
        await session.flush()

        clauses_doc1 = [
            RiskClause(
                id=uuid.uuid4(),
                analysis_id=ANALYSIS1_ID,
                clause_name="Unlimited Liability",
                risk_level=RiskLevel.CRITICAL.value,
                justification="Developer assumes unlimited financial liability for any defects, bugs, or performance issues with no cap on damages.",
                safer_alternative="Limit liability to the total contract value or a reasonable multiple thereof. Include mutual limitation of liability.",
                sort_order=0,
            ),
            RiskClause(
                id=uuid.uuid4(),
                analysis_id=ANALYSIS1_ID,
                clause_name="Broad IP Assignment",
                risk_level=RiskLevel.CRITICAL.value,
                justification="All intellectual property, including pre-existing tools and frameworks, becomes the Client's property upon creation.",
                safer_alternative="Assign only the deliverable IP to Client. Developer retains rights to pre-existing tools, frameworks, and general knowledge.",
                sort_order=1,
            ),
            RiskClause(
                id=uuid.uuid4(),
                analysis_id=ANALYSIS1_ID,
                clause_name="Non-Compete Clause",
                risk_level=RiskLevel.HIGH.value,
                justification="24-month non-compete covering all software development work globally — overly broad in scope and geography.",
                safer_alternative="Limit non-compete to 6 months, within the same industry vertical, and a reasonable geographic area.",
                sort_order=2,
            ),
            RiskClause(
                id=uuid.uuid4(),
                analysis_id=ANALYSIS1_ID,
                clause_name="Payment Terms",
                risk_level=RiskLevel.MEDIUM.value,
                justification="Net-60 payment terms with no late payment penalties. Developer bears all costs during this period.",
                safer_alternative=None,
                sort_order=3,
            ),
            RiskClause(
                id=uuid.uuid4(),
                analysis_id=ANALYSIS1_ID,
                clause_name="Governing Law",
                risk_level=RiskLevel.LOW.value,
                justification="Governed by Delaware law with disputes resolved in Delaware courts. Standard and reasonable.",
                safer_alternative=None,
                sort_order=4,
            ),
            RiskClause(
                id=uuid.uuid4(),
                analysis_id=ANALYSIS1_ID,
                clause_name="Confidentiality",
                risk_level=RiskLevel.LOW.value,
                justification="Standard mutual confidentiality clause with 3-year term. Well-balanced and reasonable.",
                safer_alternative=None,
                sort_order=5,
            ),
        ]
        session.add_all(clauses_doc1)

        # Analysis for Doc 2 (NDA) — Score: 70/100
        analysis2 = Analysis(
            id=ANALYSIS2_ID,
            document_id=DOC2_ID,
            analysis_type=AnalysisType.RISK_SCORE.value,
            result={
                "summary": "Employment NDA with moderate risk — perpetual confidentiality and broad definition of confidential information.",
            },
            safety_score=70,
            processing_time_ms=2180,
            model_used="gemini-2.5-flash",
            idempotency_key="seed-analysis-doc2",
        )
        session.add(analysis2)
        await session.flush()

        clauses_doc2 = [
            RiskClause(
                id=uuid.uuid4(),
                analysis_id=ANALYSIS2_ID,
                clause_name="Perpetual Confidentiality",
                risk_level=RiskLevel.HIGH.value,
                justification="Confidentiality obligations have no expiration date and survive indefinitely after employment ends.",
                safer_alternative="Limit confidentiality obligations to 2-5 years after termination, except for trade secrets which may be protected indefinitely.",
                sort_order=0,
            ),
            RiskClause(
                id=uuid.uuid4(),
                analysis_id=ANALYSIS2_ID,
                clause_name="Broad Definition of Confidential Information",
                risk_level=RiskLevel.HIGH.value,
                justification="'Confidential Information' is defined to include virtually all information encountered during employment, including publicly available data.",
                safer_alternative="Narrow the definition to specifically marked or clearly identified confidential materials. Exclude publicly available information.",
                sort_order=1,
            ),
            RiskClause(
                id=uuid.uuid4(),
                analysis_id=ANALYSIS2_ID,
                clause_name="Remedies and Injunctive Relief",
                risk_level=RiskLevel.MEDIUM.value,
                justification="Allows the company to seek injunctive relief without posting a bond, shifting burden entirely to the employee.",
                safer_alternative=None,
                sort_order=2,
            ),
            RiskClause(
                id=uuid.uuid4(),
                analysis_id=ANALYSIS2_ID,
                clause_name="Scope of Agreement",
                risk_level=RiskLevel.LOW.value,
                justification="Clearly defines the scope as employment-related information only. Reasonable and well-bounded.",
                safer_alternative=None,
                sort_order=3,
            ),
            RiskClause(
                id=uuid.uuid4(),
                analysis_id=ANALYSIS2_ID,
                clause_name="Governing Law",
                risk_level=RiskLevel.LOW.value,
                justification="Governed by New York law. Standard jurisdiction clause.",
                safer_alternative=None,
                sort_order=4,
            ),
        ]
        session.add_all(clauses_doc2)
        print("[OK] Analyses: 2 risk analyses with 11 total clauses")

        # ── 5. Sample RAG Query ──────────────────────────────────────────
        from app.models.query import Query

        query1 = Query(
            id=QUERY1_ID,
            document_id=DOC1_ID,
            user_id=ADMIN_ID,
            question="What are the payment terms in this agreement?",
            answer=(
                "Based on the contract, the payment terms are Net-60. This means the Client "
                "has 60 days from the date of invoice to make payment. The agreement does not "
                "include any provisions for late payment penalties or interest charges. The "
                "Developer is responsible for bearing all costs during this 60-day period."
            ),
            retrieved_chunks={
                "chunks": [
                    "Payment shall be made within sixty (60) days of receipt of invoice...",
                    "The Developer shall submit monthly invoices for work completed...",
                    "All payments shall be made in US Dollars via wire transfer...",
                ],
                "count": 3,
            },
            processing_time_ms=1850,
        )
        session.add(query1)
        print("[OK] Sample query: 'What are the payment terms?'")

        # ── Commit everything ────────────────────────────────────────────
        await session.commit()

    await engine.dispose()

    print("\n" + "=" * 60)
    print("[SUCCESS] Database seeded successfully!")
    print("=" * 60)
    print("\n Demo Credentials:")
    print(f"   Admin:   admin@juryai.demo   / {DEMO_PASSWORD}")
    print(f"   Analyst: analyst@juryai.demo / {DEMO_PASSWORD}")
    print(f"   Viewer:  viewer@juryai.demo  / {DEMO_PASSWORD}")
    print(f"\n Documents: 2 pre-analyzed contracts")
    print(f"   - software_development_agreement.pdf (Score: 45/100 -- High Risk)")
    print(f"   - employment_nda_contract.docx (Score: 70/100 -- Moderate Risk)")
    print(f"\n API: http://localhost:8000/docs")
    print(f"   Login -> POST /api/v1/auth/login")
    print()


if __name__ == "__main__":
    asyncio.run(seed())
