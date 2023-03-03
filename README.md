# Introduction
[Fluent](https://projectfluent.org/) is a localization system for natural-sounding translations. There are official implementations for [JavaScript](https://github.com/projectfluent/fluent.js), [Python](https://github.com/projectfluent/python-fluent) and [Rust](https://github.com/projectfluent/fluent-rs). This library provides an interface for [Anvil](https://anvil.works/). The repository contains both the JavaScript interface as well as the corresponding Anvil app. 

In the Anvil editor you can add this library as a third party dependency using the token UHLC7WE6TELL25TO . Therefore, you do not need to download this library unless you want to contribute (you are welcome to do so) or want to know how it works. Please note that this is a personal project with the hope that it may be of use to others as well. I am neither affiliated with [Project Fluent](https://projectfluent.org/) nor [Anvil](https://anvil.works/).

# Why use Fluent?
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
