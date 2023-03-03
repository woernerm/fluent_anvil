import { Localization, DOMLocalization } from "@fluent/dom";
import { FluentBundle, FluentResource } from "@fluent/bundle";
import { getUserLocales } from 'get-user-locale';

/**
 * Load a fluent file for the given locale and url.
 * @param {string} locale - Locale as IETF language tag, e.g. "en-US".
 * @param {string} resourceId - URL template to .ftl file.
 * @returns - Fluent resource.
 */
async function fetch_resource(locale, resourceId) {
    locale = locale.replace("-", "_") // Make Anvil-compatible path.
    const url = resourceId.replace("{locale}", locale);
    const response = await fetch(url);
    const text = await response.text();
    return new FluentResource(text);
  }

  /**
   * Create fluent bundle for the given locale and resource id. Also returns a list
   * of all errors encountered.
   * @param {string} locale - Locale as IETF language tag, e.g. "en-US".
   * @param {string} resourceId - URL template to .ftl file.
   * @param {object} errors - Container for all errors encountered during ftl parsing.
   * @returns {FluentBundle} - Fluent bundle.
   */
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

/**
 * Create a generator function for creating the desired fluent bundle and select a 
 * suitable fallback if necessary.
 * @param {string} locale - Locale as IETF language tag, e.g. "en-US". 
 * @param {list} fallback_locales - Fallback locales as lift of IETF language tags.
 * @param {object} errors - Container for all errors encountered during ftl parsing.
 * @returns - Generator function for returning a fluent bundle.
 */
function create_bundle_generator(locale, fallback_locales, errors){
    return async function* generate_bundles(resourceIds) {
        yield await create_bundle(locale, resourceIds[0], errors);
      
        for (const entry of fallback_locales) {
          yield await create_bundle(entry, resourceIds[0], errors);
        }
    }
} 

/**
 * Tries to detect the user's preferred locale. Returns the given fallback locale if
 * the operation fails.
 * @param {string} fallback - Fallback locale as IETF language tag, e.g. "en-US". 
 * @returns {list} - Returns a list of preferred locales.
 */
export function get_user_locales(fallback){
  if (fallback){
    return getUserLocales({fallbackLocale: fallback, useFallbackLocale: true})
  }
  return getUserLocales()  
}

/**
 * Initialize fluent translation system.
 * @param {string} resource_path_template - URL template to the .ftl files. Use the
 * placeholder {locale} for inserting the desired locale. Since Anvil does not support
 * hypthens in directory names, the placeholder will use underscores, e.g. "en_US".
 * @param {string} locale - Locale as IETF language tag, e.g. "en-US". 
 * @param {list} fallback_locales - Fallback locale as IETF language tag, e.g. "en-US". 
 * @returns {object} Object containing a fluent DOMLocalization and Localization
 * instance. In addition, it also contains containers for all errors encountered during
 * intialization of both instances.
 */
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