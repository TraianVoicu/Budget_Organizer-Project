import streamlit as st
import pandas as pd
import datetime
import json
import os
from collections import defaultdict
import matplotlib.pyplot as plt

FILE_NAME = "tranzactii.csv"
FILE_CONTURI = "conturi.json"

# === Functii pentru conturi ===
def incarca_conturi():
    if not os.path.exists(FILE_CONTURI):
        return {}
    with open(FILE_CONTURI, "r", encoding="utf-8") as f:
        return json.load(f)

def salveaza_conturi(conturi):
    with open(FILE_CONTURI, "w", encoding="utf-8") as f:
        json.dump(conturi, f, ensure_ascii=False, indent=2)

def actualizeaza_conturi(tip, suma, cont):
    conturi = incarca_conturi()
    if cont not in conturi:
        conturi[cont] = 0
    if tip == "incasare":
        conturi[cont] += suma
    elif tip == "cheltuiala":
        conturi[cont] -= suma
    salveaza_conturi(conturi)


def incarca_tranzactii():
    if not os.path.exists(FILE_NAME) or os.path.getsize(FILE_NAME) == 0:
        # dacă fișierul lipsește sau e gol → creăm unul cu headere
        cols = ["data", "tip", "suma", "cont", "categorie", "descriere"]
        pd.DataFrame(columns=cols).to_csv(FILE_NAME, index=False)
        return pd.DataFrame(columns=cols)
    return pd.read_csv(FILE_NAME)


def adauga_tranzactie(tip, suma, cont, categorie, descriere=""):
    data = datetime.date.today().isoformat()
    df = incarca_tranzactii()
    nou = pd.DataFrame([[data, tip, suma, cont, categorie, descriere]],
                       columns=df.columns)
    df = pd.concat([df, nou], ignore_index=True)
    df.to_csv(FILE_NAME, index=False)
    actualizeaza_conturi(tip, suma, cont)

# === Interfata Streamlit ===
st.set_page_config(page_title="Manager Financiar", layout="wide")

st.title("💰 Manager Financiar Personal")

# Sidebar pentru meniu
optiune = st.sidebar.radio("Navigare", [
    "Adauga tranzactie",
    "Vezi tranzactii",
    "Statistici",
    "Conturi"
])

if optiune == "Adauga tranzactie":
    st.header("➕ Adauga o tranzactie noua")
    tip = st.selectbox("Tip", ["incasare", "cheltuiala"])
    suma = st.number_input("Suma", min_value=0.0, step=0.1)
    cont = st.text_input("Cont")
    categorie = st.text_input("Categorie")
    descriere = st.text_area("Descriere")
    if st.button("Salveaza"):
        adauga_tranzactie(tip, suma, cont, categorie, descriere)
        st.success("Tranzactie salvata!")

elif optiune == "Vezi tranzactii":
    st.header("📄 Lista tranzactii")
    df = incarca_tranzactii()
    st.dataframe(df)

elif optiune == "Statistici":
    st.header("📊 Statistici")
    df = incarca_tranzactii()
    if not df.empty:
        total_incasari = df[df["tip"]=="incasare"]["suma"].sum()
        total_cheltuieli = df[df["tip"]=="cheltuiala"]["suma"].sum()
        st.metric("Total incasari", f"{total_incasari:.2f} RON")
        st.metric("Total cheltuieli", f"{total_cheltuieli:.2f} RON")

        # Grafic pe categorii
        cheltuieli = df[df["tip"]=="cheltuiala"].groupby("categorie")["suma"].sum()
        if not cheltuieli.empty:
            st.subheader("Distribuția cheltuielilor")
            fig, ax = plt.subplots()
            ax.pie(cheltuieli.values, labels=cheltuieli.index, autopct="%1.1f%%")
            st.pyplot(fig)
    else:
        st.info("Nu exista tranzactii salvate.")

elif optiune == "Conturi":
    st.header("🏦 Administrare conturi")
    conturi = incarca_conturi()
    st.write(conturi)

    with st.expander("➕ Adauga cont nou"):
        nume = st.text_input("Nume cont nou")
        sold = st.number_input("Sold initial", value=0.0)
        if st.button("Creeaza cont"):
            conturi[nume] = sold
            salveaza_conturi(conturi)
            st.success(f"Contul {nume} a fost creat.")

    with st.expander("✏️ Editeaza cont"):
        if conturi:
            nume_selectat = st.selectbox("Alege cont", list(conturi.keys()))
            sold_nou = st.number_input("Sold nou", value=float(conturi[nume_selectat]))
            if st.button("Salveaza modificarea"):
                conturi[nume_selectat] = sold_nou
                salveaza_conturi(conturi)
                st.success("Sold actualizat!")

    with st.expander("🗑️ Sterge cont"):
        if conturi:
            nume_selectat = st.selectbox("Alege cont pentru stergere", list(conturi.keys()))
            if conturi[nume_selectat] != 0:
                st.warning(f"⚠️ Atentie! Contul {nume_selectat} are sold {conturi[nume_selectat]:.2f} RON.")
            if st.button("Sterge cont"):
                del conturi[nume_selectat]
                salveaza_conturi(conturi)
                st.success("Cont sters.")
