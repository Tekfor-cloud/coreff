/** @odoo-module **/
/* global checkVATNumber */

import { loadJS } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";
import { KeepLast } from "@web/core/utils/concurrency";
import { useService } from "@web/core/utils/hooks";
import { renderToMarkup } from "@web/core/utils/render";
import { getDataURLFromFile } from "@web/core/utils/urls";
import { session } from "@web/session";

/**
 * Get list of companies via Autocomplete API
 *
 * @param {string} value
 * @returns {Promise}
 * @private
 */
export function useCoreffAutocomplete() {
  const keepLastCoreff = new KeepLast();

  const http = useService("http");
  const notification = useService("notification");
  const orm = useService("orm");

  function sanitizeVAT(value) {
    return value ? value.replace(/[^A-Za-z0-9]/g, "") : "";
  }

  async function isVATNumber(value) {
    // Lazyload jsvat only if the component is being used.
    await loadJS("/partner_autocomplete/static/lib/jsvat.js");

    // checkVATNumber is defined in library jsvat.
    // It validates that the input has a valid VAT number format
    return checkVATNumber(sanitizeVAT(value));
  }

  function isGSTNumber(value) {
    // Check if the input is a valid GST number.
    let isGST = false;
    if (value && value.length === 15) {
      const allGSTinRe = [
        /\d{2}[a-zA-Z]{5}\d{4}[a-zA-Z][1-9A-Za-z][Zz1-9A-Ja-j][0-9a-zA-Z]/, // Normal, Composite, Casual GSTIN
        /\d{4}[A-Z]{3}\d{5}[UO]N[A-Z0-9]/, // UN/ON Body GSTIN
        /\d{4}[a-zA-Z]{3}\d{5}NR[0-9a-zA-Z]/, // NRI GSTIN
        /\d{2}[a-zA-Z]{4}[a-zA-Z0-9]\d{4}[a-zA-Z][1-9A-Za-z][DK][0-9a-zA-Z]/, // TDS GSTIN
        /\d{2}[a-zA-Z]{5}\d{4}[a-zA-Z][1-9A-Za-z]C[0-9a-zA-Z]/, // TCS GSTIN
      ];

      isGST = allGSTinRe.some((re) => re.test(value));
    }

    return isGST;
  }

  async function isTAXNumber(value) {
    const isVAT = await isVATNumber(value);
    const isGST = isGSTNumber(value);
    return isVAT || isGST;
  }

  async function autocomplete(
    value,
    valueIsCompanyCode,
    countryId,
    isHeadOffice
  ) {
    value = value.trim();
    let coreffSuggestions = [];
    if (value.length > 8)
      return new Promise((resolve, reject) => {
        const prom = getCoreffSuggestions(
          value,
          valueIsCompanyCode,
          countryId,
          isHeadOffice
        ).then((suggestions) => {
          coreffSuggestions = suggestions;
        });
        const resolveResults = () => {
          return resolve(coreffSuggestions);
        };
        whenAll([prom]).then(resolveResults, resolveResults);
      });
    else return coreffSuggestions;
  }

  /**
   * Get enrichment data
   *
   * @param {Object} company
   * @param {string} company.website
   * @param {string} company.partner_gid
   * @param {string} company.vat
   * @returns {Promise}
   * @private
   */
  function enrichCompany(company) {
    return orm.call("res.partner", "coreff_enrich_company", [
      company.website,
      company.partner_gid,
      company.vat,
    ]);
  }

  /**
   * Get the company logo as Base 64 image from url
   *
   * @param {string} url
   * @returns {Promise}
   * @private
   */
  async function getCompanyLogo(url) {
    try {
      const base64Image = await getBase64Image(url);
      // base64Image equals "data:" if image not available on given url
      return base64Image
        ? base64Image.replace(/^data:image[^;]*;base64,?/, "")
        : false;
    } catch {
      return false;
    }
  }

  /**
   * Get enriched data + logo before populating partner form
   *
   * @param {Object} company
   * @returns {Promise}
   */
  function getCreateData(company) {
    const fields = ["country_id", "classList", "skip_enrich"];
    fields.forEach((field) => {
      delete company[field];
    });

    return new Promise((resolve) => {
      return resolve(company);
    });
  }

  /**
   * Returns a promise which will be resolved with the base64 data of the
   * image fetched from the given url.
   *
   * @private
   * @param {string} url : the url where to find the image to fetch
   * @returns {Promise}
   */
  function getBase64Image(url) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.onload = () => {
        getDataURLFromFile(xhr.response).then(resolve);
      };
      xhr.open("GET", url);
      xhr.responseType = "blob";
      xhr.onerror = reject;
      xhr.send();
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
  async function getCoreffSuggestions(
    value,
    valueIsCompanyCode,
    countryId,
    isHeadOffice
  ) {
    const prom = orm.silent.call("coreff.api", "get_companies", [
      {
        valueIsCompanyCode: valueIsCompanyCode,
        country_id: countryId,
        is_head_office: isHeadOffice,
        value: value,
        user_id: session.uid,
      },
    ]);
    return await keepLastCoreff.add(prom);
  }

  /**
   * Utility to wait for multiple promises
   * Promise.all will reject all promises whenever a promise is rejected
   * This utility will continue
   *
   * @param {Promise[]} promises
   * @returns {Promise}
   * @private
   */
  function whenAll(promises) {
    return Promise.all(
      promises.map((p) => {
        return Promise.resolve(p);
      })
    );
  }

  /**
   * @private
   * @returns {Promise}
   */
  async function notifyNoCredits() {
    const url = await orm.call("iap.account", "get_credits_url", [
      "partner_autocomplete",
    ]);
    const title = _t("Not enough credits for Partner Autocomplete");
    const content = renderToMarkup(
      "partner_autocomplete.InsufficientCreditNotification",
      {
        credits_url: url,
      }
    );
    notification.add(content, {
      title,
    });
  }

  async function notifyAccountToken() {
    const url = await orm.call("iap.account", "get_config_account_url", []);
    const title = _t("IAP Account Token missing");
    if (url) {
      const content = renderToMarkup(
        "partner_autocomplete.AccountTokenMissingNotification",
        {
          account_url: url,
        }
      );
      notification.add(content, {
        title,
      });
    } else {
      notification.add(title);
    }
  }
  return { autocomplete, getCreateData, isTAXNumber };
}
