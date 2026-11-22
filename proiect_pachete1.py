import streamlit as st
import pandas as pd
import statsmodels.api as sm
import plotly.express as px
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

st.set_page_config(page_title="Starbucks", layout="wide")

def pagina_introducere():
    st.markdown(
        "<h1 style='text-align: center;'>Starbucks - Analiza companiei în Europa </h1>",
        unsafe_allow_html=True
    )

    st.markdown("""
    Într-o lume în care consumul de cafea este în continuă creștere, cafenelele au devenit o prezență constantă în peisajul urban, de la marile capitale europene până la cele mai mici orașe universitare. 
    Prea mulți tineri - in special studenți - cafeneaua nu este doar un loc unde își iau cafeaua zilnic, ci un spațiu de întâlnire, lucru sau relaxare. 

    Printre brandurile cele mai cunoscute la nivel internațional, Starbucks se remarcă printr-o rețea extinsă de locații și printr-o identitate vizuală și de brand puternic conturată. Astfel, m-am întrebat:
    Cât de bine merg magazinele si cât de prezent este Starbucks în Europa

    Această aplicație analizează distribuția și performanța Starbucks în Europa.
    """)

    st.image(
        "starbucks.png",
        width=400
    )
    st.markdown("""---""")
    st.subheader("Obiective")

    st.markdown("""
    - Vizualizarea locațiilor Starbucks  
    - Analiza performanței  
    - Grafice și statistici  
    """)





def pagina_locatii():
    df = pd.read_csv("starbucks_date_complete.csv")
    df.columns = df.columns.str.strip().str.lower()
    st.markdown('<h2 class="custom-title">Harta locațiilor Starbucks</h2>', unsafe_allow_html=True)
    country_names = {
        "FR": "Franța", "DE": "Germania", "IT": "Italia", "ES": "Spania",
        "GB": "Regatul Unit", "NL": "Olanda", "BE": "Belgia", "PL": "Polonia",
        "RO": "România", "CH": "Elveția", "SE": "Suedia", "NO": "Norvegia",
        "AT": "Austria", "PT": "Portugalia", "IE": "Irlanda", "CZ": "Cehia",
        "HU": "Ungaria"
    }
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"])
    tari_disponibile = sorted(df["countrycode"].unique())
    tara = st.selectbox("Filtrează după țară:", ["Toate"] + tari_disponibile)
    if tara != "Toate":
        df = df[df["countrycode"] == tara]
    st.write(f"Număr locații afișate: {len(df)}")

    harta_df = df[["latitude", "longitude"]].rename(columns={
        "latitude": "lat",
        "longitude": "lon"
    })
    st.map(harta_df)
    st.markdown("---")
    st.subheader("Codurile țărilor din aplicație")
    df_countries = pd.DataFrame(country_names.items(), columns=["Cod", "Țară"])
    st.table(df_countries)


def pagina_analiza_vanzari():
    df = pd.read_csv("starbucks_date_complete.csv")
    df.columns = df.columns.str.strip().str.lower()
    st.markdown('<h2 class="custom-title">Setul de date complet</h2>', unsafe_allow_html=True)
    st.dataframe(df)
    if "tratat_lipsa" not in st.session_state:
        st.session_state.tratat_lipsa = False
    if "df_curat" not in st.session_state:
        st.session_state.df_curat = None
    if st.button("Apasă pentru a trata valorile lipsă"):
        df["sales"] = df.groupby("countrycode")["sales"].transform(
            lambda x: x.fillna(x.median())
        )
        df["satisfaction"] = df.groupby("countrycode")["satisfaction"].transform(
            lambda x: x.fillna(x.mean())
        )
        df["costs"] = df["costs"].fillna(df["costs"].median())
        df["storesize"] = df["storesize"].fillna(df["storesize"].median())

        st.session_state.df_curat = df
        st.session_state.tratat_lipsa = True

        st.success("Valorile lipsă au fost tratate!")
        st.dataframe(df)
    if st.session_state.tratat_lipsa:
        df = st.session_state.df_curat.copy()
        df["profit"] = df["sales"] - df["costs"]
        st.markdown("---")
        st.subheader("Profit mediu pe țări")
        profit_pe_tari = df.groupby("countrycode")["profit"].mean().reset_index()
        fig_profit = px.bar(
            profit_pe_tari.sort_values(by="profit", ascending=False),
            x="countrycode",
            y="profit",
            labels={"countrycode": "Țară", "profit": "Profit mediu"},
            title="Profit mediu Starbucks pe țări"
        )
        st.plotly_chart(fig_profit, use_container_width=True)
        st.subheader("Satisfacția medie a clienților pe țări")
        satisfactie_pe_tari = df.groupby("countrycode")["satisfaction"].mean().reset_index()
        fig_satisfactie = px.bar(
            satisfactie_pe_tari.sort_values(by="satisfaction", ascending=False),
            x="countrycode",
            y="satisfaction",
            labels={"countrycode": "Țară", "satisfaction": "Satisfacție medie"},
            title="Nivelul mediu de satisfacție al clienților Starbucks în Europa"
        )
        st.plotly_chart(fig_satisfactie, use_container_width=True)
        st.markdown("---")
        st.subheader("Codificarea variabilei Ownership Type")
        le = LabelEncoder()
        df["ownership_encoded"] = le.fit_transform(df["ownershiptypecode"])

        st.write("Valorile unice:")
        st.write(df["ownershiptypecode"].value_counts())

        st.write("Label Encoding:")
        st.dataframe(df[["ownershiptypecode", "ownership_encoded"]].drop_duplicates())

        st.subheader("Profit mediu în funcție de tipul de proprietate")

        profit_pe_tip = df.groupby("ownershiptypecode")["profit"].mean().reset_index()

        fig_profit_tip = px.pie(
            profit_pe_tip,
            names="ownershiptypecode",
            values="profit",
            title="Distribuția profitului mediu pe tip de proprietate"
        )
        st.plotly_chart(fig_profit_tip, use_container_width=True)

        st.markdown("---")
        st.subheader("Metode de scalare")

        scaler = StandardScaler()
        scaled_values = scaler.fit_transform(df[["sales", "costs", "satisfaction"]])

        df_scaled = pd.DataFrame(
            scaled_values,
            columns=["sales_scaled", "costs_scaled", "satisfaction_scaled"]
        )

        df_comparativ = pd.concat([
            df[["sales", "costs", "satisfaction"]].reset_index(drop=True),
            df_scaled.reset_index(drop=True)
        ], axis=1)

        st.dataframe(df_comparativ.head())

        st.markdown("---")
        st.subheader("Regresie logistică")


        df["high_satisfaction"] = (df["satisfaction"] >= 8.5).astype(int)

        X = df[["sales", "costs", "storesize"]]
        y = df["high_satisfaction"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        model_log = LogisticRegression(max_iter=1000)
        model_log.fit(X_train, y_train)

        score = model_log.score(X_test, y_test)
        st.write(f"Acuratețea modelului: **{score:.2f}**")

        coef_df = pd.DataFrame({
            "Caracteristică": X.columns,
            "Coeficient": model_log.coef_[0]
        })

        st.markdown("### Coeficienții modelului logistic")
        st.dataframe(coef_df)

        y_pred = model_log.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)

        st.markdown("### Matricea de confuzie")
        fig_cm = px.imshow(
            cm,
            text_auto=True,
            color_continuous_scale="Blues",
            labels=dict(x="Valori prezise", y="Valori reale", color="Frecvență")
        )
        st.plotly_chart(fig_cm, use_container_width=True)

def pagina_regresie_multipla():
    df = pd.read_csv("starbucks_date_complete.csv")
    df.columns = df.columns.str.strip().str.lower()

    st.markdown('<h2 class="custom-title">Regresie Liniară Multiplă (OLS)</h2>', unsafe_allow_html=True)

    st.write("Setul de date:")
    st.dataframe(df.head())


    df["sales"] = df["sales"].fillna(df["sales"].median())
    df["costs"] = df["costs"].fillna(df["costs"].median())
    df["satisfaction"] = df["satisfaction"].fillna(df["satisfaction"].mean())


    df["profit"] = df["sales"] - df["costs"]


    X = df[["sales", "costs", "satisfaction"]]
    X = sm.add_constant(X)
    y = df["profit"]


    model = sm.OLS(y, X).fit()

    st.subheader("Rezumat model OLS")
    st.text(model.summary())


    coef_df = pd.DataFrame({
        "Variabilă": model.params.index,
        "Coeficient": model.params.values
    })

    st.subheader("Coeficienți")
    st.dataframe(coef_df)


    fig = px.bar(coef_df, x="Variabilă", y="Coeficient",
                 title="Influența variabilelor asupra profitului")
    st.plotly_chart(fig)
pagina = st.sidebar.radio(
    "Meniu",
    ["Home", "Locații", "Analiză vânzări", "Regresie multiplă"],
    key="meniul_principal"
)

if pagina == "Home":
    pagina_introducere()
elif pagina == "Locații":
    pagina_locatii()
elif pagina == "Analiză vânzări":
    pagina_analiza_vanzari()
elif pagina == "Regresie multiplă":
    pagina_regresie_multipla()