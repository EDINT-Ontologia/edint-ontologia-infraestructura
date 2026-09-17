# Ontology Requirements

This folder contains all the **requirements and supporting materials** used during the development of the ontology.

# Purpose
The goal of this directory is to store and organize the **foundational information** that guides the ontology’s design and implementation.  
These requirements define **what the ontology should represent**, **why it is being developed**, and **how it should support the intended use cases**.

# Contents
Include here any documents or resources that describe or justify the ontology requirements, such as:

- **Competency questions** — Questions the ontology must be able to answer.  
- **Use cases and scenarios** — Descriptions of real-world contexts where the ontology will be applied.  
- **Domain requirements** — Lists of key concepts, relationships, or constraints gathered from experts.  
- **Stakeholder requirements** — Functional and non-functional needs from users or organizations.  

# Accepted Formats
You can use the following formats:
- `.md` — Markdown documents  
- `.docx` / `.pdf` — Formal requirement documents  
- `.csv` / `.xlsx` — Requirement lists or traceability matrices  
- `.txt` — Notes or preliminary requirement drafts  

# Best Practices
- Keep requirements **traceable** — link each one to ontology elements (classes, properties, etc. See template).  
- Maintain version history as requirements evolve.  
- Ensure consistency between requirements, conceptualization diagrams, and implementation.  
- Review and validate requirements with domain experts before ontology development begins. The [LOT methodology](https://doi.org/10.1016/j.engappai.2022.104755) proposes some guidelines:
  - A set of requirements is correct if each requirement refers to some features of the ontology to be developed.
  - A set of requirements is complete if users and domain experts review the requirements and confirm that they are not aware of additional requirements.
  - A set of requirements is internally consistent if no conflicts exist between them.
  - A set of requirements is verifiable if there is a finite process with a reasonable cost that tests whether the final ontology satisfies each requirement.
  - A set of requirements is comprehensible if each and every requirements is understandable to users and domain experts.
  - A set of requirements is unambiguous if each and every requirements has only one possible interpretation; that is, if it does not admit any doubt or misunderstanding.
  - A set of requirements is concise if each and every requirement is relevant, and no duplicated or irrelevant requirements exist.


# Notes
- This folder is intended for **requirement documentation only** — not for ontology diagrams or implementation files.  
- Use subfolders if needed (e.g., `/competency-questions/`, `/use-cases/`, `/traceability/`).
