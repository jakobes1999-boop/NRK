"""Wild cluster bootstrap (WCB) for vektede minste kvadraters DiD-modeller med få klustre.

Bakgrunn
--------
Klusterrobuste standardfeil (CR1) er nedadskjeve når antallet klustre G er lite. I dette
prosjektet er G = 27 (område × status × EAC) i hovedmodellene og G = 9 i per-EAC-modellene.
Wild cluster bootstrap med restriksjon under nullhypotesen (WCR) korrigerer dette:

  Cameron, A. C., J. B. Gelbach og D. L. Miller (2008): «Bootstrap-Based Improvements for
    Inference with Clustered Errors», Review of Economics and Statistics 90(3), 414–427.
  MacKinnon, J. G. og M. D. Webb (2018): «The wild bootstrap for few (treated) clusters»,
    The Econometrics Journal 21(2), 114–135.

MacKinnon og Webb anbefaler Webbs sekspunktsfordeling framfor Rademacher når G er lite:
Rademacher gir bare 2^G distinkte vektvektorer, slik at p-verdien er grovt diskretisert
(2^9 = 512 for ni klustre). Denne modulen bruker Webb automatisk når G < 12 dersom
`weights="auto"`, og lar begge kjøres eksplisitt.

Metode (WCR, restringert wild cluster bootstrap)
-----------------------------------------------
1. WLS håndteres ved å transformere: y~ = sqrt(w) · y, X~ = sqrt(w) · X. Alt under skjer i
   transformert rom, som er algebraisk ekvivalent med WLS.
2. Restringert estimering under H0: beta_k = b0 – dvs. minste kvadrater av (y~ − b0 · x~_k)
   på X~ uten kolonne k. Restringerte residualer u_r.
3. For hver bootstrapreplikasjon b trekkes én vekt v_g per kluster (Rademacher: ±1 med
   sannsynlighet 1/2; Webb: ±sqrt(1,5), ±1, ±sqrt(0,5) med sannsynlighet 1/6 hver) og
   y*_i = (X~ b_r + b0 · x~_k)_i + v_{g(i)} · u_{r,i}.
4. Full modell reestimeres på y*, og t*_b = (beta*_k − b0) / se_CR1(beta*_k) beregnes med
   klusterrobust CR1-varians med korreksjonen G/(G−1) · (N−1)/(N−K) (samme korreksjon som
   statsmodels bruker for cov_type="cluster").
5. p = (1 + antall replikasjoner med |t*_b| >= |t|) / (B + 1) (symmetrisk tosidig test), der t er den
   observerte teststørrelsen for samme nullverdi b0.

Konfidensintervall
------------------
`wild_cluster_ci` inverterer testen: p(b0) beregnes på et rutenett av nullverdier rundt
estimatet (standard 41 punkter over estimat ± 4 se), og intervallgrensene finnes ved lineær
interpolasjon der p(b0) krysser 0,05. Hver rutenettpunkt får sin egen restringerte
estimering, men samme bootstrapvekter (felles seed), slik at p(b0) er monotont glatt.

Alle funksjoner er vektorisert over bootstrapreplikasjonene. Kun rad k av pseudoinversen og
en N-vektor h = X~ (X~'X~)^+ e_k trengs for t-verdiene, slik at ingen K × K × B-array bygges.
"""
from __future__ import annotations

import numpy as np
import scipy.linalg as sla

__all__ = ["drop_collinear", "cluster_se", "prepare", "wild_cluster_boot", "wild_cluster_ci",
           "design_from_formula"]

WEBB_POINTS = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)])


# --------------------------------------------------------------------------------------
# Designmatrise
# --------------------------------------------------------------------------------------
def design_from_formula(formula, data, weights_col="n_mp"):
    """Bygg (y, X, navn, w) med nøyaktig samme patsy-spesifikasjon som statsmodels.wls.

    Returnerer y (N,), X (N, K), kolonnenavn (liste) og vektene w (N,).
    """
    import statsmodels.formula.api as smf

    mod = smf.wls(formula, data=data, weights=data[weights_col])
    return (np.asarray(mod.endog, float), np.asarray(mod.exog, float),
            list(mod.exog_names), np.asarray(data[weights_col], float))


def drop_collinear(X, names, keep, tol=1e-8):
    """Fjern lineært avhengige kolonner med pivotert QR, men behold alltid `keep`.

    `keep` er en liste kolonnenavn (parameterne som testes). Framgangsmåten:
    pivotert QR kjøres på de øvrige kolonnene for å velge en maksimal uavhengig delmengde;
    deretter legges `keep`-kolonnene til bakerst. Fordi `keep`-kolonnene residualiseres mot
    resten er koeffisientene på dem uendret av hvilken reparametrisering av fikseffektene
    som velges. Feiler dersom en `keep`-kolonne er kollineær med de valgte.

    Returnerer (X_ny, navn_ny, indekser for keep i X_ny).
    """
    names = list(names)
    keep_idx = [names.index(c) for c in keep]
    rest_idx = [i for i in range(X.shape[1]) if i not in keep_idx]
    R = X[:, rest_idx]
    # kolonneskalering gjør toleransen sammenliknbar på tvers av kolonner
    nrm = np.linalg.norm(R, axis=0)
    nrm[nrm == 0] = 1.0
    _, r, piv = sla.qr(R / nrm, mode="economic", pivoting=True)
    d = np.abs(np.diag(r))
    rank = int((d > tol * max(d.max(), 1.0)).sum())
    sel = [rest_idx[i] for i in sorted(piv[:rank])]
    new_idx = sel + keep_idx
    Xn = X[:, new_idx]
    nn = [names[i] for i in new_idx]
    # kontroller at hele matrisen har full kolonnerang
    nrm2 = np.linalg.norm(Xn, axis=0)
    nrm2[nrm2 == 0] = 1.0
    s = np.linalg.svd(Xn / nrm2, compute_uv=False)
    if s[-1] <= tol * s[0]:
        raise ValueError("Kolonnene som testes er kollineære med fikseffektene – ikke identifisert.")
    return Xn, nn, [len(sel) + j for j in range(len(keep_idx))]


# --------------------------------------------------------------------------------------
# Klusterrobust varians (CR1)
# --------------------------------------------------------------------------------------
def _cluster_index(groups):
    _, inv = np.unique(np.asarray(groups, dtype=object), return_inverse=True)
    return inv, int(inv.max()) + 1


def cluster_se(y, X, w, groups, k):
    """CR1 klusterrobust standardfeil og t-verdi for koeffisient k i WLS-modellen.

    Korreksjon: G/(G−1) · (N−1)/(N−K), som i statsmodels cov_type="cluster".
    Returnerer (beta_k, se_k, t_k, G).
    """
    sw = np.sqrt(w)
    Xt = X * sw[:, None]
    yt = y * sw
    gi, G = _cluster_index(groups)
    N, K = Xt.shape
    XtX = Xt.T @ Xt
    XtXi = np.linalg.pinv(XtX)
    beta = XtXi @ (Xt.T @ yt)
    u = yt - Xt @ beta
    h = Xt @ XtXi[:, k]
    s = np.bincount(gi, weights=h * u, minlength=G)
    c = G / (G - 1) * (N - 1) / (N - K)
    var = c * float(s @ s)
    se = np.sqrt(var)
    return float(beta[k]), float(se), float(beta[k] / se), G


# --------------------------------------------------------------------------------------
# Wild cluster bootstrap
# --------------------------------------------------------------------------------------
def _draw(rng, kind, G, B):
    if kind == "rademacher":
        return rng.integers(0, 2, size=(G, B)) * 2.0 - 1.0
    if kind == "webb":
        return WEBB_POINTS[rng.integers(0, 6, size=(G, B))]
    raise ValueError(f"ukjent vekttype: {kind}")


def prepare(y, X, w, groups, k):
    """Forhåndsberegn alt som ikke avhenger av nullverdien b0 eller bootstraptrekket.

    Brukes av `wild_cluster_ci` slik at pseudoinvers og restringert tilpasning ikke
    regnes på nytt for hvert rutenettpunkt. Den restringerte tilpasningen er lineær i b0:
    u0(b0) = (I − M_r)(y~ − b0 · x~_k), der M_r er projeksjonen på X~ uten kolonne k.
    """
    y = np.asarray(y, float); X = np.asarray(X, float); w = np.asarray(w, float)
    sw = np.sqrt(w)
    Xt = X * sw[:, None]
    yt = y * sw
    gi, G = _cluster_index(groups)
    N, K = Xt.shape
    XtXi = np.linalg.pinv(Xt.T @ Xt)
    P = XtXi @ Xt.T
    h = Xt @ XtXi[:, k]
    c = G / (G - 1) * (N - 1) / (N - K)
    D = np.zeros((G, N)); D[gi, np.arange(N)] = 1.0
    keep = [j for j in range(K) if j != k]
    Xr = Xt[:, keep]
    xk = Xt[:, k]
    fy = Xr @ np.linalg.lstsq(Xr, yt, rcond=None)[0]     # projeksjon av y~
    fk = Xr @ np.linalg.lstsq(Xr, xk, rcond=None)[0]     # projeksjon av x~_k
    return dict(Xt=Xt, yt=yt, gi=gi, G=G, N=N, K=K, P=P, h=h, c=c, D=D,
                xk=xk, fy=fy, fk=fk, k=k)


def wild_cluster_boot(y=None, X=None, w=None, groups=None, k=None, B=999, weights="auto",
                      restricted=True, seed=1, b0=0.0, return_t=False, prep=None):
    """Restringert wild cluster bootstrap (WCR) av H0: beta_k = b0.

    Parametre
    ---------
    y, X : utfall (N,) og designmatrise (N, K), full kolonnerang (se `drop_collinear`).
    w    : WLS-vekter (N,), her antall målepunkter.
    groups : klustertilhørighet (N,), her g = område | status | EAC.
    k    : kolonneindeks i X for parameteren som testes.
    B    : antall bootstrapreplikasjoner (999 i bruk her).
    weights : "rademacher", "webb" eller "auto" (Webb når G < 12, ellers Rademacher).
    restricted : True gir WCR (residualer fra modellen under H0, anbefalt av MacKinnon og
        Webb); False gir WCU (urestringerte residualer), kun for sammenlikning.
    seed : frø til numpy.random.default_rng.
    b0   : nullverdien som testes.

    Returnerer dict med koef, se, t, p_wcb, G, B, vekttype (og t-fordelingen hvis return_t).
    Referanser: Cameron, Gelbach og Miller (2008); MacKinnon og Webb (2018).
    """
    if prep is None:
        prep = prepare(y, X, w, groups, k)
    Xt, yt, gi, G, N, K = prep["Xt"], prep["yt"], prep["gi"], prep["G"], prep["N"], prep["K"]
    P, h, c, D, k = prep["P"], prep["h"], prep["c"], prep["D"], prep["k"]
    kind = ("webb" if G < 12 else "rademacher") if weights == "auto" else weights

    beta = P @ yt
    u_full = yt - Xt @ beta
    s = D @ (h * u_full)
    se = np.sqrt(c * float(s @ s))
    t_obs = (float(beta[k]) - b0) / se

    # residualer og tilpasning under H0 (lineær i b0)
    if restricted:
        u0 = (yt - prep["fy"]) - b0 * (prep["xk"] - prep["fk"])
        fit0 = yt - u0
    else:
        fit0 = Xt @ beta - (float(beta[k]) - b0) * Xt[:, k]
        u0 = u_full

    rng = np.random.default_rng(seed)
    v = _draw(rng, kind, G, B)                       # (G, B)
    Ys = fit0[:, None] + u0[:, None] * v[gi]         # (N, B)
    Bh = P @ Ys                                      # (K, B)
    Us = Ys - Xt @ Bh                                # (N, B)
    S = D @ (h[:, None] * Us)                        # (G, B) klustervise summer
    ses = np.sqrt(c * (S ** 2).sum(axis=0))
    t_star = (Bh[k] - b0) / ses

    p = float((1 + (np.abs(t_star) >= np.abs(t_obs) - 1e-12).sum()) / (len(t_star) + 1))   # (1 + #)/(B + 1), Davison & Hinkley
    out = {"koef": float(beta[k]), "se": se, "t": t_obs, "p_wcb": p,
           "G": G, "B": B, "vekttype": kind, "N": N, "K": K, "b0": b0}
    if return_t:
        out["t_star"] = t_star
    return out


def wild_cluster_ci(y=None, X=None, w=None, groups=None, k=None, B=999, weights="auto",
                    seed=1, level=0.05, n_grid=41, span=4.0, prep=None):
    """Bootstrapkonfidensintervall ved inversjon av WCR-testen.

    p(b0) beregnes på `n_grid` punkter over estimat ± `span` · se, og grensene finnes ved
    lineær interpolasjon i punktene der p(b0) krysser `level`. Samme seed brukes for alle
    rutenettpunkter, slik at p-kurven blir glatt. Returnerer (lav, hoy, rutenett, p-verdier).
    """
    if prep is None:
        prep = prepare(y, X, w, groups, k)
    base = wild_cluster_boot(B=B, weights=weights, seed=seed, b0=0.0, prep=prep)
    grid = np.linspace(base["koef"] - span * base["se"], base["koef"] + span * base["se"], n_grid)
    ps = np.array([wild_cluster_boot(B=B, weights=weights, seed=seed, b0=b, prep=prep)["p_wcb"]
                   for b in grid])
    inside = ps >= level
    if not inside.any():
        return np.nan, np.nan, grid, ps
    i0, i1 = int(np.argmax(inside)), int(len(inside) - 1 - np.argmax(inside[::-1]))

    def interp(ia, ib):
        pa, pb = ps[ia], ps[ib]
        if pb == pa:
            return grid[ib]
        return grid[ia] + (level - pa) * (grid[ib] - grid[ia]) / (pb - pa)

    lo = grid[0] if i0 == 0 else interp(i0 - 1, i0)
    hi = grid[-1] if i1 == len(grid) - 1 else interp(i1 + 1, i1)
    return float(lo), float(hi), grid, ps
