"""Etterprøving av NRKs vann- og dusjregnestykke.

NRK: 1 kWh krever 1429 l vann (vektet snitt energiekvivalent NO1+NO2).
     Dusj 38 °C, 6 l/min -> 1,4 kWh -> 2000 l kraftverksvann.
"""
CP = 4.186          # kJ/(kg·K)
KJ_PER_KWH = 3600.0
EN_EKV_NRK = 1 / 1.429   # kWh per m3 implisitt i NRKs tall

def kwh_for_shower(minutes, l_per_min=6, t_out=38, t_in=8, eta=1.0):
    liters = minutes * l_per_min
    return liters * CP * (t_out - t_in) / KJ_PER_KWH / eta, liters

print(f"Implisitt energiekvivalent i NRKs tall: {EN_EKV_NRK:.3f} kWh/m3")
print(f"1,4 kWh * 1429 l/kWh = {1.4*1429:.0f} l  (NRK sier 2000)")
print()
print("Hvor lang dusj gir 1,4 kWh ved 6 l/min og 38 °C?")
for t_in in (5, 8, 10, 12):
    per_min, _ = kwh_for_shower(1, t_in=t_in)
    print(f"  inntak {t_in:>2} °C: {per_min:.4f} kWh/min -> 1,4 kWh = {1.4/per_min:.1f} min "
          f"({1.4/per_min*6:.0f} l varmtvann)")
print()
print("Med virkningsgrad 0,9 (varmtvannsbereder + tap):")
for t_in in (8, 10):
    per_min, _ = kwh_for_shower(1, t_in=t_in, eta=0.9)
    print(f"  inntak {t_in} °C: 1,4 kWh = {1.4/per_min:.1f} min")
print()
# Forhold kraftverksvann / dusjvann
for mins in (6, 7, 8, 10):
    kwh, liters = kwh_for_shower(mins, t_in=8)
    print(f"  {mins:>2} min dusj: {liters:.0f} l dusjvann, {kwh:.2f} kWh, "
          f"{kwh*1429:.0f} l kraftverksvann -> forhold {kwh*1429/liters:.1f}x")
