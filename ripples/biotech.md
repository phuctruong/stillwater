---
ripple_id: ripple.biotech
version: 1.0.0
base_skills: [prime-math, prime-safety, phuc-forecast]
persona: Bioinformatician / lab automation engineer (genomics, proteomics, high-throughput screening)
domain: biotech
author: contributor:computational-biology-group
swarm_agents: [scientist, mathematician, skeptic, adversary, security, ethicist]
---

# Biotech / Bioinformatics Ripple

## Domain Context

This ripple configures prime-math, prime-safety, and phuc-forecast for bioinformatics
analysis pipelines, lab automation, and literature-based research synthesis:

- **Genomics:** GATK, BWA, STAR, salmon, DESeq2, Seurat (single-cell), VEP (variant annotation)
- **Proteomics:** MaxQuant, Perseus, AlphaFold2, PyMOL, MSFragger
- **Languages:** Python (biopython, scanpy, anndata), R (Bioconductor), Snakemake/Nextflow
- **Lab automation:** Opentrons, Hamilton VENUS, PyHamilton, plate reader scripting
- **Data standards:** FASTQ, BAM/CRAM, VCF, GFF3, FASTA, mzML, HDF5 (AnnData)
- **Repositories:** NCBI SRA, GEO, UniProt, PDB, EMBL-EBI, ClinVar
- **Correctness surface:** batch effects, multiple testing correction, reference genome version
  mismatch, sample swap detection, liquid handling precision, IRB/biosafety compliance

## Skill Overrides

```yaml
skill_overrides:
  prime-math:
    exact_arithmetic:
      enforce_in_verification_path: true
      note: >
        Statistical thresholds (adjusted p-values, fold-change cutoffs, q-values) must
        be stored and compared as Decimal strings. Float comparison for significance
        is forbidden in evidence artifacts. Bonferroni and BH correction must use
        exact rational arithmetic for the correction factor.
      forbidden_in_verification:
        - float_comparison_for_pvalue_threshold
        - uncorrected_pvalue_as_final_significance_claim
        - fold_change_computed_with_float_log2
    proof_obligations:
      require_multiple_testing_correction: true
      require_effect_size_alongside_pvalue: true
      note: >
        A p-value without effect size is an incomplete result. Every significance
        claim must report both: adjusted_p_value_decimal and effect_size_decimal
        (Cohen's d, log2FC, odds ratio, etc.).
  prime-safety:
    rung_default: 274177
    biosafety_check_required: true
    irb_check_required: true
    note: >
      Any protocol involving human samples, select agents, or BSL-2+ pathogens must
      have IRB approval number and biosafety level documented before protocol execution.
      Lab automation scripts must include pipette calibration verification.
    forbidden_ops:
      - protocol_execution_without_irb_if_human_samples
      - select_agent_protocol_without_biosafety_documentation
      - liquid_handler_script_without_calibration_check
      - sample_swap_risk_not_assessed
  phuc-forecast:
    stakes_default: HIGH
    required_lenses: [scientist, mathematician, skeptic, adversary, ethicist]
    premortem_required_before_experiment: true
    note: >
      Biological experiments have high costs (reagent cost, time, patient samples) and
      irreversibility. Premortem must address: batch effect risk, sample contamination,
      reagent degradation, instrument failure, and analysis pipeline version drift.
```

## Recipe Preferences

```yaml
recipe_preferences:
  - id: recipe.protocol-design
    priority: HIGH
    name: "Experimental Protocol Design"
    reason: >
      Lab protocols must be reproducible by a different operator from the written document
      alone. Every step must include: quantities with units, timing, equipment model and
      settings, quality checkpoints, and failure modes.
    steps:
      1: "State biological question, hypothesis, and measurable endpoint (e.g., fold-change in mRNA)"
      2: "List all reagents with: catalog number, lot number, concentration, storage condition"
      3: "List all equipment with: model number, calibration date, required settings"
      4: "Write step-by-step protocol: each step has action, quantity with units, timing, checkpoint"
      5: "Add QC checkpoints: expected appearance, concentration range, positive/negative controls"
      6: "Write failure mode guide: what does each type of failure look like? Recovery action?"
      7: "Record IRB number (if human samples) or biosafety level; document waste disposal"
      8: "Version control the protocol; compute sha256 of final protocol document"
    required_artifacts:
      - evidence/protocol.json (version_sha256, reagents_with_lots, equipment_with_calibration, irb_or_biosafety)
      - evidence/qc_checkpoints.json (checkpoint_name, expected_value_or_appearance, pass_criteria)

  - id: recipe.rna-seq-pipeline
    priority: HIGH
    name: "RNA-seq Differential Expression Analysis"
    reason: >
      RNA-seq analysis has many places for errors to silently propagate: reference genome
      version mismatch, duplicate sample, batch effect confounding, and inappropriate
      multiple testing correction. This recipe enforces a checkpoint at each step.
    steps:
      1: "Document: reference genome version, GTF annotation version, aligner version (all pinned)"
      2: "Run FastQC on all FASTQ files; flag any sample with quality score < 28 or > 30% adapter"
      3: "Align reads (STAR or HISAT2 with pinned version); record mapping rate per sample"
      4: "Flag samples with mapping rate < 70% as potential failures; do not include in DE analysis"
      5: "Count reads (salmon/featureCounts); check library size distribution for outliers"
      6: "Sample swap check: verify sex-linked gene expression matches sample metadata"
      7: "Run DESeq2 or edgeR: document design formula, normalization method"
      8: "Apply BH multiple testing correction; report adjusted_p_value and log2FC as Decimal strings"
      9: "Plot PCA colored by batch and condition; confirm batch effect not confounded with condition"
    required_artifacts:
      - evidence/pipeline_versions.json (genome_version, gtf_version, aligner, aligner_version, deseq2_version)
      - evidence/sample_qc.json (sample_id, mapping_rate_decimal, library_size, qc_pass)
      - evidence/de_results.json (gene_id, log2fc_decimal, adjusted_pvalue_decimal, effect_size_decimal)

  - id: recipe.data-validation
    priority: HIGH
    name: "Biological Data Validation Pipeline"
    reason: >
      Upstream data errors (sample swaps, contamination, format version mismatch) propagate
      silently through analysis pipelines and invalidate conclusions. Validation must happen
      before any analysis step.
    steps:
      1: "Check file format integrity: validate FASTQ/BAM/VCF headers against expected format version"
      2: "Check sample metadata completeness: all required fields populated, no NULL sample IDs"
      3: "Check sample identity: if paired samples exist, verify concordance via fingerprinting"
      4: "Check for cross-sample contamination (VerifyBamID or equivalent)"
      5: "Check reference genome version matches between all files in the analysis"
      6: "Check for known batch effects: extraction date, operator, plate position — flag if confounded"
      7: "Produce data_validation_report.json: per-sample pass/fail with specific failure reason"
    required_artifacts:
      - evidence/data_validation_report.json (sample_id, format_check, identity_check, contamination_rate_decimal, reference_version_match)

  - id: recipe.literature-synthesis
    priority: MED
    name: "Systematic Literature Review"
    reason: >
      Unsystematic literature review introduces selection bias and cherry-picking.
      This recipe enforces a PRISMA-style systematic approach with pre-registered
      search criteria before results are examined.
    steps:
      1: "Pre-register: research question, search terms, inclusion/exclusion criteria, databases to search"
      2: "Search PubMed, bioRxiv, and target journal archives with exact query strings"
      3: "Record: query_string, database, date_searched, total_results_count"
      4: "Screen titles/abstracts against inclusion criteria (blinded to conclusions where possible)"
      5: "Full-text review of included papers: extract key data into structured table"
      6: "Assess risk of bias per paper: sample size, control group, blinding, replication"
      7: "Synthesize: where do studies agree? Where do they conflict? What gaps remain?"
      8: "Cite every claim with paper DOI and specific figure/table number"
    required_artifacts:
      - evidence/search_log.json (query_string, database, date, total_results, included_count)
      - evidence/evidence_table.json (paper_doi, key_finding, sample_size, risk_of_bias, figure_reference)

  - id: recipe.liquid-handler-validation
    priority: HIGH
    name: "Liquid Handling Robot Validation"
    reason: >
      Pipetting errors in liquid handling automation cause systematic bias across
      an entire plate. Calibration must be verified before any assay run.
    steps:
      1: "Run gravimetric calibration: dispense water into pre-weighed plate; measure actual vs target volume"
      2: "Compute CV (coefficient of variation) for each tip channel as Decimal string"
      3: "Flag any channel with CV > Decimal('0.02') (2%) as out-of-spec"
      4: "Run positive and negative control wells first; verify controls are within expected range"
      5: "If calibration fails: halt run; do not proceed with sample plate"
      6: "Record: instrument_serial, calibration_date, channel_cv_decimal, pass_fail per channel"
    required_artifacts:
      - evidence/calibration_report.json (instrument_serial, calibration_date, channel_cv_decimal, overall_pass)
```

## Forbidden States (Domain-Specific)

```yaml
forbidden_states:
  - id: NO_ANALYSIS_WITHOUT_VERSION_PINNING
    description: >
      Bioinformatics pipelines using unpinned tool versions (e.g., STAR latest) produce
      results that cannot be reproduced when the tool is updated. All tools must be pinned
      to exact versions in a conda environment, Docker image, or Nextflow container.
    detector: "Check evidence/pipeline_versions.json: all tools must have exact version strings."
    recovery: "Pin all tools: conda env export > environment.yml; or use Docker image with sha256."

  - id: NO_SIGNIFICANCE_WITHOUT_CORRECTION
    description: >
      Reporting p-values without multiple testing correction when conducting multiple
      comparisons is a statistical error. BH or Bonferroni correction is mandatory for
      any analysis with more than one hypothesis test.
    detector: "Check evidence/de_results.json: must have adjusted_pvalue_decimal, not raw pvalue."
    recovery: "Apply p.adjust(method='BH') in R or statsmodels multipletests in Python; use adjusted values."

  - id: NO_HUMAN_SAMPLE_PROTOCOL_WITHOUT_IRB
    description: >
      Any experimental protocol involving human biospecimens, human-derived cell lines,
      or identifiable human data must have a documented IRB approval number before execution.
    detector: "Check evidence/protocol.json for irb_approval_number field if sample_type contains 'human'."
    recovery: "Halt protocol execution. Obtain IRB approval. Document approval number and expiration date."

  - id: NO_BATCH_EFFECT_IGNORED
    description: >
      A PCA or UMAP colored by batch that shows separation by batch before separation by
      condition indicates a confounded batch effect. Analysis must not proceed without
      addressing batch correction (ComBat, Harmony, scVI, etc.).
    detector: "Check evidence/sample_qc.json for batch_effect_assessment field."
    recovery: "Run ComBat-seq or Harmony; re-plot PCA; confirm batch no longer drives PC1/PC2."

  - id: NO_FLOAT_IN_PVALUE_COMPARISON
    description: >
      Threshold comparisons like 'if pvalue < 0.05' using Python float are forbidden
      in evidence artifacts. Adjusted p-values must be stored and compared as Decimal strings.
    detector: "grep -n 'if.*pvalue\\|if.*padj\\|if.*qvalue' -- check for Decimal comparison"
    recovery: "from decimal import Decimal; threshold = Decimal('0.05'); assert padj_decimal < threshold"
```

## Verification Extensions

```yaml
verification_extensions:
  rung_641:
    required_checks:
      - pipeline_versions_pinned: "evidence/pipeline_versions.json with exact version strings for all tools"
      - sample_qc_passed: "all samples in evidence/sample_qc.json have qc_pass: true or documented exclusion"
      - adjusted_pvalues_used: "evidence/de_results.json uses adjusted_pvalue_decimal not raw pvalue"
      - irb_documented: "evidence/protocol.json has irb_approval_number if human samples present"
  rung_274177:
    required_checks:
      - batch_effect_assessed: "PCA by batch generated and reviewed; batch_effect_assessment in sample_qc.json"
      - positive_negative_controls: "qc_checkpoints.json shows controls within expected range"
      - sample_swap_check: "identity concordance verified for paired samples"
      - calibration_report_current: "evidence/calibration_report.json dated within 30 days of assay"
  rung_65537:
    required_checks:
      - independent_replication: "key findings replicated in independent sample set or by independent analyst"
      - effect_size_reported: "all claims have effect_size_decimal alongside adjusted_pvalue_decimal"
      - literature_context: "evidence/evidence_table.json places findings in context of prior literature"
      - data_deposition_ready: "raw data ready for NCBI SRA or appropriate repository with metadata"
```

## Quick Start

```bash
# Load this ripple and start a biotech task
stillwater run --ripple ripples/biotech.md --task "Design RNA-seq analysis pipeline for tumor vs normal comparison"
```

## Example Use Cases

- Design a complete RNA-seq differential expression pipeline: pins all tool versions, runs FastQC
  quality control, detects sample swaps via sex-linked gene expression, applies BH multiple testing
  correction with Decimal-string p-values, and assesses batch effects via PCA before reporting
  any significant genes.
- Validate a liquid handling robot protocol before a high-throughput drug screen: runs gravimetric
  calibration across all channels, computes CV as Decimal strings, halts if any channel exceeds
  2% CV, and requires positive/negative controls before the sample plate is loaded.
- Conduct a systematic literature review on a target pathway: pre-registers search terms and
  inclusion criteria, screens 200+ papers, extracts structured evidence into an evidence_table.json
  with DOI and figure citations, and flags conflicts between studies with risk-of-bias assessment.
