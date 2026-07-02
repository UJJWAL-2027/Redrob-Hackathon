# Redrob Weighted Rank Fusion Analysis

Weights: Ujjwal 0.50, Ravi 0.30, Ritu 0.20. Missing candidates receive rank 150.

## Overlap

- Unique candidates across inputs: 203
- Present in all three: 18
- Pairwise overlap: Ujjwal/Ravi 47, Ujjwal/Ritu 33, Ravi/Ritu 35
- Final 100 consensus: all three 18, two sources 57, one source 25

## Top 20

| final_rank | candidate_id | fused_rank | rank_ujjwal | rank_ravi | rank_ritu | source_count |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | CAND_0018499 | 3.0 | 1 | 7 | 2 | 3 |
| 2 | CAND_0081846 | 5.2 | 2 | 6 | 12 | 3 |
| 3 | CAND_0055905 | 7.7 | 11 | 2 | 8 | 3 |
| 4 | CAND_0071974 | 8.8 | 4 | 18 | 7 | 3 |
| 5 | CAND_0068811 | 21.1 | 12 | 41 | 14 | 3 |
| 6 | CAND_0079387 | 23.9 | 36 | 13 | 10 | 3 |
| 7 | CAND_0088025 | 24.8 | 24 | 30 | 19 | 3 |
| 8 | CAND_0046525 | 26.4 | 29 | 23 | 25 | 3 |
| 9 | CAND_0037566 | 27.0 | 3 | 61 | 36 | 3 |
| 10 | CAND_0046064 | 28.4 | 54 | 4 | 1 | 3 |
| 11 | CAND_0007411 | 36.9 | 9 | 8 | 150 | 2 |
| 12 | CAND_0074735 | 37.6 | 23 | 35 | 78 | 3 |
| 13 | CAND_0011687 | 38.4 | 48 | 34 | 21 | 3 |
| 14 | CAND_0042506 | 39.8 | 10 | 16 | 150 | 2 |
| 15 | CAND_0096142 | 40.8 | 46 | 24 | 53 | 3 |
| 16 | CAND_0053591 | 42.6 | 17 | 51 | 94 | 3 |
| 17 | CAND_0042029 | 47.5 | 5 | 50 | 150 | 2 |
| 18 | CAND_0044855 | 51.2 | 31 | 19 | 150 | 2 |
| 19 | CAND_0075439 | 51.3 | 27 | 26 | 150 | 2 |
| 20 | CAND_0041568 | 51.4 | 41 | 3 | 150 | 2 |

## Newly Introduced vs Ujjwal

| final_rank | candidate_id | fused_rank | rank_ravi | rank_ritu | source_count |
| --- | --- | --- | --- | --- | --- |
| 61 | CAND_0050876 | 89.4 | 38 | 15 | 2 |
| 65 | CAND_0005260 | 93.1 | 9 | 77 | 2 |
| 66 | CAND_0057563 | 93.3 | 43 | 27 | 2 |
| 67 | CAND_0086022 | 94.1 | 53 | 16 | 2 |
| 70 | CAND_0008425 | 94.9 | 11 | 83 | 2 |
| 74 | CAND_0070398 | 99.1 | 55 | 38 | 2 |
| 77 | CAND_0052682 | 100.8 | 70 | 24 | 2 |
| 81 | CAND_0037980 | 102.7 | 85 | 11 | 2 |
| 83 | CAND_0081053 | 103.5 | 65 | 45 | 2 |
| 87 | CAND_0043228 | 105.2 | 74 | 40 | 2 |
| 89 | CAND_0075249 | 106.5 | 45 | 90 | 2 |
| 91 | CAND_0078002 | 106.8 | 84 | 33 | 2 |
| 94 | CAND_0027691 | 107.8 | 94 | 23 | 2 |
| 97 | CAND_0055992 | 109.5 | 15 | 150 | 1 |
| 99 | CAND_0033861 | 110.1 | 17 | 150 | 1 |

## Dropped from Ujjwal

| candidate_id | original_rank | fused_rank | rank_ravi | rank_ritu |
| --- | --- | --- | --- | --- |
| CAND_0038206 | 72 | 111.0 | 150 | 150 |
| CAND_0036121 | 76 | 113.0 | 150 | 150 |
| CAND_0047521 | 81 | 115.5 | 150 | 150 |
| CAND_0060538 | 82 | 116.0 | 150 | 150 |
| CAND_0010541 | 83 | 116.5 | 150 | 150 |
| CAND_0076831 | 84 | 117.0 | 150 | 150 |
| CAND_0007596 | 85 | 117.5 | 150 | 150 |
| CAND_0034164 | 86 | 118.0 | 150 | 150 |
| CAND_0050553 | 87 | 118.5 | 150 | 150 |
| CAND_0030784 | 88 | 119.0 | 150 | 150 |
| CAND_0033179 | 93 | 121.5 | 150 | 150 |
| CAND_0068932 | 94 | 122.0 | 150 | 150 |
| CAND_0083852 | 97 | 123.5 | 150 | 150 |
| CAND_0015057 | 99 | 124.5 | 150 | 150 |
| CAND_0054546 | 100 | 125.0 | 150 | 150 |

## Possible Risky Additions

| final_rank | candidate_id | fused_rank | source_count | risk |
| --- | --- | --- | --- | --- |
| 61 | CAND_0050876 | 89.4 | 2 | high notice period, plausibility concern |
| 66 | CAND_0057563 | 93.3 | 2 | plausibility concern |
| 67 | CAND_0086022 | 94.1 | 2 | high notice period |
| 70 | CAND_0008425 | 94.9 | 2 | high notice period |
| 74 | CAND_0070398 | 99.1 | 2 | high notice period |
| 77 | CAND_0052682 | 100.8 | 2 | plausibility concern |
| 81 | CAND_0037980 | 102.7 | 2 | high notice period, plausibility concern |
| 83 | CAND_0081053 | 103.5 | 2 | high notice period |
| 91 | CAND_0078002 | 106.8 | 2 | plausibility concern |
| 97 | CAND_0055992 | 109.5 | 1 | single-source selection |
| 99 | CAND_0033861 | 110.1 | 1 | single-source selection, stale activity, plausibility concern |

Final CSV: `outputs/ensemble_submission.csv`
