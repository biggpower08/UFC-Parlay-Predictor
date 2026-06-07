# Leakage Report

Input folder: `data\imports`
Files scanned: 13

## data\imports\cadelueker__ufc-fighter-and-fight-stats-as-of-04-9-2025\enhanced_fights.csv
- Columns: 30
- Summary: `{"label_only": 3, "leakage_excluded": 2, "runtime_available": 12, "unknown_review_needed": 13}`
- Blocked/label-only columns: outcome, winner, loser, method, method_details

## data\imports\cadelueker__ufc-fighter-and-fight-stats-as-of-04-9-2025\fighters.csv
- Columns: 5
- Summary: `{"runtime_available": 3, "unknown_review_needed": 2}`

## data\imports\cadelueker__ufc-fighter-and-fight-stats-as-of-04-9-2025\fights.csv
- Columns: 19
- Summary: `{"label_only": 3, "leakage_excluded": 2, "runtime_available": 1, "unknown_review_needed": 13}`
- Blocked/label-only columns: outcome, winner, loser, method, method_details

## data\imports\jerzyszocik__ufc-betting-odds-daily-dataset\UFC_betting_odds.csv
- Columns: 17
- Summary: `{"unknown_review_needed": 17}`

## data\imports\jerzyszocik__ufc-fight-forecast-complete-gold-modeling-dataset\UFC_full_data_golden.csv
- Columns: 5437
- Summary: `{"label_only": 4, "leakage_excluded": 130, "runtime_available": 529, "unknown_review_needed": 4774}`
- Blocked/label-only columns: winner, result, result_details, finish_round, finish_time, f_1_total_strikes_att, f_1_total_strikes_succ, f_1_sig_strikes_att, f_1_sig_strikes_succ, f_1_takedown_att, f_1_takedown_succ, f_1_ctrl_time_sec, f_2_total_strikes_att, f_2_total_strikes_succ, f_2_sig_strikes_att, f_2_sig_strikes_succ, f_2_takedown_att, f_2_takedown_succ, f_2_ctrl_time_sec, f_1_r1_sig_strikes_succ ...

## data\imports\jerzyszocik__ufc-fight-forecast-complete-gold-modeling-dataset\UFC_full_data_silver.csv
- Columns: 361
- Summary: `{"label_only": 4, "leakage_excluded": 65, "runtime_available": 29, "unknown_review_needed": 263}`
- Blocked/label-only columns: winner, result, result_details, finish_round, finish_time, f_1_total_strikes_att, f_1_total_strikes_succ, f_1_sig_strikes_att, f_1_sig_strikes_succ, f_1_takedown_att, f_1_takedown_succ, f_1_ctrl_time_sec, f_2_total_strikes_att, f_2_total_strikes_succ, f_2_sig_strikes_att, f_2_sig_strikes_succ, f_2_takedown_att, f_2_takedown_succ, f_2_ctrl_time_sec, f_1_r1_sig_strikes_succ ...

## data\imports\kaggle\jerzyszocik__ufc-betting-odds-daily-dataset\UFC_betting_odds.csv
- Columns: 17
- Summary: `{"unknown_review_needed": 17}`

## data\imports\kaggle\jerzyszocik__ufc-fight-forecast-complete-gold-modeling-dataset\UFC_full_data_golden.csv
- Columns: 5437
- Summary: `{"label_only": 4, "leakage_excluded": 130, "runtime_available": 529, "unknown_review_needed": 4774}`
- Blocked/label-only columns: winner, result, result_details, finish_round, finish_time, f_1_total_strikes_att, f_1_total_strikes_succ, f_1_sig_strikes_att, f_1_sig_strikes_succ, f_1_takedown_att, f_1_takedown_succ, f_1_ctrl_time_sec, f_2_total_strikes_att, f_2_total_strikes_succ, f_2_sig_strikes_att, f_2_sig_strikes_succ, f_2_takedown_att, f_2_takedown_succ, f_2_ctrl_time_sec, f_1_r1_sig_strikes_succ ...

## data\imports\kaggle\jerzyszocik__ufc-fight-forecast-complete-gold-modeling-dataset\UFC_full_data_silver.csv
- Columns: 361
- Summary: `{"label_only": 4, "leakage_excluded": 65, "runtime_available": 29, "unknown_review_needed": 263}`
- Blocked/label-only columns: winner, result, result_details, finish_round, finish_time, f_1_total_strikes_att, f_1_total_strikes_succ, f_1_sig_strikes_att, f_1_sig_strikes_succ, f_1_takedown_att, f_1_takedown_succ, f_1_ctrl_time_sec, f_2_total_strikes_att, f_2_total_strikes_succ, f_2_sig_strikes_att, f_2_sig_strikes_succ, f_2_takedown_att, f_2_takedown_succ, f_2_ctrl_time_sec, f_1_r1_sig_strikes_succ ...

## data\imports\mdabbert__ultimate-ufc-dataset\ufc-master.csv
- Columns: 118
- Summary: `{"label_only": 2, "leakage_excluded": 11, "runtime_available": 43, "unknown_review_needed": 62}`
- Blocked/label-only columns: Winner, B_avg_SIG_STR_landed, B_avg_SIG_STR_pct, B_avg_SUB_ATT, R_avg_SIG_STR_landed, R_avg_SIG_STR_pct, R_avg_SUB_ATT, sig_str_dif, avg_sub_att_dif, finish, finish_details, finish_round, finish_round_time

## data\imports\mdabbert__ultimate-ufc-dataset\upcoming.csv
- Columns: 118
- Summary: `{"label_only": 2, "leakage_excluded": 11, "runtime_available": 43, "unknown_review_needed": 62}`
- Blocked/label-only columns: Winner, B_avg_SIG_STR_landed, B_avg_SIG_STR_pct, B_avg_SUB_ATT, R_avg_SIG_STR_landed, R_avg_SIG_STR_pct, R_avg_SUB_ATT, sig_str_dif, avg_sub_att_dif, finish, finish_details, finish_round, finish_round_time

## data\imports\rajaisrarkiani__ufc-fights-and-fighter-stats-dataset\Fights Data.csv
- Columns: 12
- Summary: `{"label_only": 1, "leakage_excluded": 1, "unknown_review_needed": 10}`
- Blocked/label-only columns: fight_result, method

## data\imports\rajaisrarkiani__ufc-fights-and-fighter-stats-dataset\Players Profiles.csv
- Columns: 15
- Summary: `{"runtime_available": 3, "unknown_review_needed": 12}`
