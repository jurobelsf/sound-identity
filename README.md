# Computational Characterization of Sonic Properties in Electronic Music

## Overview

This project explores the use of statistical and computational methods to characterize sonic properties in electronic music.

The main research question is whether low-level acoustic descriptors extracted from audio signals can be used to identify patterns associated with a specific musical corpus (Voam) and distinguish it from a control corpus.

The project combines Music Information Retrieval (MIR), statistical modeling, and machine learning to investigate which acoustic features contribute most strongly to this distinction.

## Research Objectives

The project aims to:

- Develop a computational framework for describing sonic characteristics in electronic music.
- Investigate whether acoustic descriptors can distinguish the Voam corpus from a control corpus.
- Identify the features that contribute most to the classification.
- Explore the statistical relationships between acoustic descriptors and corpus membership.
- Evaluate whether the observed separation between groups is greater than would be expected by chance.

## Methodology

The current pipeline consists of several stages:

1. **Audio preprocessing**
   
   Audio files are normalized to a common loudness target before feature extraction.

2. **Feature extraction**
   
   Acoustic descriptors are extracted from the audio using [Essentia](https://essentia.upf.edu/), including spectral, Bark-band, MFCC, dissonance, spectral complexity, spectral flux, and related descriptors.

3. **Feature filtering**
   
   A theoretical selection step is used to retain descriptors relevant to the research question. Redundant variables are subsequently filtered using Spearman correlation between predictors.

4. **Statistical analysis**
   
   Generalized Additive Models (GAMs) are used to investigate the relationship between individual acoustic descriptors and corpus membership, including the detection of potentially non-linear effects.

5. **Machine learning**
   
   Random Forest classifiers are used to evaluate whether the selected acoustic features can discriminate between the Voam and control corpora. Model performance is evaluated using out-of-bag (OOB) accuracy and ROC-AUC.

6. **Permutation testing**
   
   Label permutations are used to test whether the observed classification performance can be explained by chance.

## Current Status

This repository contains the current working implementation of the research pipeline and preliminary analyses.

The project is **currently in progress**. The main analytical framework has been implemented, while further analysis, interpretation, validation, and documentation are still ongoing.

Some of the code is therefore intentionally presented in its current research-development form. The scripts will be cleaned up, documented, and consolidated as the project progresses.

## Repository Structure

```text
.
├── code/
│   ├── audio_processing/
│   ├── feature_extraction/
│   ├── statistical_analysis/
│   └── modeling/
│
├── data/
│
└── README.md
