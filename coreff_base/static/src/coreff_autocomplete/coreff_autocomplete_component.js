import { AutoComplete } from "@web/core/autocomplete/autocomplete";

export class CoreffAutoComplete extends AutoComplete {
  static template = "coreff_autocomplete.CoreffAutoComplete";

  setup() {
    super.setup();
    this.isHeadOffice = true;
  }

  // Override of AutoComplete
  loadOptions(options, request) {
    if (typeof options === "function") {
      return options(request, this.isHeadOffice);
    } else {
      return options;
    }
  }

  async toggleIsHeadOffice(ev) {
    this.isHeadOffice = !this.isHeadOffice;
    ev.preventDefault();
    super.close();
    super.open(true);
  }
}
