import anvil.js


class Message:
    """Container for a translation request.

    The Message class is used to define a translation request. You can define a
    message id and optional keyworded variables that are passed to fluent (e.g. for
    placeables). Alternatively, you may use it in a way similar to Python's setattr()
    function: In addition to the afore mentioned parameters you can define an object
    and the name of the attribute to write to. The translated string will then be
    assigned to that attribute automatically.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the Message class.

        Examples:
            Variant 1:
                ``Message(my_label, "text", "my_message_identifier", name="John")``
                This example assumes that you have a form containing the label my_label
                for greeting the user. The greeting message is defined
                in the .ftl file using identifier my_message_identifier, e.g.:
                ``my_message_identifier = Welcome, { $name }!`` or
                ``my_message_identifier = Willkommen, { $name }!`
                In the example above, the name is given as keyworded argument.
            Varian 2:
                ``Message("my_message_identifier", name="John")``
                Same as above without assigning the translation.

        Args:
            args: You may provide object (any), attribute name (str) and message id
                (str). Alternatively, you can provide the message id (str) only.
            kwargs: Optional keyworded variables to pass on to fluent (e.g. for
                placeables or selectors).
        """
        try:
            # Assume the user wants to assign the translation to an object attribute.
            self.obj, self.attribute, self.msg_id = args
            self.variables = kwargs
        except ValueError:
            # Assume the user wants to obtain the translated string only.
            self.obj = None
            self.attribute = None
            self.msg_id = args[0]
            self.variables = kwargs


class Fluent:
    """Anvil interface for fluent and some convenience functions.

    The class interfaces with a JavaScript library that initializes fluent, feeds fluent
    the .ftl files matching the selected locale and provides some convenience functions
    like obtaining the user's preferred locale.

    The function most you will use most often is Fluent.format().

    Example:
        ``
        fluent = Fluent("localization/{locale}/main.ftl", "es_MX", ["es_ES", "en_US"])
        print(fluent.format("hello", name="John"))
        ``
        This will initialize fluent with Mexican Spanish locale and return the
        translation stored with message id "hello". The name is given so that fluent
        may use it as a placeable. The last parameter is a list of fallback locales
        that will be iterated through if the given message id is not available
        for the "es_MX" locale.
    """

    class __JSInterface:
        """The JavaScript library that is used to interface with fluent creates a
        "DOMLocalization" and a "Localization" object. You can access it directly
        using the public Fluent.js attribute.

        Example:
            ``
            fl = Fluent("localization/{locale}/main.ftl", "es_MX", ["es_ES", "en_US"])
            print(fl.js.formatValue("hello", { name: "John"}))
            ``
            This will call the original fluent-dom API.
        """

        ASSET_URL = "./_/theme/"
        FLUENT_LIB = "fluent_anvil.js"

        def __init__(
            self,
            path_template: str,
            locale: str,
            fallback_locales: list = None,
            path_prefix: str = None,
        ):
            """Initialize Fluent's DOMLocalization and Localization object."""
            
            # Determine the path prefix and ensure it ends with a forward slash.
            prefix = path_prefix or self.ASSET_URL
            prefix = "" if path_template.startswith(prefix) else prefix
            prefix = prefix if prefix.endswith("/") else f"{prefix}/"

            self.module = anvil.js.import_from(f"{self.ASSET_URL}{self.FLUENT_LIB}")
            fluent = self.module.init_localization(
                f"{prefix}{path_template}", locale, fallback_locales
            )
            
            if fluent.dom_errors:
                raise Exception(fluent.dom_errors[0])

            if fluent.main_errors:
                raise Exception(fluent.main_errors[0])

            if not fluent.dom or not fluent.main:
                raise RuntimeError("Error initializing Localizer.")

            self.dom_localization = fluent.dom
            self.localization = fluent.main

    @classmethod
    def _clean_locale(cls, locale: str):
        """Ensure valid IETF language tags.

        Since Anvil does not support hyphens for directories, users may use an 
        underscore for the locale names as well. However, this would not be valid IETF 
        language tags. Therefore, replace any underscores with hyphens. The JavaScript 
        library will switch to underscore again when loading the assets.
        """
        return locale.replace("_", "-")

    def __init__(
        self,
        path_template: str,
        locale: str,
        fallback_locales: list = None,
        path_prefix: str = None,
    ):
        """Initialize Fluent.

        Args:
            path_template: Template string to the .ftl files, e.g.
                "localization/{locale}/main.ftl". You can only use the {locale}
                placeholder. It will contain the locale with underscore, e.g. "de_DE"
                instead of "de-DE", because Anvil does not support hyphens for
                directory names.
            locale: The name of the locale to use. Can be written with both hyphen or
                underscore, e.g. both "en_US" and "en-US" will work.
            fallback_locales: List of locale names to use if the primary locale is
                not available.
            path_prefix: Prefix for the given path. Will be "./_/theme/" if not given.
                The prefix will be prepended to path_template if not already present.
                This is meant as a convenience for novice users and reduce typing
                effort.
        """
        self.js = None
        self._path_template = path_template
        self._path_prefix = path_prefix
        self.set_locale(locale, fallback_locales)

    def set_locale(self, locale: str, fallback_locales: list = None):
        """Sets a new locale to translate to.

        Args:
            locale: The name of the locale to use. Can be written with both hyphen or
                underscore, e.g. both "en_US" and "en-US" will work.
            fallback_locales: List of locale names to use if the primary locale is
                not available.        
        """
        
        locale = self._clean_locale(locale)
        fallback_locales = fallback_locales or []
        fallback_locales = [self._clean_locale(e) for e in fallback_locales]

        self.js = self.__JSInterface(
            self._path_template, 
            locale, 
            fallback_locales, 
            self._path_prefix
        )  

    @classmethod
    def get_preferred_locales(cls, fallback: str = None) -> list:
        """Return the user's preferred locales.
        
        Uses the Get-User-Locale library https://github.com/wojtekmaj/get-user-locale .

        Args:
            fallback: The fallback locale to return if operation fails.

        Returns:
            A list of preferred locales (most preferrable first).
        """
        module_js = anvil.js.import_from(
            f"{cls.__JSInterface.ASSET_URL}{cls.__JSInterface.FLUENT_LIB}"
        )
        fallback = cls._clean_locale(fallback) if fallback else None
        locales = module_js.get_user_locales(fallback)
        return locales if isinstance(locales, list) else [locales]

    def format(self, message, *args, **kwargs):
        """Return a translation for the given message id and variables.

        You can either provide a single message id (with optional keyworded variables
        to pass on to Fluent) or an arbitrary number of Message instances.

        Examples:
            You get the translation for a single message id like this:
            ``
            fl = Fluent("localization/{locale}/main.ftl", "es_MX", ["en_US"])
            print(fl.format("hello", name="John"))
            ``

            Alternatively, you can provide an arbitrary number of Message instances:
            ``
            fl = Fluent("localization/{locale}/main.ftl", "es_MX", ["en_US"])
            print(fl.format(
                Message("hello", name="world"), 
                Message(self.label, "text", "hello", name="John"),
                Message("welcome", name="john")
            ))
            ``

        Args:
            message: message id (as string) or Message instance to return a
                translation for.
            args: An arbitrary number of additional Message instances (not message ids).
            kwargs: Keyworded variables to pass on to Fluent (only in case
                parameter message is a string).

        Returns: A translation string in case a string message id is given. If Message 
            instances are given, a list of translations in the same order.
        """

        # If a string is given, translate a single value.
        if isinstance(message, str):
            if args:
                raise ValueError(
                    "Parameter args is not supported if message is a string."
                )
            return self.js.localization.formatValue(message, kwargs)

        if kwargs:
            raise ValueError(
                "Parameter kwargs is only supported if message is a string"
            )

        # If multiple Message instances are given, translate all of them.
        messages = (message,) + args
        keys = [{"id": e.msg_id, "args": e.variables} for e in messages]
        translations = self.js.localization.formatValues(keys)

        # If Message instances reference an object attribute, set the translations.
        for i, msg in enumerate(messages):
            if msg.obj:
                setattr(msg.obj, msg.attribute, translations[i])

        # Return all translations.
        return translations
