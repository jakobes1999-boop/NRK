"""Kjør hele pipelinen. Bruk: py run_all.py [--skip-download] [--skip-frost]

--skip-download  hopp over steg 1–5 (bruk data som allerede ligger i data/)
--skip-frost     hopp over gradtall (krever FROST_CLIENT_ID i .env); modellen bruker da måneds-FE som værproxy
Steg 4 (Frost, ~15 min) og steg 3 (spot, ~20 min) kan kjøres separat og gjenopptas.
"""
import subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).parent
args = set(sys.argv[1:])

def run(script, *extra):
    print(f"\n########## {script} {' '.join(extra)} ##########", flush=True)
    subprocess.run([sys.executable, script, *extra], cwd=ROOT / "src", check=True)

if "--skip-download" not in args:
    run("s01_download_elhub.py")
    run("s02_download_ssb.py")
    run("s03_download_prices.py")
    if "--skip-frost" not in args:
        run("s04_download_frost.py")
    run("s05_nve_energiekvivalent.py")
run("s06_build_panel.py")
run("s06_build_panel.py", "--fylke")
run("s07_estimate_fe.py")
run("s08_did_orderstatus.py")
run("s10_forbedret_modell.py")
run("s11_nrk_pastander.py")
run("s12_kritikk2_beregninger.py")
run("s13_dose_sent.py")
run("s13b_dose_robusthet.py")
run("s14_wild_bootstrap.py")
run("s15_effektiv_pris.py")
run("s17_nettoeksport.py")
run("s18_nrk_spesifikasjonssok.py")
run("s20_timetest_prisfordel.py")
run("s21_magasin_eksport.py")
# s16_verifiser_prisomrade.py krever nettoppslag (VG) og kjøres separat
run("vann_dusj.py")
run("s09_til_godkjenning.py")
print("\nFerdig. Tall til godkjenning i output/TIL_GODKJENNING.md. Notatet fylles først etter godkjenning.")
