import csv
import datetime
from collections import defaultdict
import matplotlib.pyplot as plt

# Fișierul unde se salvează datele
FILE_NAME = "tranzactii.csv"

# Structura unui rând: data, tip (incasare/cheltuiala), suma, cont, categorie, descriere

# Inițializare fișier dacă nu există
try:
    open(FILE_NAME, "x").close()
except FileExistsError:
    pass

def adauga_tranzactie(tip, suma, cont, categorie, descriere=""):
    data = datetime.date.today().isoformat()
    with open(FILE_NAME, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([data, tip, suma, cont, categorie, descriere])
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


def statistici():
    tranzactii = incarca_tranzactii()
    balante = defaultdict(float)
    cheltuieli_totale = 0
    incasari_totale = 0

    for t in tranzactii:
        if t["tip"] == "incasare":
            balante[t["cont"]] += t["suma"]
            incasari_totale += t["suma"]
        elif t["tip"] == "cheltuiala":
            balante[t["cont"]] -= t["suma"]
            cheltuieli_totale += t["suma"]

    print("===== Statistici =====")
    print(f"Incasari totale: {incasari_totale} RON")
    print(f"Cheltuieli totale: {cheltuieli_totale} RON")
    print("--- Balanta conturi ---")
    for cont, suma in balante.items():
        print(f"{cont}: {suma:.2f} RON")
    print(f"Total general: {sum(balante.values()):.2f} RON")


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


# Exemplu de utilizare
if __name__ == "__main__":
    while True:
        print("\n1. Adauga incasare")
        print("2. Adauga cheltuiala")
        print("3. Vezi statistici generale")
        print("4. Statistici lunare")
        print("5. Statistici saptamanale")
        print("6. Grafic cheltuieli pe categorii")
        print("7. Grafic balanta lunara")
        print("8. Iesire")
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
            break
        else:
            print("Optiune invalida!")
