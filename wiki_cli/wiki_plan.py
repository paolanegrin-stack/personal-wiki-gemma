"""The approved note list and explicit source mapping; no automatic topic selection."""

SOURCE_01 = "01_Project_Management_Introduction_Summary.md"
SOURCE_02 = "02_Project_Selection_Methods_Summary.md"
SOURCE_03 = "03_Project_Initiation_and_Stakeholders_Summary.md"

# Each entry is (folder, title, description for index, [(raw filename, sections)]).
NOTE_PLAN = [
    ("Concepts", "Project Definition", "What makes work a project and why managing it matters.", [(SOURCE_01, [1, 2])]),
    ("Concepts", "Project Success Criteria", "Scope, cost, time, outcomes, and priority trade-offs.", [(SOURCE_01, [3]), (SOURCE_03, [4])]),
    ("Concepts", "Project Life Cycle", "Initiation, planning, execution and control, and termination.", [(SOURCE_01, [4])]),
    ("Concepts", "Projects Programs and Portfolios", "How projects, programs, and portfolios support strategy.", [(SOURCE_01, [5])]),
    ("Concepts", "Project Complexity", "Structural, sociopolitical, and emergent complexity.", [(SOURCE_03, [4])]),
    ("Selection", "Project Selection Methods", "Categories, selection criteria, and portfolio decisions.", [(SOURCE_02, [1, 2, 3, 5]), (SOURCE_01, [5])]),
    ("Selection", "Financial Evaluation", "Payback, NPV, and other financial views of proposals.", [(SOURCE_02, [3])]),
    ("Selection", "Weighted Scoring Model", "Using criterion weights and scores to compare proposals.", [(SOURCE_02, [3])]),
    ("Initiation", "Project Charter", "Sponsor authorization, objectives, and high-level direction.", [(SOURCE_03, [1, 2]), (SOURCE_01, [4])]),
    ("Initiation", "Statement of Work", "Deliverables, boundaries, exclusions, and scope creep.", [(SOURCE_03, [3])]),
    ("Initiation", "Stakeholder Management", "Identify, prioritize, and engage stakeholders continuously.", [(SOURCE_03, [5]), (SOURCE_02, [5])]),
    ("Cases", "Pan Europa Foods", "Choosing a portfolio within a limited capital budget.", [(SOURCE_02, [4])]),
]
