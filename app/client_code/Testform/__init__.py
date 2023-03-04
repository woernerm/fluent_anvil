from ._anvil_designer import TestformTemplate
from anvil import *
from ..lib import Fluent, Message as M

from datetime import timedelta


class Testform(TestformTemplate):
    def __init__(self, **properties):
        self.label.text = "hello"
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        print("Preferred:", Fluent.get_preferred_locales())
        print("Preferred:", Fluent.get_preferred_locales("en_US"))

        fluent = Fluent("test_localization/{locale}/main.ftl", "es_MX", ["es_MX", "en_US"])
        
        print(fluent.format("hello"))
        print(fluent.format("hello", name="John"))
        print(fluent.format("time-elapsed", duration=12342423.234 ))

        #fluent.set_locale("en_US", [])

        print(fluent.format(
            M("hello", name="world"), 
            M("hello", name="world"), 
            M("welcome", name="john")
        ))

        fluent.format(
            M(self.label, "text", "hello", name="John"),
            M(self.text, "placeholder", "hello", name="John")
        )

        print(fluent.js.dom_localization)
        print(fluent.js.localization)

        fluent_hyphen = Fluent("localization/{locale}/main.ftl", "en-US", ["en-US", "es-MX"])
        print("hyphen: ", fluent.format("hello"))
        print("hyphen: ", fluent.format("hello", name="John"))





    
