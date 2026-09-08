# Wedjat — known project context

## Problem

The project receives **very large meeting transcripts** and needs to extract useful **business insights** from them automatically.

Manual reading does not scale. The current dataset is on the order of **300,000 transcript rows**, so the solution must support large-volume processing.

## Proposed solution

Use a Portuguese transformer model from Hugging Face, especially **BERTimbau**, to analyze transcript text and return business-oriented classifications.

The general flow is:

```text
raw transcript rows
        ↓
reconstruct/group by meeting
        ↓
clean/normalize only what is justified
        ↓
tokenize
        ↓
split long meetings into token-aware chunks
        ↓
classification model
        ↓
chunk probabilities/predictions
        ↓
aggregate back to meeting/business level
        ↓
business insights
```

## Business insight categories discussed

The Sprint 3 assignment suggests classification problems such as:

- commercial opportunity:
  - opportunity
  - no opportunity

- churn / dissatisfaction risk:
  - risk
  - neutral

- sentiment:
  - positive
  - neutral
  - negative

- TOTVS product mentioned:
  - examples: Protheus, RM, Fluig, etc.

The project does not need to implement all targets simultaneously to satisfy one supervised-classification experiment. A focused target with a correct comparison and evaluation is preferable to several weakly validated targets.

## Large transcript handling

A BERT-family model has a maximum input length, so entire long meetings cannot simply be sent to the model as one sequence.

Preferred approach:

1. group rows that belong to the same meeting;
2. preserve `meeting_id` (or the repository's equivalent identifier);
3. tokenize the meeting text;
4. create token windows up to the model limit;
5. optionally use overlap;
6. classify every chunk;
7. aggregate chunk results into a meeting-level result.

### Important leakage rule

All chunks from one meeting must stay in the same train/validation/test partition.

Splitting after chunking with a normal random row split can produce unrealistically high metrics because the model can see one part of a meeting during training and another part of the same meeting during testing.

## Baseline vs BERTimbau

Sprint 3 asks for **two algorithms**.

Recommended comparison when the repository has not already decided otherwise:

### Model A — baseline

`TF-IDF + Logistic Regression`

Why:
- fast;
- cheap;
- easy to explain;
- strong text-classification baseline;
- gives a meaningful reference for whether BERTimbau adds value.

### Model B — transformer

`BERTimbau fine-tuned for sequence classification`

Why:
- language model trained for Portuguese;
- captures contextual meaning beyond bag-of-words features;
- better aligned with nuanced commercial language.

Both models should use the same target and compatible group-safe data split.

## Candidate architecture for experiments

```text
data/
  raw/
  processed/

notebooks/
  01_data_understanding.ipynb
  02_baseline_tfidf_logreg.ipynb
  03_bertimbau_finetuning.ipynb
  04_model_comparison.ipynb

src/
  data/
    load.py
    meetings.py
    split.py
  nlp/
    chunking.py
    preprocessing.py
  models/
    baseline.py
    bertimbau.py
    evaluation.py
  inference/
    aggregate.py

reports/
  metrics/
  figures/
```

This is only a recommended shape. If the Wedjat repository already has a structure, follow the repository instead.

## Questions that must be answered from the actual repo/data

Do not guess these:

- Which column uniquely identifies a meeting?
- Is each of the 300k rows a phrase, speaker turn, sentence, timestamp or another unit?
- Are labels already available?
- Are labels meeting-level or chunk/row-level?
- Which Sprint 3 target is the team's official target?
- How many classes and examples per class exist?
- Which BERTimbau checkpoint is currently used?
- Is fine-tuning already implemented or is BERTimbau only being used for embeddings/inference?
- How is chunk aggregation currently done?
- What hardware/runtime is being used in the current version?
- Which files/notebooks already exist?

Resolve these by inspecting the repository before changing architecture.
