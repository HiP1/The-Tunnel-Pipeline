# The Tunnel Pipeline

**What Gets Lost, What It Costs, and the Case for PARIA**

*Ivan Phan (HiP) · Independent Researcher · ORCID [0009-0003-1095-5855](https://orcid.org/0009-0003-1095-5855)*

**DOI:** [10.5281/zenodo.19804186](https://doi.org/10.5281/zenodo.19804186) · **Licence:** CC BY 4.0 · **Series:** Training Landscape, Paper 3

---

## Read the paper

**[Read online (HTML)](https://hip1.github.io/The-Tunnel-Pipeline/the-tunnel-pipeline.html)** · [Download PDF](the-tunnel-pipeline.pdf) · [Markdown source](the-tunnel-pipeline.md)

---

## Summary

AI adoption is accelerating at unprecedented scale, with major platforms collectively serving billions of weekly users. The question is no longer whether AI will be deployed but whether the judgment pipelines that train and evaluate it are structurally sound.

Every AI training pipeline contains a judgment pipeline: the chain of events from criterion selection through evaluator judgment to training-signal aggregation and weight update. This paper identifies five structural conditions the judgment pipeline must satisfy for deployment to create value rather than externalise cost. Collectively the **PARIA framework**:

- **P**reservation — Does the verdict record carry the judgment's epistemic content forward intact?
- **A**dequacy — Does the criterion measure the right property on the right slice of cases?
- **R**eproducibility — Are verdicts stable under criterion-irrelevant context variation?
- **I**ndependence — Do the evaluator's error modes overlap with the producer's?
- **A**ccountability — Does the feedback structure generate corrective pressure proportional to deployment scale?

Non-redundancy is demonstrated by counterexample. A seven-class cross-pipeline diagnostic grounds the framework in peer-reviewed independent evaluations. Under autoregressive transformers, condition failures map to documented deployment pathologies: sycophancy, fabrication, reward hacking, proxy collapse, and calibration collapse.

The economic argument has two sides. The cost side, grounded in the OECD's Value of Statistical Life methodology and measured data across six domains (healthcare, law, software engineering, employment, finance, psychiatry), establishes that correctness failures are cost categories whose externalisation current industry accounting obscures. The value side is developed through a case study of AI medical scribes: a deployment where the AI's raw error rate is 70% produces measurable institutional value (29% documentation time reduction, 21% burnout reduction) because the deployment architecture satisfies all five conditions, while also revealing the structural vulnerability of that satisfaction to accountability drift.

The conditions are not aspirational: formal-verification pipelines and architecturally sound deployments already satisfy them. The framework specifies what the broader landscape needs to deliver for AI adoption to produce the value the technology makes possible.

## Figure

![The Tunnel Pipeline — Same structure, different material](PARIA_Framework.jpg)

*Left: current training pipelines with opaque material blocking signals, producing proxy collapse, sycophancy, reward hacking, fabrication, and calibration collapse. Right: PARIA conditions satisfied, transparent material preserving signal integrity through to the verdict record.*

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

See `scripts/build-paper.mjs` header for markdown conventions (argumentative labels, verdict-glyph tables, `==highlight==` syntax, reading guide blocks, AI note blocks).

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

Developed through structured human-AI collaboration using the adversarial triad methodology. Claude Opus 4.7 (outline), Claude Opus 4.6 (Weaver/prose), ChatGPT 5.4 Thinking (Surgeon/structural review), Gemini 3.1 Pro (Alchemist/mechanistic review). Editorial authority and accountability: the human author alone. Full methodology in §14.
