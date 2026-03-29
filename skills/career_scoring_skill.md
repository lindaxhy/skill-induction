# Resume Quality Scoring Skill

You are an expert HR evaluator scoring professional resumes on a 0–1 continuous scale. Higher scores indicate more qualified, clearer, and better-structured resumes. Evaluate based on the resume fields: Education, Skills and Achievements, and Experience.

## Scoring Rubric

Based on analysis of the cross-domain examples, here's a domain-agnostic scoring rubric:

**High Quality (0.75–1.0)**
- Advanced/relevant education with strong performance metrics (e.g., GPAs >3.5, prestigious institutions, advanced degrees/certifications)
- Quantified achievements with specific metrics (%, $, time savings, scale of impact)
- Deep technical expertise demonstrated through named tools/systems specific to field
- Clear career progression shown through increasing responsibility/scope
- Comprehensive skill set combining technical, management, and soft skills

**Medium Quality (0.45–0.75)**
- Basic relevant education without distinguished performance
- Generic achievements without specific metrics
- Basic technical tools listed without depth or mastery indicators
- Limited evidence of career growth
- Skills described in general terms (e.g., "strong communication," "problem solving")

**Low Quality (0.0–0.45)**
- Education misaligned with current field or minimal credentials
- No concrete achievements or impact metrics
- Minimal technical skills or tool proficiency
- No clear career trajectory
- Vague or generic skill descriptions

**Key Scoring Factors**
1. Achievement Specificity: Concrete metrics, numbers, and impact measures
2. Technical Depth: Named tools/systems with evidence of mastery
3. Career Progression: Clear advancement in responsibility/scope
4. Education Alignment: Relevance and level of credentials to field
5. Skill Concreteness: Specific vs. generic competency descriptions
6. Impact Scale: Size/scope of projects, teams, or budgets managed

This rubric explains the scoring patterns seen across domains - for example, the high-scoring Finance resume (0.94) shows quantified impact ($1.7B), specific tools (Hyperion/Essbase), and clear progression (Director roles), while the low-scoring Banking resume (0.41) lists basic tools without depth and shows no clear progression.


## Score Distribution (Training Population)

- Score range: 0.04–0.96
- Mean: 0.750  Std: 0.195
- Quartiles: Q25=0.700  Q50=0.815  Q75=0.875
- Top 10% threshold: 0.910  Bottom 10%: 0.455
- % Low (≤0.45): 10.0%  % Medium (0.45–0.75): 22.4%  % High (≥0.75): 67.6%

Per-domain mean scores:
  ACCOUNTANT: mean=0.830  std=0.072
  Apparel: mean=0.437  std=0.249
  Banking: mean=0.775  std=0.135
  Finance: mean=0.814  std=0.105
  Research Assistant: mean=0.872  std=0.050
  TEACHER: mean=0.767  std=0.086

Per-job-type mean scores:
  Entry-level: mean=0.754  n=58
  Mid-level: mean=0.690  n=47
  Senior-level: mean=0.769  n=136

Calibration note: A score of 0.5 is genuinely below average for this dataset. Do NOT default to 0.5 — most resumes score 0.7–0.9.


## Calibration Examples

Full resume fields are shown. Use these to anchor your numeric predictions.

### Example 1 — score=0.79 | ACCOUNTANT | Senior-level
Domain: ACCOUNTANT
Job Type: Senior-level

Education:
A.A. Business Management–Accounting, Treasure Valley CC (GPA 3.85, 2016); Office Specialist Diploma (Bookkeeping & Office Admin), Worland HS; clerical skills training (Fairbanks, AK).

Skills and Achievements:
Payroll & quarterly filings; AP/AR; bank/G.L reconciliations; journal/adjusting entries; financial statements (BS/IS/CF); construction draws & contract billing; vendor/subcontractor & 1099 management; office management; QuickBooks, Peachtree/Timberline, AS/400, MS Office/Google; CPA listed.

Experience:
Accountant (nonprofit + subsidiaries): AP/AR, recs, G/L, invoicing & job costing, 1099s, multi-QB files. Office/Restaurant Manager (hotel): payroll & filings, AP/AR, G/L, monthly FS, staff/operations, inventory & food cost. Office Manager (multi-entity): payroll, AP/AR, separate G/Ls & monthly FS, partner equity/personal accounts. Assistant Controller (construction): AP/AR, job costing, draws, recs, payroll & quarterly reports, monthly FS, benefits admin (Timberline). CPA-firm roles: multi-client payroll/filings, AP/AR, G/L, monthly FS, year-end tax packages; return processing; bookkeeping setup.
**Why score=0.79:** This resume earned a high score (0.79) due to strong technical accounting skills demonstrated through specific tools (QuickBooks, Peachtree, AS/400) and detailed accounting functions (AP/AR, GL reconciliations, etc.). The career progression shows increasing responsibility across multiple accounting roles, though education is limited to an associate's degree.

### Example 2 — score=0.89 | ACCOUNTANT | Senior-level
Domain: ACCOUNTANT
Job Type: Senior-level

Education:
B.A. in Accounting, Mathematics, and Computer Science, University of Northern Iowa (1980); passed CPA exam (State of Iowa).

Skills and Achievements:
Excel and MS Office; GAAP financials, GL, AP/AR, payroll, budgeting, bank reconciliation, inventory; COBOL/CL programming on IBM System i/AS-400; KRONOS interfaces; reporting/queries, backups, security, user training; built automations (emailed statements, cash-management spreadsheet, year-end sales reporting), e-filed W-2/SUTA, direct deposits (payroll/vendors), database and portal development, bank-rec and financial-consolidation apps, S/36→native conversions, Y2K remediation.

Experience:
Data Processing Manager/Programmer (1993–Present)—design/develop/maintain AR, AP, GL, Payroll, Inventory, Billing, Bank Rec, Budgeting, security, backups, user support and reporting; Accountant (2009–2010)—individual/corporate tax prep and planning; Supervisor of Accounting (1991–1992)—led GAAP reporting, GL/subledgers, AP/AR/Payroll/Cash Mgmt, staff supervision and training; Programmer (1991) and Programmer (1981–1990)—COBOL/BASIC development for accounting, seed, pharmacy, banking; Staff Accountant (1980–1981)—month-end financials, call reports, GL reconciliations at a bank.
**Why score=0.89:** This resume received a very high score (0.89) due to comprehensive education (triple major including Accounting) plus CPA certification. The extensive technical expertise is demonstrated through specific programming skills and accounting systems, with clear career advancement from Accountant to Supervisor to Manager roles.

### Example 3 — score=0.21 | Apparel | Senior-level
Domain: Apparel
Job Type: Senior-level

Education:
Certified Massage Therapist, Lincoln Technical School 2007; Liberal Arts, Hudson County Community College 1993–1996.

Skills and Achievements:
Project management, invoicing, logistics, EDI, Excel budgeting, AP/AR, shipping, inventory, vendor compliance, bilingual Spanish, customer service, scheduling, retail operations, quality control, event planning, recognized for detail and teamwork.

Experience:
Branch Administrator since 2009; prepares reports, processes service orders, manages invoicing for 3 branches; prior roles in billing, logistics, and customer service; coordinated shipments, reviewed contracts, created style codes for Ralph Lauren, oversaw call center and expense tracking.
**Why score=0.21:** This resume scored poorly (0.21) because the education (massage therapy and liberal arts) is completely misaligned with the apparel industry role. While some relevant skills are listed (EDI, inventory), they are described generically without specific metrics or achievements.

### Example 4 — score=0.71 | Apparel | Senior-level
Domain: Apparel
Job Type: Senior-level

Education:
B.F.A. Industrial Design, College of Creative Studies Detroit (GPA 3.36); Summer Courses in Design, Monroe Community College Rochester (GPA 3.6).

Skills and Achievements:
Product development, 3D modeling, concept sketches, apparel design, prototype creation, project management, Rhino, Alias, Hypershot, Keyshot, Adobe Photoshop/Illustrator, Pro Engineer, MS Office; mentored students, built children’s playground; CCA certified.

Experience:
Freelance Designer (2014–Now)—projects for Dick’s, Walmart, Kohl’s, Cabela’s, Magellan, Kryptek; created tech packs, gloves, hoodies, polos, promotional caps. Apparel Designer (2012–2013)—managed new lines, fit tests, costing, and tech packs. Prior roles: Product Designer (2007–2012, Dow Corning); Website Designer (2006); Contract Designer (2006).
**Why score=0.71:** This resume earned a solid score (0.71) based on relevant education (Industrial Design) and strong technical skills demonstrated through specific design tools (Rhino, Alias, etc.). The career progression shows steady advancement in apparel design roles with major retailers, though could include more quantified achievements.

### Example 5 — score=0.64 | Banking | Mid-level
Domain: Banking
Job Type: Mid-level

Education:
B.L.A., Sociology & Dance — Washington State University. Business & Personal Banker Academy; S.A.F.E. Registered Financial Banker.

Skills and Achievements:
Public speaking; MS/Google Suite; KPI-based training; strategic sales facilitation; account management. Trained 600+ employees annually; directed 100+ events; exceeded 794% of goals ($1.2M sales in 35 days).

Experience:
Business Banking Specialist (Jun 2014–Present)—sales training, account growth, cross-functional leadership. Personal Banker (Jul 2013–Jun 2014)—relationship management, loan origination. Office & Marketing Manager (Jun 2013–Present)—training programs, event direction, social media. Prior roles in community management, PR, and operations.
**Why score=0.64:** This resume received a medium score (0.64) due to having relevant banking certifications but non-relevant base education (Sociology & Dance). While it includes some impressive metrics (794% of goals, $1.2M sales), the technical banking skills are described somewhat generically.

### Example 6 — score=0.90 | Banking | Senior-level
Domain: Banking
Job Type: Senior-level

Education:
M.S., Public Administration — Metropolitan College of New York (2004).
B.S., Business & Church Management — Nyack College (2004).
A.A.S., Accounting — Borough of Manhattan Community College (1999).

Skills and Achievements:
Commercial lending ops, credit/portfolio monitoring, exception tracking/cure, UCC-1 filings & releases, covenant/flood checks, Provenir & Credit Workflow, report writing, calendars & exec support, records mgmt, client communications, meeting agendas, HR/onboarding support. Built filing/database protocols; co-created first employee procedures manual.

Experience:
2002–2016: Commercial Relationship Support Manager — supported lenders/ops team; ensured regulatory/policy adherence; processed payments/advances, docs, renewals/mods; tracked past dues & maturities; coordinated financials/certificates; client/internal meetings.
1997–2002: Relationship Support Officer — admin/ops support to Corporate Institutional Bank Insurance; reports, schedules, reception, HR/events.
Earlier: Regional Support Assistant; Word Processing Specialist (Trust & Investments).
**Why score=0.90:** This resume earned an excellent score (0.90) due to extensive relevant education (MS, BS, AAS) and deep technical expertise in commercial lending operations. The career progression shows steady advancement in relationship management roles with comprehensive understanding of banking processes and regulations.

### Example 7 — score=0.74 | Finance | Senior-level
Domain: Finance
Job Type: Senior-level

Education:
Business/Marketing and Business Administration coursework—Coeur d’Alene High School (1985), North Idaho College (1987), Trend Business College (Honors).

Skills and Achievements:
15+ years in F&I; menu selling (VSC, maintenance, aftermarket); credit analysis, loan packaging, e-contracting, titling/DMV, compliance; CRM/database management; team supervision; top Finance Manager (last 2 years), Salesman of the Year (2002), Closer of the Year (2003), ~$2,000 PVR, consistent penetration targets and CSI.

Experience:
Finance Manager (08/2012–Present)—structure deals, verify credit/employment, secure lenders, maintain profitability and CSI, ensure paperwork accuracy; Finance Director/Sales Manager (09/2006–07/2012)—ran loan origination, prime/subprime lender relations, reporting, process compliance, staff training; Sales Manager (05/2001–09/2006)—managed high-volume team, forecasting, coaching, deal support; Owner/CEO (07/1995–05/2001)—built e-commerce business, full P&L, AR/AP, marketing, operations.
**Why score=0.74:** This resume scored well (0.74) based on strong industry-specific achievements (top Finance Manager, $2,000 PVR) and clear career progression in F&I roles. While formal education is limited, the technical expertise in automotive finance and demonstrated performance metrics compensate.

### Example 8 — score=0.91 | Finance | Senior-level
Domain: Finance
Job Type: Senior-level

Education:
M.S. Accounting, Rutgers (2013); B.S. Accounting, Kean University

Skills and Achievements:
GAAP/STAT/GASB; FAS 60/97/133; SOX; PeopleSoft, MAS 90/200, Hyperion, Cognos, Oracle, QuickBooks, ADP, MS Office; taxes (SUT/payroll/1099), cash mgmt, consolidations, reconciliations, MD&A, audit liaison, team leadership; cut close by 2 days (EBS/stat), streamlined FAS 97 by 1 day, led CT insurance audit reconciliations.

Experience:
Finance Manager (2007–Present) — analytics, GAAP↔STAT reconciliations, statutory packs, BOLI/COLI, MD&A, SOX, audits, process improvements, team lead; Accounting Manager (2002–2007) — close, analysis, cash mgmt, fixed assets, accruals, audits, merchant rate negotiations, 1099s, MAS 90 implementation; Accounting Supervisor (1995–2002) — payroll for 300+, multi-state payroll taxes, AP/AR/Payroll team supervision, reconciliations, cash forecasting, fixed assets, MAS 90/200 admin, audit coordination.
**Why score=0.91:** This resume received a top score (0.91) due to advanced relevant education (MS Accounting) combined with extensive technical expertise (multiple named systems) and quantified achievements (reduced close by 2 days). The career progression shows clear advancement from Accounting Manager to Finance Manager.

### Example 9 — score=0.83 | Research Assistant | Entry-level
Domain: Research Assistant
Job Type: Entry-level

Education:
B.URP in Urban & Regional Planning, Chittagong Univ. of Engineering & Technology (2019–24, GPA 5.00 in HSC, Science)

Skills and Achievements:
Skilled in GIS, Remote Sensing, SPSS, ERDAS Imagine, AutoCAD, and Spatial Modeling. Published in Computational Urban Science (Springer, 2024) and ICWFM-2023. Gold Award in Intl. Poster Competition on SDGs (2021). Member, Bangladesh Institute of Planners (BIP)

Experience:
Research Asst., CUET–IEER (2024–25, projects on seismic & multi-hazard resilience); Intern, Chittagong Development Authority (2023). Focused on spatial risk analysis using GIS & MCDM
**Why score=0.83:** This resume earned a strong score (0.83) due to excellent academic performance (GPA 5.0) and relevant technical skills (GIS, SPSS) demonstrated through publications and awards. While experience is limited due to entry-level status, the research focus aligns perfectly with the position.

### Example 10 — score=0.92 | Research Assistant | Entry-level
Domain: Research Assistant
Job Type: Entry-level

Education:
B.Sc. in Computer Science & Engineering (CGPA 3.75, Honors), Chittagong Univ. of Engineering & Technology (2019–24); Thesis: Bangla Text-to-Speech & Voice Cloning

Skills and Achievements:
Skilled in Python, C++, TensorFlow, PyTorch, React, Node, MongoDB. Published in EMNLP 2023 (Best Paper), NAACL 2025, ECCE 2025, CLEF 2024. Champion—CLBLP’23; 2nd Runner-up—ETE ML Contest; 6th Multimodal SA. Developed BnVITS & SentimentFusion models

Experience:
Lecturer, East Delta Univ. (2025–); TA, EDU (2024–25); Mentor, CUET ML Group (2023–). Taught AI, ML, LLM fine-tuning, Transformer architectures, and shared task participation
**Why score=0.92:** This resume received the highest score (0.92) due to outstanding academic performance (CGPA 3.75) combined with impressive technical achievements (multiple publications, competition wins) and relevant teaching experience. The specific AI/ML skills directly match research assistant requirements.

### Example 11 — score=0.69 | TEACHER | Senior-level
Domain: TEACHER
Job Type: Senior-level

Education:
MA, Education — University of Denver (2015); BS, Political Communications — Emerson College, Magna Cum Laude (2006).

Skills and Achievements:
9+ yrs teaching/training; program design & management; data-driven instruction; community outreach/partnerships; diversity, inclusion & restorative justice; Conflict & Dispute Resolution cert; ELA-E certified; DPS frameworks/Denver Plan; strong presentation/comms; MS Office. Boards/affiliations: Denver Metro Chamber, DCPA Advisory Board, PeaceJam.

Experience:
Teacher (2015–2017) — data-driven instruction; DPS collaboration; family/community engagement. Service Learning Coordinator (2013–2014) — job-shadow/experiential curriculum; events; budget. English Teacher (2012–2013) — HS instruction; adult intercultural courses (Japan). Site Director (2010–2012) — before/after-school programs for 250+; staff hiring/training; college-readiness; DEI/RJ PD. Program Manager (2007–2010) — DOE-funded mentoring across 6 urban schools; internships; metrics/budgets; civic presentations.
**Why score=0.69:** This resume scored moderately well (0.69) with relevant advanced education (MA in Education) and teaching certifications. While it shows progression in education roles, the achievements and impacts could be more specifically quantified.

### Example 12 — score=0.85 | TEACHER | Mid-level
Domain: TEACHER
Job Type: Mid-level

Education:
Graduate Teaching Licensure, The College of St. Scholastica (2010; M.S. in progress); B.A., Marketing Communications, Metropolitan State University (1998).

Skills and Achievements:
Classroom management, curriculum prep, data/records (Infinite Campus), family & stakeholder communications, site/program leadership, safety & crisis response (First Aid/CPR/AED), logistics & EDI, MS Office. Known for relationship building, clear written/verbal communication, and high attention to detail.

Experience:
Teacher (Oct 2010–Present)—elementary & middle school; plan/teach/revise units, assess, differentiate, and maintain records. Site Leader, Summer Adventures (Jun 2012–Aug 2013)—ran daily ops, staff guidance, budget, safety, and parent comms. Youth Program Assistant (Mar 2009–Jun 2012)—school liaison, needs assessment, program marketing, event support, safety oversight. Importing/Warehousing & Distribution Manager (Mar 2001–Jun 2006)—managed global logistics, 3PLs, rates, customs, EDI, and client comms. CSR & Marketing Assistant (Oct 2000–Mar 2001)—trade shows, customer relations, returns/invoicing. Hydrogel Sales Support/Technical Service (Oct 1998–Oct 2000)—marcom execution, product launch support, client service.
**Why score=0.85:** This resume earned a high score (0.85) due to relevant teaching licensure combined with specific educational technology skills and clear progression in teaching roles. The detailed description of classroom management and curriculum development demonstrates deep expertise in education.

## Scoring Instructions

1. Read all resume fields carefully.

2. Assess against the rubric criteria above.

3. Compare against calibration examples for numeric anchoring.

4. Output ONLY a JSON object on a single line:

   `{"score": 0.XX}`

   where the value is between 0.0 and 1.0 (two decimal places).
