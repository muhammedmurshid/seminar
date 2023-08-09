odoo.define('seminar.leads', function (require) {
    "use strict";
    console.log('ppoo')

    var core = require('web.core');
    var Sidebar = require('web.Sidebar');
    var session = require('web.session');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var ListController = require('web.ListController');

    var SideBar = Widget.extend({
            start: function () {
                var self = this;
                var def;
                var export_label = _t("Export");
                def = this.getSession().user_has_group('remove_export_option.group_hide_export').then(function(has_group) {
                    if (!has_group)
                    {
                        self.items['other'] = $.grep(self.items['other'], function(i){
                            return i && i.label && i.label != export_label;
                        });
                    }
                });
                return Promise.resolve(def).then(this._super.bind(this));
            },
        });
});