# yayayoo.app

Site vitrine du studio **yayayoo** — des apps iPhone simples, soignées et amusantes,
faites par un développeur solo (Stéphane Desmets).

**URL** : [yayayoo.app](https://yayayoo.app) · **EN** : [yayayoo.app/en](https://yayayoo.app/en/)

## Apps

| App | Catégorie | App Store |
|-----|-----------|-----------|
| **Versusly** | Jeu 2 joueurs, 1 iPhone (split-screen) | [id6780861699](https://apps.apple.com/fr/app/versusly/id6780861699) |
| **Almostly** | Comptes à rebours + mascotte Pip | [id6779545689](https://apps.apple.com/app/almostly/id6779545689) |
| **Givró** | Ventilation nocturne (canicule) | [id6789108463](https://apps.apple.com/fr/app/givr%C3%B3/id6789108463) |
| **Kill Chain** | Jeu tactique 2–4 joueurs | *(à publier)* |

## Stack

- **HTML statique pur** (aucun framework, aucune dépendance externe / CDN)
- Hébergé sur **GitHub Pages** (`CNAME` → yayayoo.app)
- i18n **FR/EN** côté client (dictionnaire `T` inline par page, `data-i18n`)
- **GA4** (`G-TZ3LVQ579M`) chargé **après consentement** (bandeau cookies RGPD/CNIL)

## Structure

```
yayayoo.app/
├── index.html              # Hub (studio + 4 cartes apps)
├── versusly|almostly|givro|kill-chain/
│   ├── index.html          # Page app (hero, captures, features, pricing, FAQ)
│   ├── privacy/ · terms/   # Pages légales (par app)
│   ├── screenshots/*.webp  # Captures (WebP 480px)
│   └── og.png              # Image de partage 1200×630
├── en/                     # Pages anglaises (générées — voir build_en.py)
├── og.png                  # Image de partage du hub
├── build_en.py             # Génère /en/ depuis les sources FR (+ hreflang)
├── gen_og.py               # Génère les images OG 1200×630 (Playwright)
├── sitemap.xml · robots.txt
└── google*.html            # Vérification Google Search Console
```

## Déploiement

Site statique → push sur `main` publie via **GitHub Pages**.

```bash
git add -A && git commit -m "description" && git push
```

### ⚠️ Pages anglaises (`/en/`)

Elles sont **générées** depuis les sources FR (le dictionnaire i18n est partagé — pas de
traduction dupliquée). **Après toute modif d'une page FR**, régénérer avant de pousser :

```bash
python3 build_en.py     # régénère /en/ + hreflang fr↔en
```

## SEO / partage

- `<title>`/meta/canonical, **Open Graph + Twitter cards** (images 1200×630 sur-mesure),
  **JSON-LD** (Organization + SoftwareApplication), sitemap, robots, `hreflang` FR/EN.
- Captures optimisées en **WebP**. Boutons « Partager » (Web Share API) sur les pages apps.
- **Google Search Console + Bing** validés.

## Notes

- `data-i18n` remplace le `textContent` d'un élément : ne pas y mettre de lien/HTML sans
  sortir le `<a>` de l'élément traduit (voir la section studio du hub pour le pattern).
- Régénérer les images OG : `python3 gen_og.py` (nécessite Playwright/Chromium).
