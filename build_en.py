#!/usr/bin/env python3.11
"""Génère les pages anglaises /en/ depuis les sources FR (SEO anglophone).
Ré-exécuter après toute modif des pages FR : python3 build_en.py
Les pages EN réutilisent le dictionnaire i18n partagé (T.en) — le texte bascule
en anglais via JS (lang forcé à 'en' sur /en/), pas de traduction dupliquée.
"""
import re, pathlib

BASE = pathlib.Path(__file__).parent
# (source FR, slug, chemin-URL FR sans domaine)
PAGES = [
    ("index.html",            "",           ""),
    ("versusly/index.html",   "versusly",   "versusly/"),
    ("almostly/index.html",   "almostly",   "almostly/"),
    ("givro/index.html",      "givro",      "givro/"),
    ("kill-chain/index.html", "kill-chain", "kill-chain/"),
]
DOMAIN = "https://yayayoo.app/"
SLUGS = ["", "versusly", "almostly", "givro", "kill-chain"]

# Traductions d'en-tête (title / description / og / twitter) — appliquées AU <head> SEUL
# (ne jamais toucher le body : le dico i18n T.fr y vit et doit rester intact)
HEAD_REPL = {
 "index.html": [
   ("yayayoo — Des apps qui font sourire", "yayayoo — Apps that make you smile"),
   ("yayayoo est un studio indépendant qui crée des apps iPhone simples, soignées et amusantes. Découvrez Versusly, Almostly, Givró et Kill Chain.",
    "yayayoo is an independent studio making simple, polished, fun iPhone apps. Discover Versusly, Almostly, Givró and Kill Chain."),
   ("Studio indépendant d'apps iPhone simples, soignées et amusantes : Versusly, Almostly, Givró et Kill Chain.",
    "An independent studio making simple, polished, fun iPhone apps: Versusly, Almostly, Givró and Kill Chain."),
 ],
 "versusly/index.html": [
   ("Versusly — 2 joueurs · 1 téléphone", "Versusly — 2 players · 1 phone"),
   ("Le jeu qui met l'amitié à l'épreuve. 6 mini-jeux en split-screen sur un seul iPhone.",
    "The game that puts friendships to the test. 6 split-screen mini-games on a single iPhone."),
 ],
 "almostly/index.html": [
   ("Almostly — Tes dates, avec personnalité", "Almostly — Your dates, with personality"),
   ("Almostly compte tes jours avec style — et Pip, ta mascotte, commente chaque étape avec humour, bienveillance ou zen attitude.",
    "Almostly counts your days in style — and Pip, your mascot, comments on every milestone with humor, warmth or zen."),
 ],
 "givro/index.html": [
   ("Givró — Rafraîchis ta nuit, naturellement.", "Givró — Cool your night, naturally."),
   ("Givró te dit quand ouvrir tes fenêtres la nuit pour rafraîchir ton logement naturellement pendant les canicules.",
    "Givró tells you when to open your windows at night to cool your home naturally during heat waves."),
 ],
 "kill-chain/index.html": [
   ("Kill Chain — Hackers. Tactiques. Un seul téléphone.", "Kill Chain — Hackers. Tactics. One phone."),
   ("Jeu de tactique hacker en tour par tour. 2-4 joueurs sur un seul iPhone. Programmez vos attaques en secret, exécutez simultanément.",
    "Turn-based hacker tactics game. 2-4 players on a single iPhone. Program your attacks in secret, execute simultaneously."),
 ],
}

def hreflang(frpath):
    fr = DOMAIN + frpath
    en = DOMAIN + "en/" + frpath
    return (f'  <link rel="alternate" hreflang="fr" href="{fr}" />\n'
            f'  <link rel="alternate" hreflang="en" href="{en}" />\n'
            f'  <link rel="alternate" hreflang="x-default" href="{fr}" />\n')

def add_hreflang_after_canonical(t, frpath):
    if 'hreflang=' in t:
        return t
    canon = f'<link rel="canonical" href="{DOMAIN}{frpath}" />'
    assert t.count(canon) == 1, f"canonical FR introuvable ({frpath})"
    return t.replace(canon, canon + "\n" + hreflang(frpath).rstrip("\n"), 1)

def rewrite_internal_links(t):
    # /  ->  /en/   et  /slug -> /en/slug  (liens nus uniquement, pas /slug/privacy)
    t = t.replace('href="/"', 'href="/en/"')
    for s in SLUGS:
        if s:
            t = t.replace(f'href="/{s}"', f'href="/en/{s}"')
    return t

def build_en(src, slug, frpath):
    t = (BASE / src).read_text()
    # 0) purger d'éventuels hreflang hérités de la source FR (idempotence)
    t = re.sub(r'\n\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*" />', '', t)
    # 1) enlever les JSON-LD (texte FR — éviter le mismatch schema/visible sur EN)
    t = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', '', t, flags=re.S)
    # 2) lang du document
    t = t.replace('<html lang="fr">', '<html lang="en">', 1)
    # 3) forcer l'anglais à l'init (crawlers = pas de localStorage)
    t = t.replace("localStorage.getItem('yayayoo_lang') || 'fr'", "'en'")
    t = t.replace("localStorage.getItem('lang') || 'fr'", "'en'")
    # 4) canonical + og:url -> /en/
    t = t.replace(f'<link rel="canonical" href="{DOMAIN}{frpath}" />',
                  f'<link rel="canonical" href="{DOMAIN}en/{frpath}" />', 1)
    t = t.replace(f'<meta property="og:url" content="{DOMAIN}{frpath}" />',
                  f'<meta property="og:url" content="{DOMAIN}en/{frpath}" />', 1)
    t = t.replace('content="fr_FR"', 'content="en_US"', 1)
    # 5) hreflang (après le canonical EN)
    canon_en = f'<link rel="canonical" href="{DOMAIN}en/{frpath}" />'
    assert t.count(canon_en) == 1, f"canonical EN introuvable ({slug})"
    t = t.replace(canon_en, canon_en + "\n" + hreflang(frpath).rstrip("\n"), 1)
    # 6) liens internes -> /en/
    t = rewrite_internal_links(t)
    # 7) images relatives -> absolues (Givró/Almostly)
    if slug:
        t = t.replace('src="screenshots/', f'src="/{slug}/screenshots/')
    # 8) traduire l'en-tête (title/description/og/twitter) — HEAD SEUL
    head, rest = t.split('</head>', 1)
    for fr, en in HEAD_REPL[src]:
        head = head.replace(fr, en)
    t = head + '</head>' + rest
    # écrire
    dst = BASE / "en" / (frpath + "index.html" if frpath else "index.html")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(t)
    return dst

def main():
    # pages EN
    for src, slug, frpath in PAGES:
        d = build_en(src, slug, frpath)
        print("  EN ->", d.relative_to(BASE))
    # hreflang sur les pages FR
    for src, slug, frpath in PAGES:
        p = BASE / src
        t = add_hreflang_after_canonical(p.read_text(), frpath)
        p.write_text(t)
    print("  hreflang ajouté sur les 5 pages FR")

if __name__ == "__main__":
    main()
