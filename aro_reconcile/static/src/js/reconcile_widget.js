openerp.aro_reconcile = function (instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    var account = instance.web.account;
    console.log("account = " + account);

    instance.web.aro_reconcile = instance.web.aro_reconcile || {};

    instance.web.views.add('tree_account_reconciliation', 'instance.web.aro_reconcile.ReconciliationListView');
    instance.web.aro_reconcile.ReconciliationListView = instance.web.account.ReconciliationListView.extend({
        init: function() {
            this._super.apply(this, arguments);
            var self = this;
            this.target_page = null;
            console.log("init");
        },
        load_list: function() {
            var self = this;
            var tmp = this._super.apply(this, arguments);
            if (this.partners) {
                this.$(".oe_account_next_to").click(function() {
                    self.target_page = self.$(".oe_account_target_value").val();
                    self.current_partner = parseInt(self.target_page);
                    if (self.current_partner > parseInt(self.partners.length)) {
                        self.current_partner = parseInt(self.partners.length) - 1;
                    } else {
                        self.current_partner = parseInt(self.target_page) - 1;
                    }
                    self.next_to_page();
                });
            }
            return tmp;
        },
        next_to_page: function(value) {
            console.log("inh_value = " + this.target_page);
            console.log("inh_current_partner = " + this.current_partner);
            this.search_by_partner();
        },
    });
};
