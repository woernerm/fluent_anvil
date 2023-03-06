# Fluent Anvil
[Fluent](https://projectfluent.org/) is a localization system for natural-sounding translations. There are official implementations for [JavaScript](https://github.com/projectfluent/fluent.js), [Python](https://github.com/projectfluent/python-fluent) and [Rust](https://github.com/projectfluent/fluent-rs). This library provides an interface for [Anvil](https://anvil.works/). The repository contains both the JavaScript interface as well as the corresponding Anvil app. 

In the Anvil editor you can add this library as a third party dependency using the token UHLC7WE6TELL25TO . Therefore, you do not need to download this library unless you want to contribute (you are welcome to do so), want to know how it works or experience issues adding it as a dependency. Please note that this is a personal project with the hope that it may be of use to others as well. I am neither affiliated with [Project Fluent](https://projectfluent.org/) nor [Anvil](https://anvil.works/).

## Why use Fluent?
In contrast to gettext you can create more nuanced and natural sounding translations. For example, Polish has more plural forms than English or German. Therefore, selecting the right translation requires knowing whether there are one, few or many of something. With localization systems like gettext, this requires adding additional logic inside your application for every special case you might encounter for all languages you want to support. With fluent, this language-specific logic is encapsulated in the translation file and does not impact other translations.

Personally, I also find fluent easier to learn and use than gettext. In simple cases, a translation for a given locale is just a text file with string definitions like:

en_US/main.ftl:
```
close-button = Close
```
de_DE/main.ftl:
```
close-button = Schließen
```
If you have simple translations, the file stays simple. If a translation happens to be more complicated for a language, you only need to add the logic in the translation file for that particular language. You can find out more at [Project Fluent](https://projectfluent.org/).

## Quick Guide
In Anvil's assets section, add a directory to place your translations in, ideally you have one subfolder for each locale, e.g.
- localization
     - es_MX
         - main.ftl
     - en_US
         - main.ftl
     - de_DE
         - main.ftl

With Fluent, you can use variables for placeholders or selecting the appropriate translation. In the following example we are going to greet the user. Therefore, we use a variable as a placeholder for the user's name. Assume that the content of es_MX/main.ftl is: 
`hello = Hola { $name }.`

Then, import two classes in your form (Message is optional but required for the examples):
```py
from fluent_anvil.lib import Fluent, Message
```
If you want to know which locale the user prefers, just call
```py
Fluent.get_preferred_locales()
```
This will return a list of locales such as `['de-DE']` that the user prefers (this method does not use Fluent but the [get-user-locale](https://www.npmjs.com/package/get-user-locale) package).

Now, you can initialize Fluent using the following (we ignore the preferred locale for now):
```py
fl = Fluent("localization/{locale}/main.ftl", "es-MX", ["en-US", "es-MX"])
```
This will initialize fluent with the Mexican Spanish locale. The first parameter is a template string indicating where the translation files are stored. The placeholder {locale} is replaced with the desired locale (hyphens converted to underscore, because Anvil does not allow hyphens in directory names). The second parameter is the desired locale. The last parameter is a list of fallback locales that will be iterated through if translation fails. Generally, all methods of the Python object accept locales regardless of whether you use hyphens or underscores. Note that you do not have to provide the full URL starting with `./_/theme/`. It will be prepended automatically. If your translation files are stored somewhere else entirely you can explicitly set the prefix by adding it to the end of the parameter list.

Now, you can greet the user:
```py
print(fluent.format("hello", name="John"))
```
Every variable you want to have access to in your .ftl files can be added as a keyword variable. Apart from facts like the user's name this can be used to determine a natural sounding translation. These variables may include the count of something or the time of day. Depending on the type of variable, Fluent will automatically format the value according to the selected locale. For example, these messages:
en_US/main.ftl:
`time-elapsed = Time elapsed: { $duration }s.`
and
de_DE/main.ftl:
`time-elapsed = Vergangene Zeit: { $duration }s.`
After calling a command like
```py
print(fluent.format("time-elapsed", duration=12342423.234 ))
```
the message will show up with locale `en-US` as:
`Time elapsed: ⁨12,342,423.234⁩s.`
While with locale "de_DE" it will show up as:
`Vergangene Zeit: ⁨12.342.423,234⁩s.`
Pay attention to the use of dot and comma which is specific to the respective countries.

You can translate multiple strings at once (that's more efficient than one by one) by wrapping them in Message objects:
```py
print(fl.format(
    Message("hello", name="World"), 
    Message("welcome-back", name="John"),
    ...
))
```
This returns a list of all translations in the same order as the corresponding Message instances. That's nice already. However, my favorite feature is the possibility to write directly to GUI component attributes:
```py
fl.format(
    Message("hello", name="world"), 
    Message(self.label, "text", "hello", name="John"),
)
```
You just provide the component and the name of the attribute you want to write to (similar to Python's `setattr()` function).

You can switch to a different locale on the fly using `set_locale()`. Again, the first parameter is the desired locale and the second is a list of fallback locales.
```py
fluent.set_locale("en-US", ["en-GB", "en-AU"])
```

### Bonus Round: Translate your HTML Templates
You can translate your static content as well. Just add the tags `data-l10n-id` for the message id and `data-l10n-args` for context variables (if needed) like this:
```html
<h1 id='welcome' data-l10n-id='hello' data-l10n-args='{"name": "world"}'>Localize me!</h1>
```
If you do not initialize a Fluent instance, you will see "Localize me!". As soon as the Fluent instance is initialized (e.g. with locale es-MX), the text changes to "Hola ⁨world⁩". If Fluent would fail for some reason, the default text (in this case "Localize me!") would be shown.
