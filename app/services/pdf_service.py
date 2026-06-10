from datetime import datetime, timedelta
from pathlib import Path
from contextlib import redirect_stderr
import io
import re

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import APP_DIR, GENERATED_DIR


class PDFService:
    def __init__(self) -> None:
        self.env = Environment(
            loader=FileSystemLoader(APP_DIR / "templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_resume(
        self,
        resume_strategy: dict,
        jd_analysis: dict,
        evaluation: dict,
        output_path: Path,
    ) -> None:
        html = self.env.get_template("resume.html").render(
            resume=resume_strategy,
            jd=jd_analysis,
            evaluation=evaluation,
            generated_at=datetime.now().strftime("%d %b %Y"),
        )
        if not self._render_with_weasyprint(html, output_path):
            if not self._render_resume_with_reportlab(resume_strategy, evaluation, output_path):
                self._render_plain_pdf(output_path, self._resume_lines(resume_strategy, evaluation))

    def render_cover_letter(
        self,
        cover_letter: dict,
        profile: dict,
        company_name: str | None,
        role_title: str | None,
        output_path: Path,
    ) -> None:
        html = self.env.get_template("cover_letter.html").render(
            letter=cover_letter,
            profile=profile,
            company_name=company_name or "Hiring Team",
            role_title=role_title or "Open Role",
            generated_at=datetime.now().strftime("%d %b %Y"),
        )
        if not self._render_with_weasyprint(html, output_path):
            if not self._render_cover_with_reportlab(cover_letter, profile, company_name, role_title, output_path):
                self._render_plain_pdf(output_path, self._cover_lines(cover_letter, profile, company_name, role_title))

    def prune_old_files(self) -> None:
        cutoff = datetime.now() - timedelta(hours=12)
        for path in GENERATED_DIR.glob("*.pdf"):
            modified = datetime.fromtimestamp(path.stat().st_mtime)
            if modified < cutoff:
                path.unlink(missing_ok=True)

    def _render_with_weasyprint(self, html: str, output_path: Path) -> bool:
        try:
            with redirect_stderr(io.StringIO()):
                from weasyprint import HTML

                HTML(string=html, base_url=str(APP_DIR)).write_pdf(output_path)
            return True
        except Exception:
            return False

    def _styles(self):
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="Name", fontSize=22, leading=26, textColor=colors.HexColor("#0f172a"), spaceAfter=3))
        styles.add(ParagraphStyle(name="Section", fontSize=10, leading=13, textColor=colors.HexColor("#164e63"), spaceBefore=10, spaceAfter=5, uppercase=True))
        styles.add(ParagraphStyle(name="Small", fontSize=8.5, leading=11, textColor=colors.HexColor("#64748b")))
        styles["BodyText"].fontSize = 9.5
        styles["BodyText"].leading = 13
        return styles

    def _doc(self, output_path: Path):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate

        return SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=16 * mm,
            leftMargin=16 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
        )

    def _p(self, text: str, style):
        from reportlab.platypus import Paragraph

        return Paragraph(str(text).replace("&", "&amp;"), style)

    def _render_resume_with_reportlab(self, resume: dict, evaluation: dict, output_path: Path) -> bool:
        try:
            from reportlab.lib import colors
            from reportlab.lib.units import mm
            from reportlab.platypus import Spacer, Table, TableStyle
        except Exception:
            return False

        styles = self._styles()
        story = [
            self._p(resume.get("candidate_name", "Candidate"), styles["Name"]),
            self._p(resume.get("headline", ""), styles["Small"]),
            Spacer(1, 6),
            self._p(resume.get("summary", ""), styles["BodyText"]),
            self._p(f"ATS Match Score: {evaluation.get('score', 0)}%", styles["Section"]),
        ]

        skills = resume.get("core_skills", [])
        if skills:
            rows = [[self._p(skill, styles["BodyText"]) for skill in skills[index:index + 3]] for index in range(0, len(skills), 3)]
            table = Table(rows, hAlign="LEFT", colWidths=[55 * mm, 55 * mm, 55 * mm])
            table.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.HexColor("#d8e0e7")), ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d8e0e7")), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc"))]))
            story.extend([self._p("Core Skills", styles["Section"]), table])

        story.append(self._p("Selected Experience", styles["Section"]))
        for item in resume.get("selected_experience", []):
            story.append(self._p(f"<b>{item.get('role', '')}</b> | {item.get('organization', '')}", styles["BodyText"]))
            for point in item.get("highlights", []):
                story.append(self._p(f"- {point}", styles["BodyText"]))

        story.append(self._p("Relevant Projects", styles["Section"]))
        for project in resume.get("selected_projects", []):
            story.append(self._p(f"<b>{project.get('name', '')}</b>: {project.get('summary', '')}", styles["BodyText"]))

        story.append(self._p("Education", styles["Section"]))
        for edu in resume.get("education", []):
            story.append(self._p(f"<b>{edu.get('program', '')}</b>, {edu.get('institution', '')}. {edu.get('notes', '')}", styles["BodyText"]))

        story.append(self._p("ATS Alignment", styles["Section"]))
        story.append(self._p(f"Matched: {', '.join(evaluation.get('matched_skills', []))}", styles["BodyText"]))
        story.append(self._p(f"Transparent gaps: {', '.join(evaluation.get('missing_skills', []))}", styles["BodyText"]))
        self._doc(output_path).build(story)
        return True

    def _render_cover_with_reportlab(self, letter: dict, profile: dict, company_name: str | None, role_title: str | None, output_path: Path) -> bool:
        try:
            from reportlab.platypus import Spacer
        except Exception:
            return False

        styles = self._styles()
        story = [
            self._p(profile.get("name", "Candidate"), styles["Name"]),
            self._p(f"{role_title or 'Open Role'} | {company_name or 'Hiring Team'}", styles["Small"]),
            Spacer(1, 18),
            self._p(letter.get("greeting", "Dear Hiring Team,"), styles["BodyText"]),
        ]
        for paragraph in letter.get("paragraphs", []):
            story.extend([Spacer(1, 6), self._p(paragraph, styles["BodyText"])])
        story.extend([
            Spacer(1, 8),
            self._p(letter.get("closing", "Thank you for your consideration."), styles["BodyText"]),
            Spacer(1, 12),
            self._p(letter.get("signature", profile.get("name", "")), styles["BodyText"]),
        ])
        self._doc(output_path).build(story)
        return True

    def _resume_lines(self, resume: dict, evaluation: dict) -> list[str]:
        lines = [
            resume.get("candidate_name", "Candidate"),
            resume.get("headline", ""),
            "",
            "PROFESSIONAL SUMMARY",
            resume.get("summary", ""),
            "",
            f"ATS MATCH SCORE: {evaluation.get('score', 0)}%",
            "",
            "CORE SKILLS",
            ", ".join(resume.get("core_skills", [])),
            "",
            "SELECTED EXPERIENCE",
        ]
        for item in resume.get("selected_experience", []):
            lines.append(f"{item.get('role', '')} | {item.get('organization', '')}")
            lines.extend([f"- {point}" for point in item.get("highlights", [])])
        lines.extend(["", "RELEVANT PROJECTS"])
        for project in resume.get("selected_projects", []):
            lines.append(f"{project.get('name', '')}: {project.get('summary', '')}")
        lines.extend(["", "EDUCATION"])
        for edu in resume.get("education", []):
            lines.append(f"{edu.get('program', '')}, {edu.get('institution', '')}. {edu.get('notes', '')}")
        lines.extend(["", "ATS ALIGNMENT", f"Matched: {', '.join(evaluation.get('matched_skills', []))}", f"Transparent gaps: {', '.join(evaluation.get('missing_skills', []))}"])
        return lines

    def _cover_lines(self, letter: dict, profile: dict, company_name: str | None, role_title: str | None) -> list[str]:
        lines = [
            profile.get("name", "Candidate"),
            f"{role_title or 'Open Role'} | {company_name or 'Hiring Team'}",
            "",
            letter.get("greeting", "Dear Hiring Team,"),
            "",
        ]
        for paragraph in letter.get("paragraphs", []):
            lines.extend([paragraph, ""])
        lines.extend([letter.get("closing", "Thank you for your consideration."), "", letter.get("signature", profile.get("name", ""))])
        return lines

    def _render_plain_pdf(self, output_path: Path, lines: list[str]) -> None:
        escaped_lines = []
        for line in self._wrap_lines(lines):
            clean = re.sub(r"[^\x09\x0A\x0D\x20-\x7E]", "", str(line))
            clean = clean.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            escaped_lines.append(clean)

        text_commands = ["BT", "/F1 10 Tf", "50 790 Td", "14 TL"]
        for line in escaped_lines:
            text_commands.append(f"({line}) Tj")
            text_commands.append("T*")
        text_commands.append("ET")
        stream = "\n".join(text_commands).encode("latin-1", errors="ignore")

        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
        ]

        content = [b"%PDF-1.4\n"]
        offsets = []
        for index, obj in enumerate(objects, start=1):
            offsets.append(sum(len(part) for part in content))
            content.append(f"{index} 0 obj\n".encode("ascii") + obj + b"\nendobj\n")
        xref_offset = sum(len(part) for part in content)
        xref = [b"xref\n", f"0 {len(objects) + 1}\n".encode("ascii"), b"0000000000 65535 f \n"]
        xref.extend([f"{offset:010d} 00000 n \n".encode("ascii") for offset in offsets])
        trailer = f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
        output_path.write_bytes(b"".join(content + xref + [trailer]))

    def _wrap_lines(self, lines: list[str], width: int = 92, max_lines: int = 54) -> list[str]:
        wrapped = []
        for line in lines:
            text = str(line)
            if not text:
                wrapped.append("")
                continue
            while len(text) > width:
                split_at = text.rfind(" ", 0, width)
                split_at = split_at if split_at > 0 else width
                wrapped.append(text[:split_at])
                text = text[split_at:].strip()
            wrapped.append(text)
            if len(wrapped) >= max_lines:
                wrapped.append("Continued details available in the generated strategy output.")
                break
        return wrapped
