# -*- coding: utf-8 -*-
"""
Rozwiazywanie zagadnienia brzegowego:

    u''(x) = -f(x),  u(a) = u(b) = 0

Skrypt liczy rozwiazanie analityczne przez podwojna calke oraz rozwiazanie
numeryczne metoda roznic skonczonych. Dodatkowo generuje raport tekstowy i
wykresy PNG dla kazdego zadania zdefiniowanego w ZADANIA.
"""

import numpy as np
import sympy as sp

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Konfiguracja
# ---------------------------------------------------------------------------

x_sym = sp.symbols("x")
N = 10


def _f_stala(x):
    """Funkcja f(x)=1 dzialajaca dla skalarow i tablic numpy."""
    return np.ones_like(np.asarray(x, dtype=float), dtype=float)


def _f_sin(x):
    return np.sin(np.pi * x)


def _f_liniowa(x):
    return np.asarray(x, dtype=float)


ZADANIA = [
    {
        "nr": 1,
        "a": 0.0,
        "b": 1.0,
        "f_sym": sp.Integer(1),
        "f": _f_stala,
        "etykieta_f": "1",
        "F_dane": -x_sym**2 / 2,
    },
    {
        "nr": 2,
        "a": 0.0,
        "b": 1.0,
        "f_sym": sp.sin(sp.pi * x_sym),
        "f": _f_sin,
        "etykieta_f": "sin(pi*x)",
        "F_dane": sp.sin(sp.pi * x_sym) / sp.pi**2,
    },
    {
        "nr": 3,
        "a": 0.0,
        "b": 2.0,
        "f_sym": x_sym,
        "f": _f_liniowa,
        "etykieta_f": "x",
        "F_dane": -x_sym**3 / 6,
    },
]


# ---------------------------------------------------------------------------
# Pomocnicze funkcje wypisywania raportu
# ---------------------------------------------------------------------------

SZEROKOSC = 78


def _linia(znak="-"):
    return znak * SZEROKOSC


def _naglowek(tekst):
    print()
    print(_linia("="))
    print(f"  {tekst}")
    print(_linia("="))


def _podsekcja(litera, tytul):
    print()
    print(f"[{litera}] {tytul}")
    print(_linia("-"))


def _koniec_podsekcji():
    print(_linia("-"))


def _wiersz(tekst):
    print(tekst)


def _wzor(expr):
    return sp.sstr(sp.simplify(expr))


def _liczba(expr):
    expr = sp.simplify(expr)
    if expr.is_number:
        return f"{float(expr):.8g}"
    return sp.sstr(expr)


def _wzor_u(u_expr, c1=None, c2=None):
    """Zwraca czytelny zapis u(x), z uproszczeniem gdy to mozliwe."""
    return _wzor(u_expr)


def _pokaz_macierz(A_mat, max_rozmiar=8):
    print("macierz A:")
    if A_mat.shape[0] <= max_rozmiar:
        for row in A_mat:
            print("  " + " ".join(f"{val:7.2f}" for val in row))
        return

    print(f"  rozmiar: {A_mat.shape[0]} x {A_mat.shape[1]}")
    print("  pokazano fragment lewego gornego rogu:")
    for row in A_mat[:max_rozmiar, :max_rozmiar]:
        print("  " + " ".join(f"{val:7.2f}" for val in row) + " ...")


def _pokaz_wektor(b_vec, max_rozmiar=10):
    print("wektor b:")
    if len(b_vec) <= max_rozmiar:
        print("  " + " ".join(f"{val: .6f}" for val in b_vec))
        return

    poczatek = " ".join(f"{val: .6f}" for val in b_vec[:max_rozmiar])
    print(f"  {poczatek} ...")


def _tabela(naglowki, wiersze):
    szerokosci = [len(h) for h in naglowki]
    for wiersz in wiersze:
        for i, wartosc in enumerate(wiersz):
            szerokosci[i] = max(szerokosci[i], len(str(wartosc)))

    def formatuj(wiersz):
        return " | ".join(str(wartosc).rjust(szerokosci[i]) for i, wartosc in enumerate(wiersz))

    print(formatuj(naglowki))
    print("-+-".join("-" * s for s in szerokosci))
    for wiersz in wiersze:
        print(formatuj(wiersz))


# ---------------------------------------------------------------------------
# Logika obliczeniowa
# ---------------------------------------------------------------------------

def rozwiaz_analitycznie(f_sym, a, b):
    """Wyznacza u(x) = F(x) + C1*x + C2 przez podwojna calke i warunki brzegowe."""
    x = x_sym
    F = -sp.integrate(sp.integrate(f_sym, x), x)
    C1, C2 = sp.symbols("C1 C2")
    u_ogolne = F + C1 * x + C2
    sol = sp.solve(
        [sp.Eq(u_ogolne.subs(x, a), 0), sp.Eq(u_ogolne.subs(x, b), 0)],
        [C1, C2],
    )
    u = sp.simplify(F + sol[C1] * x + sol[C2])
    return {"F": sp.simplify(F), "C1": sol[C1], "C2": sol[C2], "u": u, "x": x}


def rozwiaz_z_danego_F(F_sym, a, b):
    """Weryfikacja: wyznacza u(x) z podanego F(x) i warunkow brzegowych."""
    x = x_sym
    C1, C2 = sp.symbols("C1 C2")
    u_ogolne = F_sym + C1 * x + C2
    sol = sp.solve(
        [sp.Eq(u_ogolne.subs(x, a), 0), sp.Eq(u_ogolne.subs(x, b), 0)],
        [C1, C2],
    )
    return sp.simplify(F_sym + sol[C1] * x + sol[C2]), sol[C1], sol[C2]


def rozwiaz_dyskretnie(f_func, a, b, n_intervals):
    """
    Metoda roznic skonczonych dla -u'' = f(x), u(a)=u(b)=0.

    Schemat centraly:
        (u[i-1] - 2*u[i] + u[i+1]) / h^2 = -f(x[i])
    =>  u[i-1] - 2*u[i] + u[i+1]          =  -f(x[i]) * h^2

    Zwraca: wezly, h, macierz A, wektor b, wektor rozwiazania u.
    """
    h = (b - a) / n_intervals
    wezly = np.linspace(a, b, n_intervals + 1)
    wewnetrzne = wezly[1:-1]
    n = len(wewnetrzne)

    A_mat = np.zeros((n, n))
    b_vec = np.zeros(n)
    for i in range(n):
        A_mat[i, i] = -2.0
        if i > 0:
            A_mat[i, i - 1] = 1.0
        if i < n - 1:
            A_mat[i, i + 1] = 1.0
        b_vec[i] = -f_func(wewnetrzne[i]) * h**2

    u_wew = np.linalg.solve(A_mat, b_vec)
    u = np.zeros(n_intervals + 1)
    u[1:-1] = u_wew
    return wezly, h, A_mat, b_vec, u


def u_z_wzoru(ana, xs):
    u_func = sp.lambdify(ana["x"], ana["u"], "numpy")
    return u_func(xs)


def F_z_wzoru(ana, xs):
    F_func = sp.lambdify(ana["x"], ana["F"], "numpy")
    return F_func(xs)


def analiza_zbieznosci(zadanie, ana, lista_N):
    a, b = zadanie["a"], zadanie["b"]
    hs, bledy = [], []
    for n in lista_N:
        w, h, _, _, u_num = rozwiaz_dyskretnie(zadanie["f"], a, b, n)
        hs.append(h)
        bledy.append(np.max(np.abs(u_num - u_z_wzoru(ana, w))))
    return np.array(hs), np.array(bledy)


# ---------------------------------------------------------------------------
# Rysowanie
# ---------------------------------------------------------------------------

def rysuj_wszystkie(zadanie, wezly, u_num, ana, A_mat, n_siatki):
    """Generuje zestaw wykresow do raportu."""
    a, b = zadanie["a"], zadanie["b"]
    nr = zadanie.get("nr", 1)
    x_gladkie = np.linspace(a, b, 300)
    u_ana = u_z_wzoru(ana, x_gladkie)
    F_ana = F_z_wzoru(ana, x_gladkie)
    lista_N = [4, 8, 16, 32, 64]
    hs, bledy = analiza_zbieznosci(zadanie, ana, lista_N)
    blad_lokalny = np.abs(u_num - u_z_wzoru(ana, wezly))

    prefix = f"zad{nr}_"

    # 1) f(x) i u(x)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle(f"Zadanie {nr}: u'' = -f(x)", fontweight="bold")
    axes[0].plot(x_gladkie, zadanie["f"](x_gladkie), "g-", lw=2,
                 label=f"f(x)={zadanie['etykieta_f']}")
    axes[0].set(xlabel="x", ylabel="f(x)", title="Obciazenie")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    axes[1].plot(x_gladkie, u_ana, "b-", lw=2, label="u analityczne")
    axes[1].plot(wezly, u_num, "ro-", ms=5, label=f"u dyskretne (N={n_siatki})")
    axes[1].scatter([a, b], [0, 0], color="k", zorder=5)
    axes[1].set(xlabel="x", ylabel="u(x)", title="Rozwiazanie")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    plt.tight_layout()
    plt.savefig(f"{prefix}wykres_rozwiazanie.png", dpi=150, bbox_inches="tight")
    plt.close()

    # 2) F(x) — podwojna calka
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(x_gladkie, F_ana, "m-", lw=2, label="F(x) = -∬ f(x) dx²")
    ax.axhline(0, color="gray", lw=0.8)
    ax.set(xlabel="x", ylabel="F(x)", title="Podwojna calka F(x)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{prefix}wykres_F.png", dpi=150, bbox_inches="tight")
    plt.close()

    # 3) struktura macierzy A
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(A_mat, cmap="Blues", aspect="equal")
    ax.set(xlabel="j", ylabel="i",
           title=f"Macierz ukladu A ({A_mat.shape[0]}x{A_mat.shape[0]})")
    plt.colorbar(im, ax=ax, shrink=0.85)
    plt.tight_layout()
    plt.savefig(f"{prefix}wykres_macierz.png", dpi=150, bbox_inches="tight")
    plt.close()

    # 4) zbieznosc log-log
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.loglog(hs, bledy, "o-", lw=2, ms=7, color="steelblue", label="blad numeryczny")
    ax.loglog(hs, hs**2 * (bledy[0] / hs[0] ** 2), "k--", alpha=0.5, label="O(h²)")
    ax.set(xlabel="krok h", ylabel="max |u_num - u_dokladne|", title="Zbieznosc metody")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{prefix}wykres_zbieznosc.png", dpi=150, bbox_inches="tight")
    plt.close()

    # 5) rozne gestosci siatki
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(x_gladkie, u_ana, "k-", lw=2.5, label="u dokladne")
    for n in [4, 8, 16, 32]:
        w, _, _, _, un = rozwiaz_dyskretnie(zadanie["f"], a, b, n)
        ax.plot(w, un, "o-", ms=4, alpha=0.75, label=f"N={n}")
    ax.scatter([a, b], [0, 0], color="red", zorder=5)
    ax.set(xlabel="x", ylabel="u(x)", title="Wplyw gestosci siatki na rozwiazanie")
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{prefix}wykres_siatki.png", dpi=150, bbox_inches="tight")
    plt.close()

    # 6) blad punktowy
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.stem(wezly, blad_lokalny, linefmt="C3-", markerfmt="C3o", basefmt=" ")
    ax.set(xlabel="x", ylabel="|u_num - u_ana|",
           title=f"Blad lokalny (N={n_siatki})")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{prefix}wykres_blad.png", dpi=150, bbox_inches="tight")
    plt.close()

    # 7) panel podsumowujacy 2x3
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle(f"Podsumowanie — zadanie {nr}", fontsize=14, fontweight="bold")
    axes[0, 0].plot(x_gladkie, zadanie["f"](x_gladkie), "g-")
    axes[0, 0].set_title("f(x)")
    axes[0, 1].plot(x_gladkie, F_ana, "m-")
    axes[0, 1].set_title("F(x)")
    axes[0, 2].plot(x_gladkie, u_ana, "b-", label="ana")
    axes[0, 2].plot(wezly, u_num, "r.--", label="num")
    axes[0, 2].legend(fontsize=8)
    axes[0, 2].set_title("u(x)")
    axes[1, 0].imshow(A_mat, cmap="Blues")
    axes[1, 0].set_title("macierz A")
    axes[1, 1].loglog(hs, bledy, "o-")
    axes[1, 1].set_title("zbieznosc")
    axes[1, 2].stem(wezly, blad_lokalny, linefmt="C3-", markerfmt="C3o", basefmt=" ")
    axes[1, 2].set_title("blad lokalny")
    for ax in axes.flat:
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{prefix}wykres_podsumowanie.png", dpi=150, bbox_inches="tight")
    plt.close()

    return [
        f"{prefix}wykres_rozwiazanie.png",
        f"{prefix}wykres_F.png",
        f"{prefix}wykres_macierz.png",
        f"{prefix}wykres_zbieznosc.png",
        f"{prefix}wykres_siatki.png",
        f"{prefix}wykres_blad.png",
        f"{prefix}wykres_podsumowanie.png",
    ]


# ---------------------------------------------------------------------------
# Glowna procedura dla jednego zadania
# ---------------------------------------------------------------------------

def rozwiaz_zadanie(zadanie, n_siatki=N):
    """
    Parametr n_siatki zastepuje globalna stala N, dzieki czemu kazde
    zadanie mozna wywolac z inna gestoscia siatki bez efektow ubocznych.
    """
    a, b = zadanie["a"], zadanie["b"]
    nr = zadanie.get("nr", 1)
    _naglowek(f"ZADANIE {nr}:  u''(x) = -f(x),  x ∈ [{a:g}, {b:g}]")
    print(f"  f(x) = {zadanie['etykieta_f']}     |     u({a:g}) = u({b:g}) = 0")

    ana = rozwiaz_analitycznie(zadanie["f_sym"], a, b)

    _podsekcja("A", "rozwiazanie analityczne (podwojna calka)")
    _wiersz("F(x) = -∬ f(x) dx²")
    _wiersz(f"F(x) = {_wzor(ana['F'])}")
    _wiersz(f"C1   = {_liczba(ana['C1'])}")
    _wiersz(f"C2   = {_liczba(ana['C2'])}")
    _wiersz(f"u(x) = {_wzor_u(ana['u'], ana['C1'], ana['C2'])}")
    u_mid = float(ana["u"].subs(x_sym, (a + b) / 2))
    _wiersz(f"przyklad:  u({(a+b)/2:g}) = {u_mid:.6f}")
    _koniec_podsekcji()

    if "F_dane" in zadanie:
        u_z_F, c1, c2 = rozwiaz_z_danego_F(zadanie["F_dane"], a, b)
        _podsekcja("B", "weryfikacja z podanym F(x)")
        _wiersz(f"F(x) = {_wzor(zadanie['F_dane'])}")
        _wiersz(f"C1   = {_liczba(c1)}    C2 = {_liczba(c2)}")
        _wiersz(f"u(x) = {_wzor_u(u_z_F, c1, c2)}")
        zgodne = sp.simplify(u_z_F - ana["u"]) == 0
        _wiersz(f"zgoda z czescia A: {'TAK' if zgodne else 'NIE'}")
        _koniec_podsekcji()

    wezly, h, A_mat, b_vec, u_num = rozwiaz_dyskretnie(zadanie["f"], a, b, n_siatki)
    u_ref = u_z_wzoru(ana, wezly)
    blad_lok = np.abs(u_num - u_ref)
    blad = np.max(blad_lok)

    _podsekcja("C", "rozwiazanie dyskretne (roznice skonczone)")
    _wiersz(f"siatka: N = {n_siatki} podzialow,  h = {h:.5f},  wezlow: {len(wezly)}")
    _wiersz("wzor:  (u[i-1] - 2*u[i] + u[i+1]) / h^2 = -f(x[i])")
    _wiersz("       => A*u = b,  A[i,i]=-2,  A[i,i+-1]=+1")
    _pokaz_macierz(A_mat)
    _pokaz_wektor(b_vec)
    _wiersz(f"max |u_num - u_ana| = {blad:.2e}")

    krok = 2 if len(wezly) > 12 else 1
    wiersze_siatki = []
    for i in range(0, len(wezly), krok):
        wiersze_siatki.append([
            f"{wezly[i]:.2f}",
            f"{u_num[i]:.8f}",
            f"{u_ref[i]:.8f}",
            f"{blad_lok[i]:.2e}",
        ])
    last = len(wezly) - 1
    if last % krok != 0:
        wiersze_siatki.append([
            f"{wezly[last]:.2f}",
            f"{u_num[last]:.8f}",
            f"{u_ref[last]:.8f}",
            f"{blad_lok[last]:.2e}",
        ])
    _wiersz("")
    _tabela(["x", "u_num", "u_ana", "|blad|"], wiersze_siatki)
    _koniec_podsekcji()

    _podsekcja("D", "zbieznosc przy zageszczaniu siatki")
    wiersze_zb = []
    poprzedni = None
    for n_podzialow in [4, 8, 16, 32, 64]:
        w, hn, _, _, un = rozwiaz_dyskretnie(zadanie["f"], a, b, n_podzialow)
        e = np.max(np.abs(un - u_z_wzoru(ana, w)))
        stosunek = f"{poprzedni / e:.1f}x" if poprzedni else "—"
        wiersze_zb.append([str(n_podzialow), f"{hn:.5f}", f"{e:.2e}", stosunek])
        poprzedni = e
    _tabela(["N", "h", "max |blad|", "przysp. vs poprz."], wiersze_zb)
    _wiersz("oczekiwane przyspieszenie ~4x przy podwojeniu N  (rzad O(h^2))")
    _koniec_podsekcji()

    pliki = rysuj_wszystkie(zadanie, wezly, u_num, ana, A_mat, n_siatki)
    _podsekcja("E", "wygenerowane wykresy")
    for p in pliki:
        _wiersz(f"  {p}")
    _koniec_podsekcji()


# ---------------------------------------------------------------------------
# Punkt wejscia
# ---------------------------------------------------------------------------

def main():
    print(_linia("═"))
    print("  u''(x) = -f(x),   u(a) = u(b) = 0")
    print("  metoda: podwojna calka (analitycznie) + roznice skonczone (numerycznie)")
    print(_linia("═"))
    for z in ZADANIA:
        rozwiaz_zadanie(z, n_siatki=N)
    print(f"\n{_linia('═')}")
    print("  koniec")
    print(_linia("═"))


if __name__ == "__main__":
    main()
