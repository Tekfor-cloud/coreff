/** @odoo-module **/
/* global checkVATNumber */

import { _t } from "@web/core/l10n/translation";
import { KeepLast } from "@web/core/utils/concurrency";
import { useService } from "@web/core/utils/hooks";

/**
 * Get list of companies via Autocomplete API
 *
 * @param {string} value
 * @returns {Promise}
 * @private
 */
export function useCoreffAutocomplete() {
  const keepLastOdoo = new KeepLast();

  const orm = useService("orm");

  async function autocomplete(
    value,
    valueIsCompanyCode,
    countryId,
    isHeadOffice,
  ) {
    value = value.trim();
    return await getSuggestions(
      value,
      valueIsCompanyCode,
      countryId,
      isHeadOffice,
    );
  }

  /**
   * Get enriched data + logo before populating partner form
   *
   * @param {Object} company
   * @returns {Promise}
   */
  function getCreateData(company) {
    const fields = [
      "country_id",
      "classList",
      "skip_enrich",
      "query",
      "coreff_company_id_key",
      "description",
    ];
    fields.forEach((field) => {
      delete company[field];
    });
    return new Promise((resolve) => {
      return resolve(company);
    });
  }

  /**
   * Use Odoo Autocomplete API to return suggestions
   *
   * @param {string} value
   * @param {boolean} isVAT
   * @returns {Promise}
   * @private
   */
  async function getSuggestions(
    value,
    valueIsCompanyCode,
    countryId,
    isHeadOffice,
  ) {
    const prom = orm.silent.call("coreff.api", "get_companies", [
      {
        valueIsCompanyCode: valueIsCompanyCode,
        country_id: countryId,
        is_head_office: isHeadOffice,
        value: value,
      },
    ]);

    const suggestions = await keepLastOdoo.add(prom);
    await Promise.all(
      suggestions.map(async (suggestion) => {
        suggestion.query = value; // Save queried value (name, VAT) for later
        suggestion.description = "";
        if (suggestion.coreff_company_code) {
          suggestion.description += suggestion.coreff_company_code;
        }
      }),
    );
    return suggestions;
  }

  return { autocomplete, getCreateData };
}
