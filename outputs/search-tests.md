# Search retrieval tests

Date: 2026-09-29T16:51:03-07:00

Source: unchanged tests/test-plan.md. Top k = 4; keyword weight = 0.5; semantic weight = 0.5. No weight tuning.

Each row lists results in ranked order. Yes means every expected source section appears in the top four. The unsupported question is No because no agile evidence exists; this is not an abstention test.

Search seconds cover data loading, BM25, the local query embedding, and ranking; exclude CLI startup and output saving.

| Question | Four retrieved sections (ranked) | Expected evidence in top 4? | Search seconds |
|---|---|---|---:|
| What should a project charter include? | 1. 03_Project_Initiation_and_Stakeholders_Summary.md, section 2<br>2. 01_Project_Management_Introduction_Summary.md, section 4<br>3. 03_Project_Initiation_and_Stakeholders_Summary.md, section 3<br>4. 01_Project_Management_Introduction_Summary.md, section 1 | Yes | 2.404 |
| How can a company decide which projects to fund when it has more ideas than money? | 1. 02_Project_Selection_Methods_Summary.md, section 5<br>2. 02_Project_Selection_Methods_Summary.md, section 1<br>3. 02_Project_Selection_Methods_Summary.md, section 2<br>4. 02_Project_Selection_Methods_Summary.md, section 4 | No | 2.394 |
| How should a project manager balance scope, time, and cost? | 1. 01_Project_Management_Introduction_Summary.md, section 3<br>2. 03_Project_Initiation_and_Stakeholders_Summary.md, section 4<br>3. 03_Project_Initiation_and_Stakeholders_Summary.md, section 1<br>4. 01_Project_Management_Introduction_Summary.md, section 6 | Yes | 2.381 |
| How does agile project management differ from traditional approaches? | 1. 01_Project_Management_Introduction_Summary.md, section 2<br>2. 03_Project_Initiation_and_Stakeholders_Summary.md, section 4<br>3. 01_Project_Management_Introduction_Summary.md, section 5<br>4. 03_Project_Initiation_and_Stakeholders_Summary.md, section 1 | No | 2.368 |

## Saved detailed results

- Search 1: [20260929-165106-998241-what-should-a-project-charter-include.md](search/20260929-165106-998241-what-should-a-project-charter-include.md)
- Search 2: [20260929-165110-451714-how-can-a-company-decide-which-projects-to-fund-when-it-has-more-ideas.md](search/20260929-165110-451714-how-can-a-company-decide-which-projects-to-fund-when-it-has-more-ideas.md)
- Search 3: [20260929-165114-350462-how-should-a-project-manager-balance-scope-time-and-cost.md](search/20260929-165114-350462-how-should-a-project-manager-balance-scope-time-and-cost.md)
- Search 4: [20260929-165117-749936-how-does-agile-project-management-differ-from-traditional-approaches.md](search/20260929-165117-749936-how-does-agile-project-management-differ-from-traditional-approaches.md)

## Evidence expectations

- Question 1: Class 3, section 2
- Question 2: Class 2, sections 1, 3, and 5
- Question 3: Class 1, section 3 + Class 3, section 4
- Question 4: None: the notes do not mention agile

Verified unchanged hashes for every vault file, tests/test-plan.md, and the original ingest log. Rebuilt only retrieval data; no wiki notes regenerated.
