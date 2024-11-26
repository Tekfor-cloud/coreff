/** @odoo-module **/

import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { useChildRef } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { CharField } from "@web/views/fields/char/char_field";
import { useInputField } from "@web/views/fields/input_field_hook";

import { useCoreffAutocomplete } from "@coreff_base/js/coreff_autocomplete_core";

export class PartnerAutoCompleteCharField extends CharField {
  setup() {
    super.setup();

    this.partner_autocomplete = useCoreffAutocomplete();

    this.inputRef = useChildRef();
    useInputField({
      getValue: () => this.props.value || "",
      parse: (v) => this.parse(v),
      ref: this.inputRef,
    });
  }

  async validateSearchTerm(request) {
    if (this.props.name == "vat") {
      return this.partner_autocomplete.isTAXNumber(request);
    } else {
      return request && request.length > 2;
    }
  }

  get sources() {
    return [
      {
        options: async (request) => {
          if (await this.validateSearchTerm(request)) {
            const suggestions = await this.partner_autocomplete.autocomplete(
              request,
              this.props.name !== "name",
              this.props.record.data.country_id[0],
              false
            );
            suggestions.forEach((suggestion) => {
              suggestion.classList = "partner_autocomplete_dropdown_char";
            });
            return suggestions;
          } else {
            return [];
          }
        },
        optionTemplate: "coreff_base.CharFieldDropdownOption",
        placeholder: _t("Searching Autocomplete..."),
      },
    ];
  }

  async onSelect(option) {
    const data = await this.partner_autocomplete.getCreateData(
      Object.getPrototypeOf(option)
    );

    if (data.logo) {
      const logoField =
        this.props.record.resModel === "res.partner" ? "image_1920" : "logo";
      data.company[logoField] = data.logo;
    }

    // Some fields are unnecessary in res.company
    if (this.props.record.resModel === "res.company") {
      const fields = ["comment", "child_ids", "additional_info"];
      fields.forEach((field) => {
        delete data.company[field];
      });
    }

    // Format the many2one fields
    const many2oneFields = ["country_id", "state_id"];
    many2oneFields.forEach((field) => {
      if (data.company[field]) {
        data.company[field] = [
          data.company[field].id,
          data.company[field].display_name,
        ];
      }
    });
    this.props.record.update(data.company);
    if (this.props.setDirty) {
      this.props.setDirty(false);
    }
  }
}

PartnerAutoCompleteCharField.template =
  "coreff_base.PartnerAutoCompleteCharField";
PartnerAutoCompleteCharField.components = {
  ...CharField.components,
  AutoComplete,
};

registry
  .category("fields")
  .add("field_coreff_autocomplete", PartnerAutoCompleteCharField);
