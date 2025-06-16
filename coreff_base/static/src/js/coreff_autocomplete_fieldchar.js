/** @odoo-module **/

import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { useChildRef } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { CharField } from "@web/views/fields/char/char_field";
import { useInputField } from "@web/views/fields/input_field_hook";

import { useCoreffAutocomplete } from "@coreff_base/js/coreff_autocomplete_core";

import { useForwardRefToParent, useService } from "@web/core/utils/hooks";
import { useDebounced } from "@web/core/utils/timing";
import { usePosition } from "@web/core/position_hook";

import { useExternalListener, useRef, useState } from "@odoo/owl";

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
              this.state.headOffice
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
    delete data.coreff_company_id_key;
    this.props.record.update(data);
    if (this.props.setDirty) {
      this.props.setDirty(false);
    }
  }
}

class CoreffAutoComplete extends AutoComplete {
  setup() {
    this.nextSourceId = 0;
    this.nextOptionId = 0;
    this.sources = [];

    this.state = useState({
      navigationRev: 0,
      optionsRev: 0,
      open: false,
      activeSourceOption: null,
      value: this.props.value,
      headOffice: true,
    });

    this.inputRef = useForwardRefToParent("input");
    this.root = useRef("root");

    this.debouncedProcessInput = useDebounced(async () => {
      const currentPromise = this.pendingPromise;
      this.pendingPromise = null;
      this.props.onInput({
        inputValue: this.inputRef.el.value,
      });
      try {
        await this.open(true);
        currentPromise.resolve();
      } catch {
        currentPromise.reject();
      } finally {
        if (currentPromise === this.loadingPromise) {
          this.loadingPromise = null;
        }
      }
    }, this.constructor.timeout);

    useExternalListener(window, "scroll", this.externalClose, true);
    useExternalListener(window, "pointerdown", this.externalClose, true);

    this.hotkey = useService("hotkey");
    this.hotkeysToRemove = [];

    super.setup();
    owl.onWillUpdateProps((nextProps) => {
      if (this.props.value !== nextProps.value || this.forceValFromProp) {
        this.forceValFromProp = false;
        this.state.value = nextProps.value;
        this.inputRef.el.value = nextProps.value;
      }
    });

    // position and size
    usePosition(() => this.inputRef.el, {
      popper: "sourcesList",
      position: "bottom-start",
    });
  }

  async onUpdateHeadOffice(ev) {
    this.state.headOffice = ev.target.checked;
    this.props.onHeadOfficeCheck(this.state.headOffice);
    await this.onInput();
  }
}
CoreffAutoComplete.template = "coreff_base.AutoComplete";
CoreffAutoComplete.props = {
  ...AutoComplete.props,
  onHeadOfficeCheck: { type: Function, optional: true },
};

PartnerAutoCompleteCharField.template =
  "coreff_base.PartnerAutoCompleteCharField";
PartnerAutoCompleteCharField.components = {
  ...CharField.components,
  CoreffAutoComplete,
};

registry
  .category("fields")
  .add("field_coreff_autocomplete", PartnerAutoCompleteCharField);
