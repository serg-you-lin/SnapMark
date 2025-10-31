"""
Esempio: uso delle funzioni rapide di SnapMark
"""

import snapmark as sm

if __name__ == "__main__":
    folder = "Examples/Input"

    print("👉 Esegui marcatura rapida (quick_mark)")
    sm.mark_by_name(folder, scale_factor=100)

    # print("\n👉 Conta rapidamente i fori (quick_count_holes)")
    stats = sm.quick_count_holes(folder, min_diam=4.9, max_diam=10.1, verbose=False)

    print("\n📊 Totale fori trovati:", stats.get("total_count", "?"))
