"""Rankings tables (formerly Fighter_stats_database_v2)."""

import pandas as pd


def p4p_rankings() -> pd.DataFrame:
    data = [
        [1, "Islam Makhachev", "WW", "28-1-0", 432],
        [2, "Ilia Topuria", "LW", "17-0-0", 361],
        [3, "Joshua Van", "FLW", "17-2-0", 311],
        [4, "Sean Strickland", "MW", "31-7-0", 231],
        [5, "Petr Yan", "BW", "20-5-0", 224],
        [6, "Khamzat Chimaev", "MW", "15-1-0", 222],
        [7, "Alex Pereira", "LHW", "13-3-0", 221],
        [8, "Merab Dvalishvili", "BW", "21-5-0", 164],
        [9, "Alexander Volkanovski", "FW", "28-4-0", 159],
        [10, "Dricus Du Plessis", "MW", "23-3-0", 138],
        [11, "Alexandre Pantoja", "FLW", "30-6-0", 138],
        [12, "Nassourdine Imavov", "MW", "17-4-0", 133],
        [13, "Charles Oliveira", "LW", "37-11-0", 124],
        [14, "Magomed Ankalaev", "LHW", "21-2-1", 119],
        [15, "Carlos Ulberg", "LHW", "14-1-0", 119],
    ]
    return pd.DataFrame(
        data, columns=["Rank", "Fighter", "Division", "Record", "Points"]
    )


def division_point_dominance() -> pd.DataFrame:
    data = [
        [1, "MM", "Joshua Van", "FLW", "17-2-0", 791],
        [2, "RU", "Petr Yan", "BW", "20-5-0", 774],
        [3, "US", "Merab Dvalishvili", "BW", "21-5-0", 705],
        [4, "US", "Sean Strickland", "MW", "31-7-0", 545],
        [5, "AU", "Alexander Volkanovski", "FW", "28-4-0", 544],
        [6, "AE", "Khamzat Chimaev", "MW", "15-1-0", 541],
        [7, "ES", "Ilia Topuria", "LW", "17-0-0", 518],
        [8, "BR", "Charles Oliveira", "LW", "37-11-0", 518],
        [9, "BR", "Alex Pereira", "LHW", "13-3-0", 510],
        [10, "ZA", "Dricus Du Plessis", "MW", "23-3-0", 505],
    ]
    return pd.DataFrame(
        data,
        columns=["Rank", "Country", "Fighter", "Division", "Record", "Points"],
    )
