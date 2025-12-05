# wat betekent de underscore `_` in Django?
In Django betekent de underscore `_` in jouw voorbeeld:

```python
email = models.EmailField(_('email address'), unique=True)
```

**Het is een alias voor de vertaalfunctie `gettext_lazy()`**.

### Wat doet `_()` precies?

* Het markeert de tekst **'email address'** als **vertaalbaar**.
* Django’s i18n-systeem (internationalization) kan deze tekst dan vertalen op basis van de ingestelde taal in de applicatie.
* Meestal wordt `_` zo gedefinieerd:

```python
from django.utils.translation import gettext_lazy as _
```

### Dus:

`_('email address')` betekent eigenlijk:

> “Vertaal deze tekst wanneer nodig.”

### Waarom een underscore?

* `_` wordt in Django en veel andere frameworks gebruikt als *korte alias* omdat je het vaak gebruikt.
* Het is een conventie, geen speciale Python-syntax.

### Samengevat

**`_()` = shorthand voor lazy vertalen (gettext)**
Het maakt jouw label of tekst vertaalbaar in verschillende talen.

