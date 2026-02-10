"""
Sample Document Generator
Creates sample university PDF documents for testing the FAQ chatbot
Run this if you don't have real university documents
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch


# Sample content for university documents
STUDENT_HANDBOOK = """
UNIVERSITY STUDENT HANDBOOK
Academic Year 2025-2026

TABLE OF CONTENTS
1. Welcome Message
2. Admission Requirements
3. Academic Policies
4. Student Services
5. Campus Life

1. WELCOME MESSAGE

Welcome to our university! This handbook provides essential information for students.

2. ADMISSION REQUIREMENTS

Undergraduate Admission:
- High school diploma or equivalent
- Minimum GPA of 3.0
- SAT score of 1200+ or ACT score of 24+
- Two letters of recommendation
- Personal statement (500-750 words)
- Application fee: $75

International Students:
- All of the above requirements
- TOEFL score of 80+ or IELTS 6.5+
- Proof of financial support
- Valid passport

Application Deadlines:
- Fall Semester: January 15
- Spring Semester: September 15
- Early Decision: November 1

3. ACADEMIC POLICIES

Grading System:
- A: 90-100 (Excellent)
- B: 80-89 (Good)
- C: 70-79 (Satisfactory)
- D: 60-69 (Poor)
- F: Below 60 (Fail)

GPA Calculation:
- A = 4.0, B = 3.0, C = 2.0, D = 1.0, F = 0.0
- Minimum GPA for good standing: 2.0

Academic Probation:
Students with GPA below 2.0 are placed on academic probation and must:
- Meet with academic advisor monthly
- Limit course load to 12 credits
- Participate in tutoring programs

Graduation Requirements:
- Complete minimum 120 credit hours
- Maintain cumulative GPA of 2.0 or higher
- Complete all major requirements
- Satisfy general education requirements
- Final semester must be completed in residence

4. STUDENT SERVICES

Academic Advising:
- Available Monday-Friday, 9 AM - 5 PM
- Schedule appointments through student portal
- Walk-ins accepted during open hours

Library Services:
- Open 24/7 during academic year
- Extensive digital resources
- Study rooms available for reservation
- Research assistance available

Career Services:
- Resume writing workshops
- Mock interviews
- Job fairs (Fall and Spring)
- Internship placement assistance

5. CAMPUS LIFE

Housing:
- On-campus housing available for all students
- Residence halls and apartments
- Housing application deadline: May 1

Dining:
- Multiple dining halls across campus
- Meal plans required for on-campus residents
- Various dietary options available

Student Organizations:
- Over 200 student clubs
- Academic, cultural, and recreational organizations
- Leadership opportunities available
"""

COURSE_CATALOG = """
COURSE CATALOG
Academic Year 2025-2026

COMPUTER SCIENCE DEPARTMENT

CS 101 - Introduction to Programming (4 credits)
Prerequisites: None
Introduction to programming using Python. Topics include variables, control structures, 
functions, and basic data structures.

CS 201 - Data Structures (4 credits)
Prerequisites: CS 101
Study of fundamental data structures including arrays, linked lists, stacks, queues, 
trees, and graphs. Implementation and analysis of algorithms.

CS 301 - Database Systems (4 credits)
Prerequisites: CS 201
Design and implementation of database systems. Topics include relational model, SQL, 
normalization, and transaction management.

CS 401 - Artificial Intelligence (4 credits)
Prerequisites: CS 201, MATH 220
Introduction to AI concepts including search algorithms, machine learning, and 
neural networks.

MATHEMATICS DEPARTMENT

MATH 101 - Calculus I (4 credits)
Prerequisites: High school algebra and trigonometry
Limits, continuity, derivatives, and applications of derivatives.

MATH 102 - Calculus II (4 credits)
Prerequisites: MATH 101
Integration techniques, applications of integration, and sequences and series.

MATH 220 - Linear Algebra (3 credits)
Prerequisites: MATH 101
Matrices, vector spaces, linear transformations, and eigenvalues.

BUSINESS DEPARTMENT

BUS 101 - Introduction to Business (3 credits)
Prerequisites: None
Overview of business fundamentals including management, marketing, and finance.

BUS 301 - Marketing Management (3 credits)
Prerequisites: BUS 101
Principles of marketing, consumer behavior, and marketing strategies.

GENERAL EDUCATION REQUIREMENTS

All students must complete:
- English Composition (6 credits)
- Mathematics (6 credits)
- Natural Sciences (8 credits)
- Social Sciences (6 credits)
- Humanities (6 credits)
- Arts (3 credits)

Total General Education: 35 credits
"""

ACADEMIC_POLICIES = """
ACADEMIC POLICIES AND PROCEDURES

1. REGISTRATION

Course Registration:
- Registration opens 2 weeks before semester start
- Students register based on credit hours completed
- Maximum course load: 18 credits per semester
- Minimum for full-time status: 12 credits

Add/Drop Period:
- First week of semester: Add or drop without penalty
- Second week: Drop with "W" on transcript
- After second week: Withdrawal requires approval

2. ATTENDANCE POLICY

Class Attendance:
- Students expected to attend all classes
- Absence may affect grade at instructor's discretion
- More than 3 unexcused absences may result in course failure
- Medical absences require documentation

3. GRADING POLICIES

Grade Appeals:
- Students may appeal grades within 30 days of posting
- Must first discuss with course instructor
- If unresolved, submit written appeal to department chair

Incomplete Grades:
- Granted only for documented emergencies
- Must be completed within one semester
- Reverts to F if not completed

4. ACADEMIC INTEGRITY

Plagiarism:
- Presenting others' work as your own
- First offense: Zero on assignment and disciplinary probation
- Second offense: Course failure and suspension

Cheating:
- Using unauthorized materials during exams
- Penalties same as plagiarism

5. REFUND POLICY

Tuition Refunds:
- Before semester starts: 100% refund
- Week 1: 90% refund
- Week 2: 75% refund
- Week 3: 50% refund
- Week 4: 25% refund
- After Week 4: No refund

6. LEAVE OF ABSENCE

Students may request leave of absence for:
- Medical reasons
- Family emergencies
- Military service
- Study abroad

Maximum leave period: 2 semesters
Must reapply for readmission after leave
"""

ACADEMIC_CALENDAR = """
ACADEMIC CALENDAR
2025-2026

FALL SEMESTER 2025

August 25, 2025 - Fall semester begins
August 25-31 - Add/Drop period
September 7 - Labor Day (University closed)
October 19-20 - Fall break
November 24-28 - Thanksgiving break
December 15-19 - Final exams
December 20 - Fall semester ends
December 21 - Grades due

SPRING SEMESTER 2026

January 11, 2026 - Spring semester begins
January 11-17 - Add/Drop period
January 18 - Martin Luther King Jr. Day (University closed)
March 9-13 - Spring break
April 10 - Good Friday (University closed)
May 4-8 - Final exams
May 9 - Spring semester ends
May 10 - Grades due
May 16 - Commencement ceremony

SUMMER SESSION 2026

May 25, 2026 - Summer Session I begins
June 26 - Summer Session I ends
July 6 - Summer Session II begins
August 14 - Summer Session II ends

IMPORTANT DEADLINES

Fall 2025:
- Application deadline: January 15, 2025
- Housing application: May 1, 2025
- Financial aid priority deadline: March 1, 2025
- Registration begins: August 1, 2025

Spring 2026:
- Application deadline: September 15, 2025
- Housing application: November 1, 2025
- Financial aid deadline: October 1, 2025
- Registration begins: December 1, 2025

ACADEMIC HOLIDAYS

Labor Day - September 7, 2025
Fall Break - October 19-20, 2025
Thanksgiving - November 24-28, 2025
Winter Break - December 21, 2025 - January 10, 2026
Martin Luther King Jr. Day - January 18, 2026
Spring Break - March 9-13, 2026
Good Friday - April 10, 2026
Summer Break - May 10 - May 24, 2026
"""


def create_pdf(filename, title, content, output_dir):
    """Create a PDF document with the given content"""
    
    filepath = output_dir / filename
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Container for content
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='navy',
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Add title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Add content
    for line in content.strip().split('\n'):
        if line.strip():
            para = Paragraph(line, styles['Normal'])
            story.append(para)
            story.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Created: {filename}")


def main():
    """Generate sample university PDF documents"""
    
    print("\n" + "="*60)
    print("📄 SAMPLE DOCUMENT GENERATOR")
    print("="*60 + "\n")
    
    # Get output directory
    script_dir = Path(__file__).parent
    output_dir = script_dir / "data" / "pdfs"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Output directory: {output_dir}\n")
    print("Generating sample PDFs...\n")
    
    # Check if reportlab is installed
    try:
        import reportlab
    except ImportError:
        print("❌ Error: reportlab not installed")
        print("\nTo install reportlab, run:")
        print("   pip install reportlab")
        return
    
    # Create PDFs
    documents = [
        ("student_handbook.pdf", "Student Handbook", STUDENT_HANDBOOK),
        ("course_catalog.pdf", "Course Catalog", COURSE_CATALOG),
        ("academic_policies.pdf", "Academic Policies", ACADEMIC_POLICIES),
        ("academic_calendar.pdf", "Academic Calendar", ACADEMIC_CALENDAR),
    ]
    
    for filename, title, content in documents:
        create_pdf(filename, title, content, output_dir)
    
    print("\n" + "="*60)
    print("✅ SAMPLE DOCUMENTS CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📊 Generated {len(documents)} PDF documents")
    print(f"📍 Location: {output_dir}")
    print("\n✨ You can now run: python backend/ingest.py\n")


if __name__ == "__main__":
    main()
