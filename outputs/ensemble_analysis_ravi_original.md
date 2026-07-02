# Redrob Weighted Rank Fusion Analysis

Weights: Ravi 0.50, Ujjwal 0.30, Ritu 0.20. Missing candidates receive rank 150.

## Overlap

- Unique candidates across inputs: 203
- Present in all three: 18
- Pairwise overlap: Ujjwal/Ravi 47, Ujjwal/Ritu 33, Ravi/Ritu 35
- Final 100 consensus: all three 18, two sources 57, one source 25

## Top 20

| final_rank | candidate_id | fused_rank | rank_ujjwal | rank_ravi | rank_ritu | source_count |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | CAND_0018499 | 4.2 | 1 | 7 | 2 | 3 |
| 2 | CAND_0055905 | 5.9 | 11 | 2 | 8 | 3 |
| 3 | CAND_0081846 | 6.0 | 2 | 6 | 12 | 3 |
| 4 | CAND_0071974 | 11.6 | 4 | 18 | 7 | 3 |
| 5 | CAND_0046064 | 18.4 | 54 | 4 | 1 | 3 |
| 6 | CAND_0079387 | 19.3 | 36 | 13 | 10 | 3 |
| 7 | CAND_0046525 | 25.2 | 29 | 23 | 25 | 3 |
| 8 | CAND_0088025 | 26.0 | 24 | 30 | 19 | 3 |
| 9 | CAND_0068811 | 26.9 | 12 | 41 | 14 | 3 |
| 10 | CAND_0011687 | 35.6 | 48 | 34 | 21 | 3 |
| 11 | CAND_0096142 | 36.4 | 46 | 24 | 53 | 3 |
| 12 | CAND_0007411 | 36.7 | 9 | 8 | 150 | 2 |
| 13 | CAND_0037566 | 38.6 | 3 | 61 | 36 | 3 |
| 14 | CAND_0074735 | 40.0 | 23 | 35 | 78 | 3 |
| 15 | CAND_0042506 | 41.0 | 10 | 16 | 150 | 2 |
| 16 | CAND_0005649 | 43.7 | 44 | 1 | 150 | 2 |
| 17 | CAND_0041568 | 43.8 | 41 | 3 | 150 | 2 |
| 18 | CAND_0083307 | 48.0 | 40 | 12 | 150 | 2 |
| 19 | CAND_0041669 | 48.1 | 37 | 14 | 150 | 2 |
| 20 | CAND_0044883 | 48.5 | 45 | 10 | 150 | 2 |

## Newly Introduced vs Ravi

| final_rank | candidate_id | fused_rank | rank_ravi | rank_ritu | source_count |
| --- | --- | --- | --- | --- | --- |
| 49 | CAND_0075574 | 83.3 | 150 | 31 | 2 |
| 66 | CAND_0011432 | 92.8 | 150 | 41 | 2 |
| 68 | CAND_0098846 | 93.6 | 150 | 66 | 2 |
| 73 | CAND_0081852 | 95.6 | 150 | 64 | 2 |
| 75 | CAND_0098217 | 96.8 | 150 | 13 | 2 |
| 78 | CAND_0006418 | 98.2 | 150 | 71 | 2 |
| 79 | CAND_0004402 | 98.5 | 150 | 17 | 2 |
| 83 | CAND_0002025 | 102.3 | 150 | 18 | 2 |
| 84 | CAND_0043860 | 102.8 | 150 | 22 | 2 |
| 91 | CAND_0091909 | 105.3 | 150 | 48 | 2 |
| 94 | CAND_0093547 | 107.4 | 150 | 150 | 1 |
| 98 | CAND_0043637 | 108.9 | 150 | 54 | 2 |
| 100 | CAND_0037000 | 109.5 | 150 | 150 | 1 |

## Dropped from Ravi

| candidate_id | original_rank | fused_rank | rank_ujjwal | rank_ritu |
| --- | --- | --- | --- | --- |
| CAND_0092278 | 71 | 110.5 | 150 | 150 |
| CAND_0018722 | 72 | 111.0 | 150 | 150 |
| CAND_0017960 | 75 | 112.5 | 150 | 150 |
| CAND_0053695 | 78 | 114.0 | 150 | 150 |
| CAND_0026532 | 79 | 114.5 | 150 | 150 |
| CAND_0066376 | 80 | 115.0 | 150 | 150 |
| CAND_0070202 | 81 | 115.5 | 150 | 150 |
| CAND_0061655 | 83 | 116.5 | 150 | 150 |
| CAND_0076904 | 86 | 118.0 | 150 | 150 |
| CAND_0047721 | 87 | 118.5 | 150 | 150 |
| CAND_0095528 | 90 | 120.0 | 150 | 150 |
| CAND_0052335 | 96 | 123.0 | 150 | 150 |
| CAND_0006557 | 100 | 125.0 | 150 | 150 |

## Possible Risky Additions

| final_rank | candidate_id | fused_rank | source_count | risk |
| --- | --- | --- | --- | --- |
| 73 | CAND_0081852 | 95.6 | 2 | low response rate |
| 94 | CAND_0093547 | 107.4 | 1 | single-source selection |
| 100 | CAND_0037000 | 109.5 | 1 | single-source selection |

Final CSV: `outputs/ensemble_submission_ravi_original.csv`
