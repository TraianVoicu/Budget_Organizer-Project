import csv
import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import json
import os

# Fișierele unde se salvează datele
FILE_NAME = "tranzactii.csv"
FILE_CONTURI = "conturi.json"

# Structura unui rând în CSV: data, tip (incasare/cheltuiala), suma, cont, categorie, descriere

# Inițializare fișier CSV dacă nu există
try:
    open(FILE_NAME, "x").close()
except FileExistsError:
    pass

# === GESTIONARE CONTURI ===
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

def afiseaza_conturi():
    conturi = incarca_conturi()
    print("=== Solduri curente ===")
    for cont, suma in conturi.items():
        print(f"{cont}: {suma:.2f} RON")
    print(f"Total general: {sum(conturi.values()):.2f} RON")

# Funcții pentru administrarea conturilor
def adauga_cont():
    conturi = incarca_conturi()
    nume = input("Nume cont: ")
    if nume in conturi:
        print("Contul există deja!")
        return
    try:
        sold = float(input("Sold inițial: "))
    except ValueError:
        print("Valoare invalidă!")
        return
    conturi[nume] = sold
    salveaza_conturi(conturi)
    print("Cont adăugat cu succes!")

def editeaza_cont():
    conturi = incarca_conturi()
    afiseaza_conturi()
    nume = input("Introduceți numele contului de editat: ")
    if nume not in conturi:
        print("Contul nu există!")
        return
    try:
        sold = float(input("Noul sold: "))
    except ValueError:
        print("Valoare invalidă!")
        return
    conturi[nume] = sold
    salveaza_conturi(conturi)
    print("Cont actualizat!")

def sterge_cont():
    conturi = incarca_conturi()
    afiseaza_conturi()
    nume = input("Introduceți numele contului de șters: ")
    if nume not in conturi:
        print("Contul nu există!")
        return
    
    if conturi[nume] != 0:
        confirm = input(f"⚠️ Contul '{nume}' are sold {conturi[nume]:.2f} RON. Sigur vrei să-l ștergi? (da/nu): ")
        if confirm.lower() != "da":
            print("Operațiune anulată.")
            return
    
    del conturi[nume]
    salveaza_conturi(conturi)
    print("Cont șters cu succes!")


# === GESTIONARE TRANZACȚII ===
def adauga_tranzactie(tip, suma, cont, categorie, descriere=""):
    data = datetime.date.today().isoformat()
    with open(FILE_NAME, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([data, tip, suma, cont, categorie, descriere])
    actualizeaza_conturi(tip, suma, cont)
    print("Tranzacție adăugată!")

def incarca_tranzactii():
    tranzactii = []
    try:
        with open(FILE_NAME, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    data, tip, suma, cont, categorie, descriere = row
                    tranzactii.append({
                        "data": datetime.date.fromisoformat(data),
                        "tip": tip,
                        "suma": float(suma),
                        "cont": cont,
                        "categorie": categorie,
                        "descriere": descriere
                    })
    except FileNotFoundError:
        pass
    return tranzactii

# === STATISTICI ===
def statistici():
    tranzactii = incarca_tranzactii()
    cheltuieli_totale = 0
    incasari_totale = 0

    for t in tranzactii:
        if t["tip"] == "incasare":
            incasari_totale += t["suma"]
        elif t["tip"] == "cheltuiala":
            cheltuieli_totale += t["suma"]

    print("===== Statistici =====")
    print(f"Incasari totale: {incasari_totale} RON")
    print(f"Cheltuieli totale: {cheltuieli_totale} RON")
    afiseaza_conturi()

def statistici_lunare():
    tranzactii = incarca_tranzactii()
    pe_luna = defaultdict(lambda: {"incasari": 0, "cheltuieli": 0})
    for t in tranzactii:
        luna = t["data"].strftime("%Y-%m")
        if t["tip"] == "incasare":
            pe_luna[luna]["incasari"] += t["suma"]
        else:
            pe_luna[luna]["cheltuieli"] += t["suma"]

    print("===== Statistici lunare =====")
    for luna, valori in sorted(pe_luna.items()):
        print(f"{luna}: Incasari={valori['incasari']} RON, Cheltuieli={valori['cheltuieli']} RON")

def statistici_saptamanale():
    tranzactii = incarca_tranzactii()
    pe_sapt = defaultdict(lambda: {"incasari": 0, "cheltuieli": 0})
    for t in tranzactii:
        year, week, _ = t["data"].isocalendar()
        sapt = f"{year}-W{week}"
        if t["tip"] == "incasare":
            pe_sapt[sapt]["incasari"] += t["suma"]
        else:
            pe_sapt[sapt]["cheltuieli"] += t["suma"]

    print("===== Statistici saptamanale =====")
    for sapt, valori in sorted(pe_sapt.items()):
        print(f"{sapt}: Incasari={valori['incasari']} RON, Cheltuieli={valori['cheltuieli']} RON")

# === GRAFICE ===
def grafic_cheltuieli_pe_categorii():
    tranzactii = incarca_tranzactii()
    categorii = defaultdict(float)
    for t in tranzactii:
        if t["tip"] == "cheltuiala":
            categorii[t["categorie"]] += t["suma"]

    plt.pie(categorii.values(), labels=categorii.keys(), autopct="%1.1f%%")
    plt.title("Distribuția cheltuielilor pe categorii")
    plt.show()

def grafic_balanta_lunara():
    tranzactii = incarca_tranzactii()
    pe_luna = defaultdict(float)
    for t in tranzactii:
        luna = t["data"].strftime("%Y-%m")
        if t["tip"] == "incasare":
            pe_luna[luna] += t["suma"]
        else:
            pe_luna[luna] -= t["suma"]

    luni = sorted(pe_luna.keys())
    valori = [pe_luna[l] for l in luni]
    plt.bar(luni, valori)
    plt.title("Balanta lunara")
    plt.ylabel("RON")
    plt.xticks(rotation=45)
    plt.show()

# === MENIU PRINCIPAL ===
if __name__ == "__main__":
    while True:
        print("\n1. Adauga incasare")
        print("2. Adauga cheltuiala")
        print("3. Vezi statistici generale")
        print("4. Statistici lunare")
        print("5. Statistici saptamanale")
        print("6. Grafic cheltuieli pe categorii")
        print("7. Grafic balanta lunara")
        print("8. Vezi solduri curente")
        print("9. Adauga cont")
        print("10. Editeaza cont")
        print("11. Sterge cont")
        print("12. Iesire")
        opt = input("> ")

        if opt == "1":
            suma = float(input("Suma: "))
            cont = input("Cont: ")
            categorie = input("Categorie: ")
            desc = input("Descriere (optional): ")
            adauga_tranzactie("incasare", suma, cont, categorie, desc)
        elif opt == "2":
            suma = float(input("Suma: "))
            cont = input("Cont: ")
            categorie = input("Categorie: ")
            desc = input("Descriere (optional): ")
            adauga_tranzactie("cheltuiala", suma, cont, categorie, desc)
        elif opt == "3":
            statistici()
        elif opt == "4":
            statistici_lunare()
        elif opt == "5":
            statistici_saptamanale()
        elif opt == "6":
            grafic_cheltuieli_pe_categorii()
        elif opt == "7":
            grafic_balanta_lunara()
        elif opt == "8":
            afiseaza_conturi()
        elif opt == "9":
            adauga_cont()
        elif opt == "10":
            editeaza_cont()
        elif opt == "11":
            sterge_cont()
        elif opt == "12":
            break
        else:
            print("Optiune invalida!")
