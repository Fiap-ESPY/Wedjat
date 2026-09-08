# Sprint 3 — Data Science and Statistical Computing

## Objective

Evolve work from previous sprints using **supervised Machine Learning models** to automatically classify transcript excerpts into business-relevant categories.

## Example problem types from the assignment

- commercial opportunity: opportunity / no opportunity;
- churn or dissatisfaction risk: risk / neutral;
- sentiment: positive / neutral / negative;
- TOTVS product mentioned: Protheus, RM, Fluig, etc.

## Required deliverables/checklist

The work must contain:

- comparison of **two algorithms**;
- confusion matrix;
- precision;
- recall;
- F1-score;
- accuracy;
- justification of which metric is most important for the analyzed problem.

## Recommended Wedjat mapping

A clean way to satisfy the requirement:

### Algorithm 1
TF-IDF + Logistic Regression

### Algorithm 2
BERTimbau fine-tuned for the same classification target

This gives the project:
- a classical baseline;
- a contextual Portuguese transformer;
- a defensible model comparison.

## Evaluation template

For each model, report:

| Item | What to report |
|---|---|
| Target | Exact class names |
| Unit | meeting / chunk / row |
| Split | train/validation/test and whether grouped by meeting |
| Confusion matrix | matrix + readable plot |
| Precision | per class + chosen average |
| Recall | per class + chosen average |
| F1 | per class + macro/weighted |
| Accuracy | overall |
| Runtime/cost | optional but useful |
| Errors | examples or categories of confusion |

## Choosing the most important metric

Do not automatically say accuracy.

Use business impact:

### Opportunity classification
- High recall: finds more real opportunities.
- High precision: reduces false alerts.
- F1: useful when both matter.
- If the dataset is imbalanced, macro F1 can be a good model-comparison metric.

### Churn / dissatisfaction risk
Missing a risky customer can be more costly than investigating a false alert, so **recall of the risk class** can be the primary business metric.

### Sentiment
If neutral dominates the dataset, accuracy can hide poor performance on positive/negative examples. **Macro F1** is often more informative.

### Product mentioned
Use per-product metrics. Macro F1 helps prevent a frequent product from dominating the global score.

## Critical methodological requirement for Wedjat

Because one meeting may create many chunks, use a **group-aware split by meeting**.

Bad:

```text
meeting A → chunk 1 train
meeting A → chunk 2 test
```

Good:

```text
meeting A → all chunks train
meeting B → all chunks test
```

This is essential for trustworthy Sprint 3 metrics.

## Suggested experiment sequence

1. choose one official classification target;
2. measure class balance;
3. split by meeting;
4. train classical baseline;
5. evaluate;
6. fine-tune BERTimbau;
7. evaluate on the same test partition;
8. compare metrics;
9. analyze confusion matrix;
10. justify the primary metric based on business consequences;
11. document limitations, especially labeling quality and long-context chunk aggregation.
