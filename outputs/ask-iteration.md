# Ask instruction iteration: v1 to v2

One documented instruction-only improvement round. V1 run files and the renamed v1 summary are intact. V2 answers are unedited and are not graded here.

## What changed

The following three general rules were appended to the exact v1 instructions. Targets are the v1 observations specified by Paola; no v2 correctness judgment is made.

### Rule a

Read all passages before answering. Use every passage that is relevant to the question. When the question involves several ideas or how they relate, combine evidence from different passages and cite each one.

Observed v1 issue targeted: Q3 used only class 3 section 4, although class 1 section 3 was retrieved.

### Rule b

Keep the scope of the source: if a point comes from a specific case or example, say so instead of presenting it as a general rule.

Observed v1 issue targeted: Q2 presented Pan Europa Foods case content as a general rule.

### Rule c

Keep separate items from the source as separate items; do not merge them.

Observed v1 issue targeted: Q1 merged separate charter items using "including".

## Controlled settings

Only the answer instructions changed. Search code, data, weights (0.5/0.5), top_k (4), temperature (0.2), seed (42), context (8192), token limit (1024), persona, vault, and test plan are unchanged.
Retrieval was not changed, so the Q2 retrieval miss (class 2 section 3) is still expected. Instruction changes cannot add that missing passage.

Generation times below include any model loading and are observations, not a controlled performance benchmark.

## Q1. What should a project charter include?

| Field | V1 | V2 |
|---|---|---|
| Answer | The project charter should include:<br><br>*   Project title, brief description, reason for doing it, and link to strategy [1].<br>*   Specific objectives, expected benefits, results, and major deliverables [1].<br>*   Assumptions that must later be checked, high-level scope and boundaries [1].<br>*   Major milestones and timeline, including effects on existing systems or teams [1].<br>*   Roles and contact details, including initial funding, people, and other resources [1].<br>*   Main risks and responses, success measures and targets, and approval signatures [1]. | The project charter should include:<br><br>*   Project title, brief description, reason for doing it, and link to strategy [1].<br>*   Specific objectives, expected benefits, results, and major deliverables [1].<br>*   Assumptions that must later be checked, high-level scope and boundaries [1].<br>*   Major milestones and timeline, including effects on existing systems or teams [1].<br>*   Roles and contact details, initial funding, people, and other resources [1].<br>*   Main risks and responses, success measures and targets, and approval signatures [1]. |
| Citations used | [1] | [1] |
| Generation time | 53.041 s | 60.594 s |

Run records: [V1](ask/20260929-170009-329500-what-should-a-project-charter-include.md), [V2](ask/20260929-171254-119566-what-should-a-project-charter-include.md).
Retrieved passages, order, and stored scores matched v1 exactly.

## Q2. How can a company decide which projects to fund when it has more ideas than money?

| Field | V1 | V2 |
|---|---|---|
| Answer | Selection means choosing a set of projects that supports the organization's goals while considering each project's benefits, costs, risks, and resource needs [2]. Managers should combine project categories, financial measures, and nonfinancial criteria [2].<br><br>A practical portfolio process involves:<br>1. Forming a project council and identifying relevant stakeholders [1].<br>2. Setting project categories and selection criteria [1].<br>3. Collecting comparable information for each proposal and checking available resources [1].<br>4. Removing proposals or criteria that do not help the decision [1].<br>5. Ranking projects within categories, selecting those to fund, and keeping others in reserve [1].<br>6. Putting the decision process into practice and reviewing it as circumstances change [1].<br><br>Leaders can use five early yes/no screens: Is the project mandatory for an external reason? Does it meet the minimum IRR? Is its payback within the company's limit? Is the risk acceptable? Does it fit current corporate strategy? These screens can narrow the list before detailed comparisons [1].<br><br>Leaders can also rank projects by fastest payback, highest NPV, or highest IRR, and add strategy, implementation difficulty, risk, project dependencies, and synergies to produce another answer [4]. Leaders from finance, distribution, production, sales, marketing, and strategy may value projects differently [4]. The lesson is to make criteria and trade-offs visible, check conflicts with corporate strategy, and consider how projects work together [4]. | Selection means choosing a set of projects that supports the organization's goals while considering each project's benefits, costs, risks, and resource needs, as organizations usually have more project ideas than money, people, or time [2]. Managers should combine project categories, financial measures, and nonfinancial criteria [2].<br><br>A practical portfolio process involves:<br>1. Forming a project council and identifying relevant stakeholders [1].<br>2. Setting project categories and selection criteria [1].<br>3. Collecting comparable information for each proposal and checking available resources [1].<br>4. Removing proposals or criteria that do not help the decision [1].<br>5. Ranking projects within categories, selecting those to fund, and keeping others in reserve [1].<br>6. Putting the decision process into practice and reviewing it as circumstances change [1].<br><br>The lecture suggests using five early yes/no screens: Is the project mandatory for an external reason? Does it meet the minimum IRR? Is its payback within the company's limit? Is the risk acceptable? Does it fit current corporate strategy? These screens can narrow the list before detailed comparisons, and their thresholds should reflect company policy, with a mandatory project needing special treatment [1]. The key idea is to choose a balanced set of projects that the organization can actually fund and deliver, using numbers to inform the decision, then testing strategic fit, risk, resources, and the effects of combining projects [1].<br><br>Projects can be classified before comparing them:<br>*   A **compliance** project may be mandatory because of a rule or external requirement [3].<br>*   **Strategic** projects build future capabilities, products, or markets [3].<br>*   **Operational** projects improve current processes, quality, or support [3].<br>*   A genuine “must do” project may have to proceed even if it scores poorly on the usual ranking criteria [3].<br><br>When ranking projects, leaders from finance, distribution, production, sales, marketing, and strategy may value projects differently [4]. Leaders should make criteria and trade-offs visible, check conflicts with corporate strategy, and consider how projects work together [4]. |
| Citations used | [2], [1], [4] | [2], [1], [3], [4] |
| Generation time | 47.360 s | 57.881 s |

Run records: [V1](ask/20260929-170100-935815-how-can-a-company-decide-which-projects-to-fund-when-it-has-more-ideas.md), [V2](ask/20260929-171356-520531-how-can-a-company-decide-which-projects-to-fund-when-it-has-more-ideas.md).
Retrieved passages, order, and stored scores matched v1 exactly.

## Q3. How should a project manager balance scope, time, and cost?

| Field | V1 | V2 |
|---|---|---|
| Answer | Projects balance scope or performance, time, cost, and quality [2]. A priority matrix helps determine which goal to constrain (keep fixed), enhance (improve if possible), or accept (allow some flexibility) [2]. | Projects balance scope or performance, time, cost, and quality [2]. A priority matrix can be used to determine which goal to constrain (keep fixed), enhance (improve if possible), or accept (allow some flexibility) when requirements change or work needs to be accelerated [2]. Adding features may require more money or time, and reducing the schedule may increase cost or reduce what can be delivered [1]. |
| Citations used | [2] | [2], [1] |
| Generation time | 27.124 s | 33.725 s |

Run records: [V1](ask/20260929-170133-486883-how-should-a-project-manager-balance-scope-time-and-cost.md), [V2](ask/20260929-171434-605304-how-should-a-project-manager-balance-scope-time-and-cost.md).
Retrieved passages, order, and stored scores matched v1 exactly.

## Q4. How does agile project management differ from traditional approaches?

| Field | V1 | V2 |
|---|---|---|
| Answer | I don't have enough evidence in my notes to answer this. | I don't have enough evidence in my notes to answer this. |
| Citations used | None | None |
| Generation time | 26.748 s | 26.944 s |

Run records: [V1](ask/20260929-170205-306530-how-does-agile-project-management-differ-from-traditional-approaches.md), [V2](ask/20260929-171505-908648-how-does-agile-project-management-differ-from-traditional-approaches.md).
Retrieved passages, order, and stored scores matched v1 exactly.

## Preservation checks

Verified unchanged hashes for the vault, data, search code, persona, test plan, v1 instructions, v1 summary, v1 run files, and the original memory capture. All existing configuration values were unchanged; ASK_PROMPT_VERSION=v2 was added.
