---
name: wedjat-project-context
description: Use whenever Codex is working in the Wedjat project on transcript processing, business-insight extraction, BERTimbau/NLP classification, chunking meetings, supervised ML experiments, Sprint 3 Data Science requirements, model evaluation, notebooks, pipelines, tests, documentation, or architecture. Do not use for unrelated repositories or generic programming questions.
---

# Wedjat Project Context

The user's explicit request takes precedence over this skill.

## Purpose

Maintain continuity when developing **Wedjat**, a project that turns very large meeting transcripts into structured business insights.

For project-specific decisions, use this order of evidence:

1. current repository code, tests, configs, notebooks, data schemas and README;
2. `references/project-context.md`;
3. `references/sprint-3-data-science.md`;
4. reasonable inference, clearly marked as inference.

Do not invent repository details that are not present in the code or these references.

## Required context recovery

Before a substantial change:

1. Inspect the relevant repository files.
2. Check `README.md`, notebooks, dependency manifests, configs, source folders and tests.
3. Check `git status` and the current diff before editing.
4. If the task touches the ML pipeline, inspect how meetings are identified, how text is chunked, how labels are represented, how train/test splitting is done and how metrics are calculated.
5. Preserve unrelated user changes.

## Core project direction

Wedjat addresses the problem of **huge meeting transcripts that are difficult to analyze manually**.

The intended solution is to use **Portuguese NLP models, especially BERTimbau from Hugging Face**, to classify transcript content and extract business-relevant signals.

The source dataset is large, with roughly **300,000 transcript rows**. Processing must therefore be designed to work in batches/chunks rather than assuming an entire corpus or long meeting fits into a single model input.

Read `references/project-context.md` for the detailed known context.

## ML / NLP decisions

When implementing or reviewing the ML pipeline:

- Treat the meeting as the business-level unit whenever the repository data supports a meeting identifier.
- Do not blindly cut text only by dataframe row count if rows belonging to one meeting can be reconstructed.
- Respect the tokenizer/model maximum sequence length.
- If a meeting is longer than the model input limit, create text windows/chunks and keep the meeting ID attached to every chunk.
- Prefer token-aware chunking over character-count chunking.
- Use overlap only when it helps preserve context across boundaries; keep it configurable.
- Never leak chunks from the same meeting across training and test sets.
- Aggregate chunk predictions back to the meeting level when the business question is defined per meeting.
- Keep the aggregation rule explicit and testable, such as majority vote, maximum-risk score, mean probability, or another rule justified by the target.
- Keep preprocessing identical between training, evaluation and inference.
- Preserve stopwords by default for transformer models unless an experiment proves removal improves the target task.
- Do not remove words merely because they look like conversational filler without measuring the effect.

## Sprint 3 compatibility

Sprint 3 requires supervised classification and a comparison between two algorithms.

BERTimbau may be one of the compared approaches. When the repository does not already define the second model, prefer a simple, explainable baseline such as:

- TF-IDF + Logistic Regression; or
- TF-IDF + Multinomial Naive Bayes.

Do not claim the comparison is complete until both approaches are trained and evaluated on the same compatible split.

Read `references/sprint-3-data-science.md` for the exact project checklist derived from the assignment.

## Evaluation rules

At minimum, produce or verify:

- confusion matrix;
- precision;
- recall;
- F1-score;
- accuracy.

When classes are imbalanced, do not use accuracy alone.

Prefer reporting per-class metrics plus macro and/or weighted averages. For a multi-class target, **macro F1** is usually a strong primary comparison metric because it gives each class equal importance, but the final metric justification must depend on the chosen business problem.

Examples:

- churn/risk detection: recall for the risky class can be especially important;
- opportunity detection: recall may matter when missing opportunities is costly, while precision matters when false commercial alerts overload the team;
- sentiment: macro F1 is often more informative than accuracy when neutral examples dominate;
- product mention: per-class precision/recall/F1 helps reveal products that the model confuses.

## Data splitting

Prefer splitting by meeting, not by individual chunk.

If multiple rows/chunks originate from the same meeting, keep all of them in exactly one of train/validation/test.

Use stratification when feasible for the chosen target.

If labels are created manually or assisted by another model, keep the labeling method documented and separate ground-truth labels from predictions.

## Recommended implementation path

When the user asks to continue the project and the repository does not already contain a more advanced working pipeline, favor this sequence:

1. understand the raw transcript schema and meeting identifier;
2. create a reproducible meeting-level dataset;
3. define one Sprint 3 classification target first;
4. inspect class distribution and missing labels;
5. create group-safe train/validation/test splits;
6. build TF-IDF + Logistic Regression baseline;
7. fine-tune/evaluate BERTimbau on the same target;
8. compare confusion matrix, precision, recall, F1 and accuracy;
9. justify the primary business metric;
10. implement chunk-to-meeting aggregation for long meetings;
11. document limitations and next steps;
12. only then generalize to multiple business insight heads/categories.

Avoid trying to solve every business insight category at once if doing so makes Sprint 3 evaluation unclear.

## Coding behavior

- Follow existing project structure and naming.
- Reuse helpers before creating new abstractions.
- Keep experiments reproducible with fixed seeds where supported.
- Record model name/version, tokenizer, chunk size, overlap, split strategy and evaluation metrics.
- Prefer configuration values over hard-coded magic numbers.
- Do not commit credentials, Hugging Face tokens or private transcript content.
- Keep raw sensitive transcripts out of logs and example outputs unless the repository explicitly uses sanitized synthetic examples.

## Finish criteria for ML tasks

Before calling an ML task complete, state:

- target variable/classes;
- unit of analysis: row, chunk or meeting;
- split strategy;
- models compared;
- metrics obtained;
- primary metric and why it matters to the business case;
- whether chunks from the same meeting can leak across splits;
- how chunk predictions are aggregated;
- known limitations.

Never claim a metric, test or training run succeeded unless it actually ran.
