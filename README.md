# The Tunnel Pipeline

**What Gets Lost, What It Costs, and the Case for PARIA**

*Ivan Phan (HiP) · Independent Researcher · ORCID [0009-0003-1095-5855](https://orcid.org/0009-0003-1095-5855)*

**DOI:** [10.5281/zenodo.19804186](https://doi.org/10.5281/zenodo.19804186) · **Licence:** CC BY 4.0 · **Series:** Training Landscape, Paper 3

---

## Read the paper

**[Read online (HTML)](https://hip1.github.io/The-Tunnel-Pipeline/the-tunnel-pipeline.html)** · [Download PDF](the-tunnel-pipeline.pdf) · [Markdown source](the-tunnel-pipeline.md)

---

## Summary

Every AI training pipeline contains a judgment pipeline: the chain of events from criterion selection through evaluator judgment to training-signal aggregation and weight update. This paper identifies five structural conditions the judgment pipeline must satisfy, collectively the **PARIA framework**:

- **P**reservation — Does the verdict record carry the judgment's epistemic content forward intact?
- **A**dequacy — Does the criterion measure the right property on the right slice of cases?
- **R**eproducibility — Are verdicts stable under criterion-irrelevant context variation?
- **I**ndependence — Do the evaluator's error modes overlap with the producer's?
- **A**ccountability — Does the feedback structure generate corrective pressure proportional to deployment scale?

Non-redundancy is demonstrated by counterexample. A seven-class cross-pipeline diagnostic grounds the framework in peer-reviewed independent evaluations. Under autoregressive transformers, condition failures map to documented deployment pathologies: sycophancy, fabrication, reward hacking, proxy collapse, and calibration collapse.

The economic argument, grounded in the OECD's Value of Statistical Life methodology and measured cost data across six domains (healthcare, law, software engineering, employment, finance, psychiatry), establishes that correctness failures are cost categories whose externalisation current industry accounting obscures.

A case study of AI medical scribes demonstrates the condition-satisfaction paradox: a deployment where the AI's raw error rate is 70% produces measurable institutional value because the deployment architecture satisfies all five conditions, while also revealing the structural vulnerability of that satisfaction to accountability drift.

## Figure

![The Tunnel Pipeline — Same structure, different material](PARIA_Framework.jpg)

## Series

This is Paper 3 in the open-ended **Training Landscape** series:

1. **Uncertainty Collapse** — Architectural substrate analysis. [DOI: 10.5281/zenodo.19482051](https://doi.org/10.5281/zenodo.19482051)
2. **The Judgment Paradox** — Annotation methodology and the Rich Annotation Object. [DOI: 10.5281/zenodo.19594378](https://doi.org/10.5281/zenodo.19594378)
3. **The Tunnel Pipeline** — Structural conditions on the judgment step (this paper). [DOI: 10.5281/zenodo.19804186](https://doi.org/10.5281/zenodo.19804186)

## Building

The HTML reading shell is self-contained. To rebuild from updated markdown:

```bash
node scripts/build-paper.mjs the-tunnel-pipeline.md the-tunnel-pipeline.html --template scripts/paper-template.html
```

See `scripts/build-paper.mjs` header for markdown conventions.

## Citation

```bibtex
@article{phan2026tunnel,
  title     = {The Tunnel Pipeline: What Gets Lost, What It Costs, and the Case for PARIA},
  author    = {Phan, Ivan},
  year      = {2026},
  month     = {4},
  doi       = {10.5281/zenodo.19804186},
  publisher = {Zenodo},
  license   = {CC BY 4.0},
  note      = {Training Landscape series, Paper 3}
}
```

## Methodology

Developed through structured human-AI collaboration. Methodology and model versions in §14 of the paper. Editorial authority and accountability: the human author alone.
