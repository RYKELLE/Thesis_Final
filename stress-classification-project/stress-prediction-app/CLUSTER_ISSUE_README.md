# Cluster‑Centers Path Troubleshooting

This document isolates the subset of the repository that is involved in the
"cluster_centers.csv not found" error.  It is intended to make it easier to
verify the locations of the files and understand how the app looks for them.

```
stress-classification-project/
├── data/
│   └── processed/
│       └── cluster_centers.csv           # original centroids used during
│                                         # training; located at project root
│
├── stress-prediction-app/               # Streamlit application folder
│   ├── cluster_centers.csv              # local copy, created at startup
│   ├── app/
│   │   └── streamlit_app.py             # main app script; contains logic to
│   │                                         copy and locate the CSV, collect
│   │                                         user inputs, assign clusters
│   ├── src/
│   │   └── utils/
│   │       └── data_processing.py        # helpers: encode, scale, assign
│   │                                         cluster (reads CSV path given)
│   ├── models/
│   │   └── model_config.json            # feature list including "Cluster"
│   │   └── multinomial_logreg_lifestyle_cluster.pkl  # trained model
│   └── README.md                        # general instructions (updated)
└── notebooks/                           # not directly involved but
    └── ...                              # used to generate cluster_centers
```

## How the lookup works

1. On import, `streamlit_app.py` attempts to copy
   `../data/processed/cluster_centers.csv` into the app directory.  This step
   ensures a concrete file exists next to the Streamlit script regardless of
   working directory issues.

2. When assigning a cluster, it calls `find_centers_file()` which:
   * First checks for the local copy (`stress-prediction-app/cluster_centers.csv`).
   * If absent, walks up to six levels of parent directories looking for
     `data/processed/cluster_centers.csv`.
   * Raises `FileNotFoundError` if neither location contains the file.

3. `assign_cluster()` in `data_processing.py` reads whatever path is given and
   computes the nearest centroid.

## Common failure modes

* `data/processed/cluster_centers.csv` is missing or mis‑spelled in the
  project root.
* Streaming execution sets `__file__` to a relative name, causing earlier
  path constructions to resolve to `stress-prediction-app/data/processed/...`
  (which does not exist).
* Permissions prevent copying the CSV into the app folder.

Ensure the original CSV is present and readable; the app will create a copy
automatically on startup and then use that copy for clustering.