# Contributing

Thanks for contributing to **chocosales-analyser**. Contributions include code, documentation, bug reports, and feedback.

## Report bugs / request changes
Please open an issue in this repository:
- https://github.com/UBC-MDS/DSCI-532_2026_17_chocosales-analyser/issues

When filing an issue, include:
- what you expected to happen
- what actually happened
- steps to reproduce (screenshots if helpful)

## Git workflow (required for this course)

### Branches
- **Do not push directly to `main`.**
- Create a feature branch for your work:

```bash
git checkout main
git pull
git checkout -b <branch-name>
```

## Commits
- Make atomic commits (one meaningful change per commit).
- Use imperative commit messages (e.g., “Add EDA notebook”, “Fix parsing of Amount”).

## Pull Requests (PRs)
- All changes must be merged via a PR into `main`.
- PRs should have one clear goal and a short description of what changed.
- Request at least one teammate review before merging.
- Squash and merge is recommended for a clean history.

## Local development

### Setup
Follow the project `README.md` for the most up-to-date instructions. Typical setup:

```bash
git clone https://github.com/UBC-MDS/DSCI-532_2026_17_chocosales-analyser.git
cd DSCI-532_2026_17_chocosales-analyser
conda env create -f environment.yml
conda activate chocosales-analyser
```

## Run the app

See `README.md` for the exact command for the dashboard framework used in this project.

## Data guidelines

- Keep raw data in `data/raw/`.
- Save processed outputs in `data/processed/` (only commit small/needed files).
- Avoid committing large files or secrets.

## Release workflow (milestones)

For each milestone, we create a GitHub Release:

- M1: `v0.1.0`, M2: `v0.2.0`, M3: `v0.3.0`, M4: `v0.4.0`

Include short release notes with headings like `## Added`, `## Fixed`.

## Attribution

Adapted from the DSCI 524 dumbpy CONTRIBUTING template: https://github.com/UBC-MDS/dumbpy/blob/main/CONTRIBUTING.md