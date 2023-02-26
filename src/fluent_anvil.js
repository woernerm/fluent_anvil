import { Localization, DOMLocalization } from "@fluent/dom";
import { FluentBundle, FluentResource } from "@fluent/bundle";

async function fetchResource(locale, resourceId) {
    const url = resourceId.replace("{locale}", locale);
    const response = await fetch(url);
    const text = await response.text();
    return new FluentResource(text);
  }

async function createBundle(locale, resourceId) {
    let resource = await fetchResource(locale, resourceId);
    let bundle = new FluentBundle(locale);
    let errors = bundle.addResource(resource);
    if (errors.length) {
      // Syntax errors are per-message and don't break the whole resource
    }
    return bundle;
}

function create_bundle_generator(locale, fallback_locales){
    return async function* generateBundles(resourceIds) {
        yield await createBundle(locale, resourceIds[0]);
      
        for (const entry of fallback_locales) {
          yield await createBundle(entry, resourceIds[0]);
        }
    }
}

export function init_localization(resource_path_template, locale, fallback_locales){
    const bundle_generator = create_bundle_generator(locale, fallback_locales)
    
    // Activate DOM localization
    const l10n = new DOMLocalization(
        [resource_path_template], 
        bundle_generator
    );
    l10n.connectRoot(document.documentElement);
    l10n.translateRoots();

    return [l10n, new Localization([resource_path_template], bundle_generator)]
}

