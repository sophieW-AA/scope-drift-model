---
name: meta-skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.
---

# Skill Creator

This skill provides guidance for creating effective skills.

## About Skills

Skills are modular, self-contained packages that extend Claude's capabilities by providing
specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific
domains or tasks—they transform Claude from a general-purpose agent into a specialized agent
equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else Claude needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption: Claude is already very smart.** Only add context Claude doesn't already have. Challenge each piece of information: "Does Claude really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of Claude as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   ├── description: (required)
│   │   └── compatibility: (optional, rarely needed)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/ - Executable code (Python/Bash/etc.)
    ├── references/ - Documentation intended to be loaded into context as needed
    └── assets/ - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter** (YAML): Contains `name` and `description` fields (required), plus optional fields like `license`, `metadata`, and `compatibility`. Only `name` and `description` are read by Claude to determine when the skill triggers, so be clear and comprehensive about what the skill is and when it should be used. The `compatibility` field is for noting environment requirements (target product, system packages, etc.) but most skills don't need it.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by Claude for patching or environment-specific adjustments

##### References (`references/`)

Documentation and reference material intended to be loaded as needed into context to inform Claude's process and thinking.

- **When to include**: For documentation that Claude should reference while working
- **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md or references files, not both

##### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output Claude produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates

#### What to Not Include in a Skill

Do NOT create extraneous documentation or auxiliary files, including README.md, INSTALLATION_GUIDE.md, QUICK_REFERENCE.md, CHANGELOG.md, etc. The skill should only contain the information needed for an AI agent to do the job at hand.

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Claude (Unlimited because scripts can be executed without reading into context window)

Keep SKILL.md body to the essentials and under 500 lines. Split content into separate files when approaching this limit.

## Skill Creation Process

1. Understand the skill with concrete examples
2. Plan reusable skill contents (scripts, references, assets)
3. Initialize the skill (run init_skill.py)
4. Edit the skill (implement resources and write SKILL.md)
5. Validate the skill (run quick_validate.py)
6. Publish the skill
7. Iterate based on real usage

Follow these steps in order, skipping only if there is a clear reason why they are not applicable.

### Step 1: Understanding the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood.

Ask the user:

1. "What should this skill help an AI agent do? Give me a concrete example of a task."
2. "What would someone say or ask that should trigger this skill?"
3. "Does the agent need any external data, APIs, or tools to do this?"

If the user's answers are vague, ask follow-up questions until the scope is clear. Do not proceed until at least one concrete usage example is gathered.

### Step 2: Planning the Reusable Skill Contents

Analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

### Step 2b: Naming and Overlap Check

Before creating the skill folder:

1. Read the **Naming Convention** section of the repository's `README.md` to identify the correct domain prefix for the new skill.
2. Scan existing folders under `skills/` and read their SKILL.md frontmatter (`name` and `description`) to verify the new skill does not duplicate or significantly overlap an existing one. If a similar skill exists, ask the user whether to extend the existing skill or create a new one.
3. If no prefix fits, document the rationale for a new prefix in the PR description.

Propose a name (prefix + 2–4 descriptive words, kebab-case, max 64 chars) and confirm with the user before proceeding.

### Step 3: Initializing the Skill

When creating a new skill from scratch, always run the `init_skill.py` script:

```bash
scripts/init_skill.py <skill-name> --path <parent-directory>
```

The script creates a skill directory with SKILL.md template, and example `scripts/`, `references/`, and `assets/` directories.

### Step 4: Edit the Skill

When editing the skill, remember that the skill is being created for another instance of Claude to use.

#### Learn Proven Design Patterns

- **Multi-step processes**: See references/workflows.md for sequential workflows and conditional logic
- **Specific output formats or quality standards**: See references/output-patterns.md for template and example patterns

#### Start with Reusable Skill Contents

Begin with the reusable resources identified in Step 2. Added scripts must be tested by actually running them. Delete any example files not needed.

#### Update SKILL.md

**Writing Guidelines:** Always use imperative/infinitive form.

##### Frontmatter — Name and Description

The `name` and `description` are the most important parts of any skill. They are the **only** text an agent sees before deciding whether to load the skill. Get them wrong and the skill either never triggers or triggers for the wrong tasks.

**`name`**: Must match the folder name exactly. Use the domain prefix from Step 2b.

**`description`**: This is a semantic definition of the skill's purpose — not a feature list, not a keyword dump.

- Focus on **what** the skill does and **when** to use it. Define the skill's remit clearly enough that an agent can confidently decide "this applies" or "this doesn't apply".
- Do NOT include **how** the skill works — no tools, table names, SQL, APIs, commands, or implementation details. These belong in the body.
- Avoid listing specific trigger phrases, keywords, or narrow use-cases. These dilute the core meaning and can delay or confuse triggering. Instead, write a clear, general statement that naturally covers those cases.
- Write in third person.

**Good** — clear semantic definition:
> Landscape analysis for new journal opportunities. Use when evaluating whether a research field has a gap worth filling — competitor mapping, market sizing, and author pool identification.

**Bad** — keyword list that dilutes meaning:
> Use when user says "whitespace", "competitor journals", "submission pool", "new journal idea", "market gap", "research field analysis", or asks about launching journals.

Do not include any other fields in YAML frontmatter.

Ask the user to review the SKILL.md draft before finalizing. Delete any placeholder subdirectories (`scripts/`, `references/`, `assets/`) the skill doesn't need.

### Step 5: Validate

#### 5a. Run the structural validator

```bash
python skills/meta-skill-creator/scripts/quick_validate.py skills/<skill-name>
```

Fix any issues it reports before proceeding.

#### 5b. Two skill reviewers (same bar as publish)

After structural validation passes, **run both reviewers against the skill** before Step 6. Treat `reviewers/reviewer-general.md` and `reviewers/reviewer-naming.md` as the checklists: read them, evaluate the skill (including overlap with existing `skills/` entries for the naming reviewer), and **present all findings to the user** in the conversation. Tell the user up front that there are **two** reviewers—one for general skill quality, one for naming and overlap—so they know what to expect.

**Do not automatically edit the skill** to implement reviewer suggestions. The agent’s job here is to report: severity, reviewer, and enough context (file, section, or quote) for the user to judge. The user decides what to change, defer, or reject, and **only then** should the agent apply edits—when the user gives explicit instructions (per item, subset, or blanket “fix all blocking”).

Report findings using the same severity labels the reviewer specs use (**Blocking** / **Important** / **Minor**). **Blocking** issues should be addressed before treating the skill as ready to publish; **Important** issues should be addressed unless the user documents a reason to defer—after the user has directed which fixes to make.

| Reviewer | File | Focus |
|-------|------|-------|
| General | `reviewers/reviewer-general.md` | Structural validity, description quality, internal consistency, examples correctness |
| Naming | `reviewers/reviewer-naming.md` | Domain prefix convention, duplication/overlap with existing skills, naming clarity |

If the same reviewers are also wired to run on pull requests in this repository, treat PR comments as a repeat of the same bar—not a separate standard.

### Step 6: Publish the Skill

Try running `package_skill.py` first — it validates, packages, and pushes the skill to GitHub:

```bash
python skills/meta-skill-creator/scripts/package_skill.py skills/<skill-name>
```

If it succeeds, the PR is created. After merge, add the skill to the table in `README.md` under the appropriate domain section.

If it fails (e.g. environment not configured), help the user publish manually: create a branch, commit the skill folder, push, and open a PR.

### Step 7: Iterate

After testing, users may request improvements. Iterate by:

1. Using the skill on real tasks
2. Noticing struggles or inefficiencies
3. Identifying how SKILL.md or bundled resources should be updated
4. Implementing changes and testing again
