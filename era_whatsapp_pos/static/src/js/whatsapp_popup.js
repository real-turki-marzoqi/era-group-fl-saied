/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { useService } from "@web/core/utils/hooks";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(TicketScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
    },

    async _sendReceiptToCustomer(destination) {
        const order = this.getSelectedOrder();
        console.log("Calling RPC - Order ID:", order.id, "Phone:", destination);
        const result = await this.pos.data.call('pos.order', 'action_era_sent_receipt_on_whatsapp', [
            [order.id],
            destination,
            null,
            false
        ]);
        console.log("RPC Success:", result);
        return result;
    },

    async onClickSendWhatsapp() {
        //Affichage popup moderne (Odoo 18)
        const order = this.getSelectedOrder();
        const partner = order?.get_partner();
        const mobile = partner?.mobile || "";

        const phone = await makeAwaitable(this.dialog, TextInputPopup, {
            title: "Send Receipt via WhatsApp",
            startingValue: mobile,
            placeholder: "Enter WhatsApp number",
        });

        console.log("Popup result:", phone);
        if (phone) {
            this._sendReceiptToCustomer(phone);
        }
    },

});
