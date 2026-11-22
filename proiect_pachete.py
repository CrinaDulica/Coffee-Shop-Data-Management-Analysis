import pandas as pd
import numpy as np

df_date = pd.read_csv("directory.csv")
coduri_tari_europene = [
    "FR", "DE", "IT", "ES", "UK", "GB", "RU", "GR", "NL", "BG", "BE", "PL",
    "RO", "CH", "SK", "SE", "NO", "FI", "AT", "PT", "IE", "CZ", "HU"
]
df_europa = df_date[df_date["Country"].isin(coduri_tari_europene)]
df_europa_filtrat = df_europa[["Country", "Ownership Type", "Latitude", "Longitude", "City"]]
df_europa_filtrat = df_europa_filtrat.rename(columns={
    "Country": "countrycode",
    "Ownership Type": "ownershiptypecode",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "City": "city"
})
np.random.seed(42)
df_europa_filtrat["sales"] = np.random.uniform(50, 150, len(df_europa_filtrat)).round(2)
df_europa_filtrat["costs"] = np.random.uniform(20, 100, len(df_europa_filtrat)).round(2)
df_europa_filtrat["satisfaction"] = np.random.uniform(6, 10, len(df_europa_filtrat)).round(2)
df_europa_filtrat["storesize"] = np.random.uniform(50, 300, len(df_europa_filtrat)).round(2)
df_europa_filtrat.to_csv("starbucks_date_complete.csv", index=False)
print("S-a realizat fisierul starbucks_date_complete.csv")
print(df_europa_filtrat.head())