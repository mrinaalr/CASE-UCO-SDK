# RECAP keyword machines, v0.0.0

`scripts/build_recap_machines.py` reads `collected/recap/{bulk,cyber,fraud,trafficking}`. One `traj:Trajectory` per case when the text contains a controlled cue. Cue order is vocabulary order, not chronology. Confidence is 40. Passages are not copied. The four graphs validate. Conforms: True.

`collected/recap/csea` is counted and not read. Close reads stay in `../`.

| Collection | PDFs | Cases | Keyword machines | Not phased |
| --- | ---: | ---: | ---: | --- |
| bulk | 506 | 499 | 70 | 4 hand-modeled, sealed 94, image-only 87, child-sexual withheld 133, no filing date 21, no cue 90 |
| fraud | 277 | 156 | 67 | 10 hand-modeled, sealed 24, image-only 5, child-sexual withheld 9, no filing date 10, no cue 31 |
| trafficking | 55 | 55 | 44 | 4 hand-modeled, no filing date 5, no cue 2 |
| cyber | 4 | 4 | 0 | all 4 hand-modeled |
| csea | 12 | 12 | 0 | withheld without reading |

`trafficking` and `cyber` here are the curated folders, not the old civil first batch. Status for every case is `manifest.json`.
