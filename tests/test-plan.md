# Test Plan and Design Decisions (written before implementation)

Date: 2026-09-28
Author: Paola

This file lives in `tests/`, outside the Obsidian vault, so the retrieval step can never read it as a source.

## 1. Data

**Purpose:** a personal study wiki for the Project Management course, covering classes 1 to 3.

| Source file (`vault/raw/`) | Topic |
|---|---|
| `01_Project_Management_Introduction_Summary.md` | What a project is, success criteria, life cycle, projects vs programs vs portfolios |
| `02_Project_Selection_Methods_Summary.md` | Project categories, financial and nonfinancial selection methods, Pan Europa Foods case |
| `03_Project_Initiation_and_Stakeholders_Summary.md` | Charter, statement of work, responsibilities, priorities, complexity, stakeholders |

All sources are my own class notes, written in English, and shareable.

## 2. Planned wiki notes (`vault/wiki/`)

| Folder | Notes |
|---|---|
| Concepts | Project Definition, Project Success Criteria, Project Life Cycle, Projects Programs and Portfolios, Project Complexity |
| Selection | Project Selection Methods, Financial Evaluation, Weighted Scoring Model |
| Initiation | Project Charter, Statement of Work, Stakeholder Management |
| Cases | Pan Europa Foods |

Planned cross-class links:

- Project Success Criteria (class 1) ↔ Project Charter, priority matrix (class 3)
- Projects Programs and Portfolios (class 1) ↔ Project Selection Methods (class 2)
- Project Life Cycle, initiation stage (class 1) ↔ Project Charter, Statement of Work, Stakeholder Management (class 3)
- Project Selection Methods, portfolio process step 1 (class 2) ↔ Stakeholder Management (class 3)

## 3. Model

| Item | Choice |
|---|---|
| Runtime | Ollama 0.34.4 (Windows) |
| Generation model | `gemma4:e2b-it-qat` (Gemma 4 E2B, 4-bit quantization-aware trained, 4.3 GB file) |
| Embedding model | `embeddinggemma` (621 MB) |
| Device | Intel Core i5-1335U, 16 GB RAM, Intel Iris Xe integrated graphics (no dedicated VRAM), Windows 11 Pro |
| Reason | CPU-only laptop; E2B is the smallest Gemma option and fits with room for the OS, apps, and retrieval |
| Planned setting | Disable the model's "thinking" output to reduce response time on CPU |

## 4. Retrieval

- **Method:** hybrid search, combining keyword matching and embedding similarity.
- **Passage size:** one numbered section of a source note per passage.
- **Context sent to Gemma:** the top 4 passages per question, each with its source path and section.

## 5. Ask-mode tests

| # | Type | Question | Expected answer | Expected evidence |
|---|---|---|---|---|
| 1 | Direct, one source | What should a project charter include? | Title and reason, SMART objectives, benefits and deliverables, assumptions, high-level scope, milestones, roles, resources, risks, success measures, approval signatures | Class 3, section 2 |
| 2 | Different wording from the source | How can a company decide which projects to fund when it has more ideas than money? | Classify projects by category; combine financial (payback, NPV) and nonfinancial (weighted scoring) methods; apply yes/no screens; build a balanced portfolio the organization can fund and deliver | Class 2, sections 1, 3, and 5 |
| 3 | Connects two sources | How should a project manager balance scope, time, and cost? | The three goals affect one another (class 1); the priority matrix decides which to constrain, enhance, or accept (class 3) | Class 1, section 3 + Class 3, section 4 |
| 4 | Unsupported | How does agile project management differ from traditional approaches? | Explicit statement that the evidence is insufficient | None: the notes do not mention agile |

## 6. Expected behavior (before testing)

- **Tests 1 and 3:** expected to work; the key terms appear directly in the sources.
- **Test 2:** most likely retrieval failure, because the question does not use the words "selection" or "portfolio". Hybrid search is meant to address this.
- **Test 4:** most likely answer failure, because Gemma has general knowledge about agile and may answer from it instead of reporting insufficient evidence.
- **General risk:** broad questions produce longer answers with more claims to check; any claim not found in the retrieved passages counts as a failure.
