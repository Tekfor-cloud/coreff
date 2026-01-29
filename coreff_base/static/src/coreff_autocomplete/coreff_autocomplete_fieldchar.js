/** @odoo-module **/

import { useChildRef, useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { CharField, charField } from "@web/views/fields/char/char_field";
import { useInputField } from "@web/views/fields/input_field_hook";

import { useCoreffAutocomplete } from "@coreff_base/coreff_autocomplete/coreff_autocomplete_core";
import { CoreffAutoComplete } from "@coreff_base/coreff_autocomplete/coreff_autocomplete_component";

export class CoreffAutoCompleteCharField extends CharField {
  static template = "coreff_autocomplete.CoreffAutoCompleteCharField";
  static components = {
    ...CharField.components,
    CoreffAutoComplete,
  };
  setup() {
    super.setup();

    this.orm = useService("orm");
    this.coreffAutocomplete = useCoreffAutocomplete();

    this.inputRef = useChildRef();
    useInputField({
      getValue: () => this.props.record.data[this.props.name] || "",
      parse: (v) => this.parse(v),
      ref: this.inputRef,
    });
  }

  async validateSearchTerm(request) {
    return request && request.length > 2;
  }

  get sources() {
    return [
      {
        options: async (request, isHeadOffice) => {
          if (await this.validateSearchTerm(request)) {
            let queryCountryId = this.props.record.data?.country_id
              ? this.props.record.data.country_id[0]
              : false;
            const suggestions = await this.coreffAutocomplete.autocomplete(
              request,
              this.props.name !== "name",
              queryCountryId,
              isHeadOffice,
            );
            suggestions.forEach((suggestion) => {
              suggestion.classList = "coreff_autocomplete_dropdown_char";
            });
            return suggestions;
          } else {
            return [];
          }
        },
        optionTemplate: "coreff_autocomplete.DropdownOption",
        placeholder: _t("Searching Coreff..."),
      },
    ];
  }

  async onSelect(option) {
    let data = await this.coreffAutocomplete.getCreateData(
      Object.getPrototypeOf(option),
    );
    await this.props.record.update(data);

    if (this.props.setDirty) {
      this.props.setDirty(false);
    }
  }
}

export const coreffAutoCompleteCharField = {
  ...charField,
  component: CoreffAutoCompleteCharField,
};

registry
  .category("fields")
  .add("field_coreff_autocomplete", coreffAutoCompleteCharField);
