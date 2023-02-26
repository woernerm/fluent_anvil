import { Localization, DOMLocalization } from "@fluent/dom";
import { FluentBundle, FluentResource } from "@fluent/bundle";
import { getUserLocales } from 'get-user-locale';


async function fetch_resource(locale, resourceId) {
    locale = locale.replace("-", "_") // Make Anvil-Compatible path
    const url = resourceId.replace("{locale}", locale);
    const response = await fetch(url);
    const text = await response.text();
    return new FluentResource(text);
  }

async function create_bundle(locale, resourceId, errors) {
    let resource = await fetch_resource(locale, resourceId);
    let bundle = new FluentBundle(locale);
    errors.entries += bundle.addResource(resource);

    // Output errors, if any.
    for (const entry of errors.entries) {
      console.log("Error creating bundle for locale " + locale + entry)
    }
    return bundle;
}

function create_bundle_generator(locale, fallback_locales, errors){
    return async function* generate_bundles(resourceIds) {
        yield await create_bundle(locale, resourceIds[0], errors);
      
        for (const entry of fallback_locales) {
          yield await create_bundle(entry, resourceIds[0], errors);
        }
    }
} 

export function get_user_locales(fallback){
  if (fallback){
    return getUserLocales({fallbackLocale: fallback, useFallbackLocale: true})
  }
  return getUserLocales()  
}

export function init_localization(resource_path_template, locale, fallback_locales){
  let dom_errors = {entries: []}
  let main_errors = {entries: []}  
  
  const dom_bundle_gen = create_bundle_generator(locale, fallback_locales, dom_errors)
  const loc_bundle_gen = create_bundle_generator(locale, fallback_locales, main_errors)
    
    
  // Activate DOM localization
  const dom = new DOMLocalization(
      [resource_path_template], 
      dom_bundle_gen
  );
  dom.connectRoot(document.documentElement);
  dom.translateRoots(); 

  const main = new Localization([resource_path_template], loc_bundle_gen)

  return {
    dom: dom, 
    dom_errors: dom_errors.entries,
    main: main, 
    main_errors: main_errors.entries
  }
}

