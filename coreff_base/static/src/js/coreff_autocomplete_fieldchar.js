/** @odoo-module **/

import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { useChildRef } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { CharField, charField } from "@web/views/fields/char/char_field";
import { useInputField } from "@web/views/fields/input_field_hook";

import { useCoreffAutocomplete } from "@coreff_base/js/coreff_autocomplete_core";

import { useState } from "@odoo/owl";

class CoreffAutoComplete extends AutoComplete {
  static template = "coreff_base.AutoComplete";
  static props = {
    ...AutoComplete.props,
    onHeadOfficeCheck: { type: Function, optional: true },
  };

  async onUpdateHeadOffice(ev) {
    this.state.headOffice = ev.target.checked;
    this.props.onHeadOfficeCheck(this.state.headOffice);
    await this.onInput();
  }
}

export class PartnerAutoCompleteCharField extends CharField {
  static template = "coreff_base.PartnerAutoCompleteCharField";
  static components = {
    ...CharField.components,
    CoreffAutoComplete,
  };

  setup() {
    super.setup();

    this.partner_autocomplete = useCoreffAutocomplete();

    this.inputRef = useChildRef();
    useInputField({
      getValue: () => this.props.value || "",
      parse: (v) => this.parse(v),
      ref: this.inputRef,
    });
    this.state = useState({
      headOffice: true,
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
              this.state.headOffice,
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
      Object.getPrototypeOf(option),
    );
    delete data.coreff_company_id_key;
    this.props.record.update(data);
    if (this.props.setDirty) {
      this.props.setDirty(false);
    }
  }
}

registry.category("fields").add("field_coreff_autocomplete", {
  ...charField,
  component: PartnerAutoCompleteCharField,
});
