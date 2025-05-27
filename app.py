import streamlit as st
from fpdf import FPDF
import tempfile

# -------------------- Config --------------------
st.set_page_config(layout="wide", page_title="ATS Resume Builder", page_icon="📄")
st.title("📄 Resume Builder - ATS Friendly")
st.markdown("Create a professional, ATS-optimized resume in minutes!")

# -------------------- Form Inputs --------------------
st.sidebar.header("📝 Enter Resume Details")

# Section Order Configuration
st.sidebar.markdown("### 📋 Section Order")
section_order = st.sidebar.selectbox(
    "Choose Resume Layout",
    options=[
        "Traditional (Experience First)",
        "Recent Graduate (Education First)", 
        "Tech-Focused (Skills First)",
        "Career Changer (Skills & Projects First)",
        "Custom Order"
    ],
    help="Select the order that best fits your career stage and goals"
)

# Basic Info
st.sidebar.markdown("### 👤 Personal Information")
name = st.sidebar.text_input("Full Name", placeholder="e.g. Jane Doe")
email = st.sidebar.text_input("Email", placeholder="e.g. jane.doe@email.com")
phone = st.sidebar.text_input("Phone", placeholder="e.g. +1 (555) 123-4567")
address = st.sidebar.text_area("Address", placeholder="e.g. 123 Main Street, New York, NY 10001", height=70)
linkedin = st.sidebar.text_input("LinkedIn", placeholder="e.g. linkedin.com/in/yourprofile")
github = st.sidebar.text_input("GitHub (Optional)", placeholder="e.g. github.com/yourprofile")

# Additional Professional Profiles (ATS-Friendly)
st.sidebar.markdown("### 🌐 Additional Profiles")
kaggle = st.sidebar.text_input("Kaggle Profile (Optional)", placeholder="e.g. kaggle.com/yourprofile")
docker_hub = st.sidebar.text_input("Docker Hub (Optional)", placeholder="e.g. hub.docker.com/u/yourprofile")
streamlit_profile = st.sidebar.text_input("Streamlit Cloud (Optional)", placeholder="e.g. share.streamlit.io/yourprofile")
portfolio_website = st.sidebar.text_input("Portfolio Website (Optional)", placeholder="e.g. yourportfolio.com")

# About Me
st.sidebar.markdown("### 💭 Professional Summary")
about = st.sidebar.text_area("Professional Summary", 
                            placeholder="Write a compelling 3-4 line summary highlighting your key strengths and career objectives.",
                            height=100)

# Skills
st.sidebar.markdown("### 💻 Technical Skills")
skills = st.sidebar.text_area("Technical Skills", 
                             placeholder="Python, JavaScript, React, SQL, AWS, Docker, Git, Machine Learning",
                             height=85)

# Work Experience (Dynamic)
st.sidebar.markdown("### 💼 Work Experience")
num_work = st.sidebar.number_input("Number of Work Experiences", min_value=0, max_value=8, value=1, step=1)
work_experience_list = []

for i in range(num_work):
    with st.sidebar.expander(f"Work Experience #{i+1}"):
        title = st.text_input(f"Job Title", key=f"work_title_{i}", 
                             placeholder="e.g. Software Engineer")
        company = st.text_input(f"Company", key=f"work_company_{i}", 
                               placeholder="e.g. Tech Corp")
        duration = st.text_input(f"Duration", key=f"work_duration_{i}", 
                                placeholder="e.g. Jan 2022 - Present")
        details = st.text_area(f"Key Achievements & Responsibilities", key=f"work_details_{i}", 
                              placeholder="• Developed and maintained web applications\n• Improved system performance by 30%\n• Led a team of 3 developers",
                              height=100)
        work_experience_list.append((title, company, duration, details))

# Education (Dynamic)
st.sidebar.markdown("### 🎓 Education")
num_edu = st.sidebar.number_input("Number of Education Entries", min_value=1, max_value=5, value=1, step=1)
education_list = []

for i in range(num_edu):
    with st.sidebar.expander(f"Education #{i+1}"):
        degree = st.text_input(f"Degree", key=f"edu_degree_{i}", 
                              placeholder="e.g. Bachelor of Science in Computer Science")
        institution = st.text_input(f"Institution", key=f"edu_institution_{i}", 
                                   placeholder="e.g. University of Technology")
        year = st.text_input(f"Year", key=f"edu_year_{i}", 
                            placeholder="e.g. 2020-2024")
        details = st.text_area(f"Additional Details (Optional)", key=f"edu_details_{i}", 
                              placeholder="• GPA: 3.8/4.0\n• Relevant Coursework: Data Structures, Algorithms",
                              height=85)
        education_list.append((degree, institution, year, details))

# Projects (Dynamic)
st.sidebar.markdown("### 🚀 Projects")
num_proj = st.sidebar.number_input("Number of Projects", min_value=0, max_value=6, value=1, step=1)
projects_list = []

for i in range(num_proj):
    with st.sidebar.expander(f"Project #{i+1}"):
        proj_title = st.text_input(f"Project Title", key=f"proj_title_{i}", 
                                  placeholder="e.g. E-commerce Web Application")
        proj_link = st.text_input(f"Project Link (Optional)", key=f"proj_link_{i}", 
                                 placeholder="https://github.com/yourproject")
        proj_details = st.text_area(f"Description & Technologies", key=f"proj_details_{i}", 
                                   placeholder="• Built a full-stack e-commerce platform\n• Technologies: React, Node.js, MongoDB\n• Features: User authentication, payment integration",
                                   height=100)
        projects_list.append((proj_title, proj_link, proj_details))

# Certifications (Dynamic)
st.sidebar.markdown("### 📜 Certifications")
num_cert = st.sidebar.number_input("Number of Certifications", min_value=0, max_value=8, value=0, step=1)
certifications_list = []

for i in range(num_cert):
    with st.sidebar.expander(f"Certification #{i+1}"):
        cert_title = st.text_input(f"Certification Title", key=f"cert_title_{i}", 
                                  placeholder="e.g. AWS Certified Solutions Architect")
        cert_issuer = st.text_input(f"Issuing Organization", key=f"cert_issuer_{i}", 
                                   placeholder="e.g. Amazon Web Services")
        cert_date = st.text_input(f"Date Obtained", key=f"cert_date_{i}", 
                                 placeholder="e.g. March 2024")
        cert_link = st.text_input(f"Certificate Link (Optional)", key=f"cert_link_{i}", 
                                 placeholder="https://certificate-link.com")
        certifications_list.append((cert_title, cert_issuer, cert_date, cert_link))

# -------------------- Resume Preview --------------------
st.subheader("📄 Resume Preview")

if name:  # Only show preview if name is entered
    # Build preview markdown
    preview_parts = []
    
    # Header
    preview_parts.append(f"## {name}")
    
    contact_info = []
    if email:
        contact_info.append(f"📧 {email}")
    if phone:
        contact_info.append(f"📞 {phone}")
    if address:
        contact_info.append(f"📍 {address}")
    
    if contact_info:
        preview_parts.append(" | ".join(contact_info))
    
    links = []
    if linkedin:
        links.append(f"[LinkedIn]({linkedin})")
    if github:
        links.append(f"[GitHub]({github})")
    if portfolio_website:
        links.append(f"[Portfolio]({portfolio_website})")
    
    # Additional profiles section
    additional_links = []
    if kaggle:
        additional_links.append(f"[Kaggle]({kaggle})")
    if docker_hub:
        additional_links.append(f"[Docker Hub]({docker_hub})")
    if streamlit_profile:
        additional_links.append(f"[Streamlit]({streamlit_profile})")
    
    if links:
        preview_parts.append("🔗 " + " | ".join(links))
    
    if additional_links:
        preview_parts.append("💼 " + " | ".join(additional_links))
    
    preview_parts.append("---")
    
    # Define section order based on selection
    def get_sections_in_order():
        sections = []
        
        if section_order == "Traditional (Experience First)":
            order = ['summary', 'experience', 'education', 'skills', 'projects', 'certifications']
        elif section_order == "Recent Graduate (Education First)":
            order = ['summary', 'education', 'experience', 'skills', 'projects', 'certifications']
        elif section_order == "Tech-Focused (Skills First)":
            order = ['summary', 'skills', 'experience', 'projects', 'education', 'certifications']
        elif section_order == "Career Changer (Skills & Projects First)":
            order = ['summary', 'skills', 'projects', 'certifications', 'experience', 'education']
        else:  # Custom Order
            order = ['summary', 'skills', 'experience', 'education', 'projects', 'certifications']
        
        for section in order:
            if section == 'summary' and about:
                sections.append(('summary', "### 💭 Professional Summary", about, ""))
            elif section == 'skills' and skills:
                sections.append(('skills', "### 💻 Technical Skills", skills, ""))
            elif section == 'experience' and any(title or company for title, company, duration, details in work_experience_list):
                exp_content = []
                for title, company, duration, details in work_experience_list:
                    if title or company:
                        job_header = []
                        if title:
                            job_header.append(f"**{title}**")
                        if company:
                            job_header.append(f"at **{company}**")
                        if duration:
                            job_header.append(f"({duration})")
                        exp_content.append(" ".join(job_header))
                        if details:
                            exp_content.append(details)
                        exp_content.append("")
                sections.append(('experience', "### 💼 Work Experience", "\n".join(exp_content), ""))
            elif section == 'education' and any(degree or institution for degree, institution, year, details in education_list):
                edu_content = []
                for degree, institution, year, details in education_list:
                    if degree or institution:
                        edu_header = []
                        if degree:
                            edu_header.append(f"**{degree}**")
                        if institution:
                            edu_header.append(f"at **{institution}**")
                        if year:
                            edu_header.append(f"({year})")
                        edu_content.append(" ".join(edu_header))
                        if details:
                            edu_content.append(details)
                        edu_content.append("")
                sections.append(('education', "### 🎓 Education", "\n".join(edu_content), ""))
            elif section == 'projects' and any(proj_title for proj_title, proj_link, proj_details in projects_list):
                proj_content = []
                for proj_title, proj_link, proj_details in projects_list:
                    if proj_title:
                        if proj_link:
                            proj_content.append(f"**[{proj_title}]({proj_link})**")
                        else:
                            proj_content.append(f"**{proj_title}**")
                        if proj_details:
                            proj_content.append(proj_details)
                        proj_content.append("")
                sections.append(('projects', "### 🚀 Projects", "\n".join(proj_content), ""))
            elif section == 'certifications' and any(cert_title for cert_title, cert_issuer, cert_date, cert_link in certifications_list):
                cert_content = []
                for cert_title, cert_issuer, cert_date, cert_link in certifications_list:
                    if cert_title:
                        cert_header = []
                        if cert_link:
                            cert_header.append(f"**[{cert_title}]({cert_link})**")
                        else:
                            cert_header.append(f"**{cert_title}**")
                        if cert_issuer:
                            cert_header.append(f"- {cert_issuer}")
                        if cert_date:
                            cert_header.append(f"({cert_date})")
                        cert_content.append(" ".join(cert_header))
                        cert_content.append("")
                sections.append(('certifications', "### 📜 Certifications", "\n".join(cert_content), ""))
        
        return sections
    
    # Build preview with selected order
    sections = get_sections_in_order()
    for section_type, header, content, extra in sections:
        preview_parts.append(header)
        preview_parts.append(content)
        preview_parts.append("")
    
    # Display preview
    preview_md = "\n".join(preview_parts)
    st.markdown(preview_md)
else:
    st.info("👆 Please enter your name in the sidebar to see the resume preview.")

# -------------------- PDF Generation with Enhanced Formatting --------------------
def generate_professional_pdf(name, email, phone, address, linkedin, github, kaggle, docker_hub, 
                            streamlit_profile, portfolio_website, about, skills, 
                            work_experience_list, education_list, projects_list, certifications_list, section_order):
    
    class ProfessionalPDF(FPDF):
        def __init__(self):
            super().__init__()
            self.set_auto_page_break(auto=True, margin=15)
            
        def header(self):
            if self.page_no() > 1:
                self.set_font('Arial', 'B', 10)
                self.set_text_color(100, 100, 100)
                self.cell(0, 10, f'{name} - Resume', 0, 1, 'C')
                self.ln(5)
        
        def add_section_header(self, title):
            self.ln(3)
            self.set_font('Arial', 'B', 12)
            self.set_text_color(0, 51, 102)  # Professional blue
            self.cell(0, 8, title.upper(), 0, 1)
            self.set_draw_color(0, 51, 102)
            self.set_line_width(0.5)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(3)
            self.set_text_color(0, 0, 0)
        
        def add_text(self, text, bold=False, size=10):
            self.set_font('Arial', 'B' if bold else '', size)
            self.set_text_color(0, 0, 0)
            if text:
                # Handle bullet points and long URLs
                lines = text.split('\n')
                for line in lines:
                    if line.strip().startswith('•') or line.strip().startswith('-'):
                        self.multi_cell(0, 5, f"  {line.strip()}", 0, 'L')
                    else:
                        # Check if line contains URLs and is too long
                        if ('http' in line or 'www.' in line) and len(line) > 90:
                            self.multi_cell(0, 5, line.strip(), 0, 'L')
                        else:
                            self.multi_cell(0, 5, line.strip(), 0, 'L')
            self.ln(1)
        
        def add_url_safe(self, text, alignment='C'):
            """Add text with URL-safe formatting to prevent overflow"""
            self.set_font('Arial', '', 9)  # Slightly smaller font for URLs
            self.set_text_color(60, 60, 60)
            if len(text) > 95:  # If text is too long
                self.multi_cell(0, 5, text, 0, alignment)
            else:
                self.cell(0, 5, text, 0, 1, alignment)

    pdf = ProfessionalPDF()
    pdf.add_page()
    
    # Header with name
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 12, name.upper(), 0, 1, 'C')
    pdf.ln(2)
    
    # Contact information - Enhanced Layout
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(60, 60, 60)
    
    # Address on separate line if provided
    if address:
        pdf.cell(0, 5, address, 0, 1, 'C')
    
    # Email and phone on same line
    contact_details = []
    if email:
        contact_details.append(f"Email: {email}")
    if phone:
        contact_details.append(f"Phone: {phone}")
    
    if contact_details:
        pdf.cell(0, 5, " | ".join(contact_details), 0, 1, 'C')
    
    # Primary professional links
    primary_links = []
    if linkedin:
        primary_links.append(f"LinkedIn: {linkedin}")
    if github:
        primary_links.append(f"GitHub: {github}")
    if portfolio_website:
        primary_links.append(f"Portfolio: {portfolio_website}")
    
    # Handle long URLs by splitting them across lines if necessary
    if primary_links:
        combined_primary = " | ".join(primary_links)
        # Check if the combined line is too long (approximate check)
        if len(combined_primary) > 95:  # Rough character limit for PDF width
            # Split into separate lines
            for link in primary_links:
                pdf.add_url_safe(link, 'C')
        else:
            pdf.cell(0, 5, combined_primary, 0, 1, 'C')
    
    # Additional professional profiles - always on separate lines to prevent overflow
    if kaggle:
        pdf.add_url_safe(f"Kaggle: {kaggle}", 'C')
    if docker_hub:
        pdf.add_url_safe(f"Docker Hub: {docker_hub}", 'C')
    if streamlit_profile:
        pdf.add_url_safe(f"Streamlit: {streamlit_profile}", 'C')
    
    pdf.ln(5)
    
    # Apply same section ordering to PDF
    def add_pdf_sections():
        if section_order == "Traditional (Experience First)":
            order = ['summary', 'experience', 'education', 'skills', 'projects', 'certifications']
        elif section_order == "Recent Graduate (Education First)":
            order = ['summary', 'education', 'experience', 'skills', 'projects', 'certifications']
        elif section_order == "Tech-Focused (Skills First)":
            order = ['summary', 'skills', 'experience', 'projects', 'education', 'certifications']
        elif section_order == "Career Changer (Skills & Projects First)":
            order = ['summary', 'skills', 'projects', 'certifications', 'experience', 'education']
        else:  # Custom Order
            order = ['summary', 'skills', 'experience', 'education', 'projects', 'certifications']
        
        for section in order:
            if section == 'summary' and about:
                pdf.add_section_header("Professional Summary")
                pdf.add_text(about, size=10)
            elif section == 'skills' and skills:
                pdf.add_section_header("Technical Skills")
                pdf.add_text(skills, size=10)
            elif section == 'experience' and any(title or company for title, company, duration, details in work_experience_list):
                pdf.add_section_header("Work Experience")
                for title, company, duration, details in work_experience_list:
                    if title or company:
                        job_line = []
                        if title:
                            job_line.append(title)
                        if company:
                            job_line.append(f"at {company}")
                        if duration:
                            job_line.append(f"({duration})")
                        pdf.add_text(" ".join(job_line), bold=True, size=11)
                        if details:
                            pdf.add_text(details, size=10)
            elif section == 'education' and any(degree or institution for degree, institution, year, details in education_list):
                pdf.add_section_header("Education")
                for degree, institution, year, details in education_list:
                    if degree or institution:
                        edu_line = []
                        if degree:
                            edu_line.append(degree)
                        if institution:
                            edu_line.append(f"at {institution}")
                        if year:
                            edu_line.append(f"({year})")
                        pdf.add_text(" ".join(edu_line), bold=True, size=11)
                        if details:
                            pdf.add_text(details, size=10)
            elif section == 'projects' and any(proj_title for proj_title, proj_link, proj_details in projects_list):
                pdf.add_section_header("Projects")
                for proj_title, proj_link, proj_details in projects_list:
                    if proj_title:
                        if proj_link:
                            pdf.add_text(f"{proj_title} ({proj_link})", bold=True, size=11)
                        else:
                            pdf.add_text(proj_title, bold=True, size=11)
                        if proj_details:
                            pdf.add_text(proj_details, size=10)
            elif section == 'certifications' and any(cert_title for cert_title, cert_issuer, cert_date, cert_link in certifications_list):
                pdf.add_section_header("Certifications")
                for cert_title, cert_issuer, cert_date, cert_link in certifications_list:
                    if cert_title:
                        cert_line = [cert_title]
                        if cert_issuer:
                            cert_line.append(f"- {cert_issuer}")
                        if cert_date:
                            cert_line.append(f"({cert_date})")
                        cert_text = " ".join(cert_line)
                        if cert_link:
                            cert_text += f" - {cert_link}"
                        pdf.add_text(cert_text, bold=True, size=10)
    
    add_pdf_sections()
    
    # Save PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        return tmp_file.name

# -------------------- Generate and Download PDF --------------------
if 'pdf_file' not in st.session_state:
    st.session_state['pdf_file'] = None

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🎯 Generate Professional PDF", type="primary", use_container_width=True):
        if not name:
            st.error("Please enter your name to generate the resume.")
        else:
            with st.spinner("Generating your professional resume..."):
                try:
                    pdf_path = generate_professional_pdf(
                        name, email, phone, address, linkedin, github, kaggle, docker_hub,
                        streamlit_profile, portfolio_website, about, skills,
                        work_experience_list, education_list, projects_list, certifications_list, section_order
                    )
                    st.session_state['pdf_file'] = pdf_path
                    st.success("✅ Resume generated successfully!")
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")

with col2:
    if st.session_state['pdf_file']:
        try:
            with open(st.session_state['pdf_file'], "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="📥 Download Resume PDF",
                data=pdf_bytes,
                file_name=f"{name.replace(' ', '_')}_Resume.pdf" if name else "resume.pdf",
                mime="application/pdf",
                type="secondary",
                use_container_width=True
            )
        except Exception as e:
            st.error("Error preparing download. Please regenerate the PDF.")

# -------------------- Tips Section --------------------
st.markdown("---")
st.subheader("💡 ATS Optimization Tips")

tips_col1, tips_col2 = st.columns(2)

with tips_col1:
    st.markdown("""
    **📝 Content Tips:**
    - Use action verbs (developed, implemented, managed)
    - Quantify achievements with numbers and percentages
    - Include relevant keywords from job descriptions
    - Keep bullet points concise and impactful
    """)

with tips_col2:
    st.markdown("""
    **🎯 ATS-Friendly Format:**
    - Simple, clean formatting without graphics
    - Standard section headings (Experience, Education, Skills)
    - Consistent font and spacing
    - Professional profiles (Kaggle, Docker, Streamlit) are ATS-readable
    - Section order doesn't affect ATS parsing
    """)

# Section Order Guide
st.markdown("### 📋 When to Use Each Layout:")
layout_col1, layout_col2 = st.columns(2)

with layout_col1:
    st.markdown("""
    **Traditional Layout:**
    - 3+ years work experience
    - Career progression to highlight
    - Applying to traditional industries
    
    **Recent Graduate Layout:**
    - New graduates or career changers
    - Strong educational background
    - Limited work experience
    
    **Career Changer Layout:**
    - Transitioning between industries/roles
    - Emphasizing transferable skills
    - Showcasing relevant projects & certifications
    """)

with layout_col2:
    st.markdown("""
    **Tech-Focused Layout:**
    - Technical roles (developer, engineer)
    - Skills-based hiring
    - Portfolio/project-heavy roles
    
    **Custom Layout:**
    - Unique career situations
    - Specific employer requirements
    - Creative or consulting roles
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.8em;'>"
    "💼 Professional Resume Builder – Created with ❤️ by Waseem and 🤖 Claude AI"
    "</div>", 
    unsafe_allow_html=True
)