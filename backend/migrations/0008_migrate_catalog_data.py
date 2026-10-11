from django.db import migrations
from django.utils.text import slugify

# (title, category, language, price, thumbnail, description)
SEED_MOVIES = [
    ("The Super Mario Bros.", "Movies", "English", 250, "Thumb/f769d69be489f65e8cb1748693fce35e.jpg",
     "Brooklyn plumbers Mario and Luigi are swept into a magical world, where Mario teams up with Princess Peach to stop Bowser."),
    ("Avatar: The Way of Water", "Movies", "English", 300, "Thumb/1ec694a9d587d509ec7a9be815aacfac.jpg",
     "Jake Sully and Neytiri's family seek refuge with the ocean clans of Pandora when an old threat returns."),
    ("Transformers: Rise of the Beasts", "Movies", "English", 420, "Thumb/3534b9bf9505c28893f0204d0f77a00a.jpg",
     "The Autobots join forces with the Maximals to stop Scourge and the Terrorcons from unleashing Unicron on Earth."),
    ("Extraction 2", "Movies", "English", 400, "Thumb/9cd56c00c2b79598f7fba8ba33b2128d.jpg",
     "Back from the brink of death, mercenary Tyler Rake takes on a deadly mission to rescue a family from a Georgian prison."),
    ("John Wick: Chapter 4", "Movies", "English", 250, "Thumb/1e9efbf118acd1e7661d144868dc5ef5.jpg",
     "John Wick uncovers a path to defeating the High Table, but must face a powerful new enemy with alliances across the globe."),
    ("The Flash", "Movies", "English", 300, "Thumb/f7975e92348f8055ee359ea5218d1aa5.jpg",
     "Barry Allen travels back in time to save his family, and accidentally creates a world without superheroes."),
    ("Guardians of the Galaxy Volume 3", "Movies", "English", 200, "Thumb/91670229ac9f3b6fb4d242d6b5511644.jpg",
     "Peter Quill rallies his team on a dangerous mission to protect one of their own: Rocket."),
    ("Knights of the Zodiac", "Movies", "English", 300, "Thumb/552080e2fea0c47fb4accfc959d5836a.jpg",
     "A headstrong street orphan discovers he is destined to protect the reincarnation of the goddess Athena."),
    ("Fast X", "Movies", "English", 400, "Thumb/a99ba7cd6b251e75c6723da994bc02b4.jpg",
     "Dom Toretto and his family are hunted by Dante Reyes, a vengeful enemy from their past."),
    ("Spider-Man: Across the Spider-Verse", "Movies", "English", 250, "Thumb/677f8af5b3641ba09964277253a36761.jpg",
     "Miles Morales is catapulted across the Multiverse, where he clashes with the Spider-Society over how to face a new threat."),
    ("The Witcher", "TV Series", "English", 200, "Thumb/32824d7b554c66c28f64e53cc70459d7.jpg",
     "Geralt of Rivia, a mutated monster hunter, struggles to find his place in a world where people often prove more wicked than beasts."),
    ("Tom Clancy's Jack Ryan", "TV Series", "English", 250, "Thumb/851fef7b680d66fcf6999efd06d2b971.jpg",
     "CIA analyst Jack Ryan is thrust into dangerous field assignments after uncovering a pattern in terrorist communications."),
    ("Lust Stories 2", "TV Series", "Hindi", 200, "Thumb/70031a1866177c9504ee6fb913e6779c.jpg",
     "A four-part anthology exploring love, desire and relationships through the eyes of different generations."),
    ("Silo", "TV Series", "English", 400, "Thumb/d647891fbe0106f96a358ee8b463d622.jpg",
     "Thousands live in a giant underground silo, where an engineer starts asking questions about a mysterious death."),
    ("Hijack", "TV Series", "English", 300, "Thumb/bbb3557a25a80ce3023d454218495652.jpg",
     "When a flight from Dubai to London is hijacked, a seasoned negotiator uses every skill he has to save the passengers."),
    ("Secret Invasion", "TV Series", "English", 555, "Thumb/84218c778e006f43777e1f8fe18a2560.jpg",
     "Nick Fury and Talos uncover a conspiracy by shapeshifting Skrulls to take control of Earth."),
    ("Warrior", "TV Series", "English", 200, "Thumb/30d238381da810605dd0e2d428cc2ea6.jpg",
     "A martial arts prodigy arrives in 1870s San Francisco and is caught up in the brutal Tong Wars of Chinatown."),
    ("Celebrity", "TV Series", "English", 150, "Thumb/0633c2205ea8842b6a8c1b42bf96115c.jpg",
     "A young woman becomes an overnight social media star and enters the glamorous, cutthroat world of influencers."),
]
SEED_CATEGORIES = ["Movies", "TV Series"]
SEED_LANGUAGES = ["English", "Hindi", "Tamil", "Malayalam"]
DESCRIPTIONS = {title: desc for title, *_, desc in SEED_MOVIES}


def forwards(apps, schema_editor):
    Category = apps.get_model("backend", "Category")
    Language = apps.get_model("backend", "Language")
    Movie = apps.get_model("backend", "Movie")
    categorydb = apps.get_model("backend", "categorydb")
    languagedb = apps.get_model("backend", "languagedb")
    productdb = apps.get_model("backend", "productdb")

    def category(name):
        name = (name or "Uncategorised").strip()
        return Category.objects.get_or_create(name=name, defaults={"slug": slugify(name)})[0]

    def language(name):
        return Language.objects.get_or_create(name=(name or "Unknown").strip())[0]

    legacy_products = list(productdb.objects.order_by("id"))
    if legacy_products:
        for c in categorydb.objects.exclude(CategoryName__isnull=True).exclude(CategoryName=""):
            category(c.CategoryName)
        for lang in languagedb.objects.exclude(Language__isnull=True).exclude(Language=""):
            language(lang.Language)
        for p in legacy_products:
            thumb = p.Thumbnail.name or ""
            if thumb and "/" not in thumb:
                thumb = f"Thumb/{thumb}"
            Movie.objects.create(
                title=p.MovieName or "Untitled",
                category=category(p.CategoryName),
                language=language(p.Language),
                price=max(p.Price or 0, 0),
                description=DESCRIPTIONS.get(p.MovieName, ""),
                thumbnail=thumb,
            )
        return

    for name in SEED_CATEGORIES:
        category(name)
    for name in SEED_LANGUAGES:
        language(name)
    for title, cat, lang, price, thumb, desc in SEED_MOVIES:
        Movie.objects.create(
            title=title, category=category(cat), language=language(lang),
            price=price, description=desc, thumbnail=thumb,
        )


class Migration(migrations.Migration):
    dependencies = [("backend", "0007_catalog_models")]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
