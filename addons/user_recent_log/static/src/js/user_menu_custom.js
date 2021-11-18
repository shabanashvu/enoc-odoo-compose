odoo.define('user_recent_log.CustomUserMenu', function (require) {
var UserMenu = require('web.UserMenu');

var CustomUserMenu = UserMenu.include({
    template: 'UserMenu',

    _onMenuActivity: function () {
        var self = this;
        var session = this.getSession();
        this.trigger_up('clear_uncommitted_changes', {
            callback: function () {
                self._rpc({
                        route: "/web/action/load",
                        params: {
                            action_id: "user_recent_log.action_user_activity",
                        },
                    })
                    .then(function (result) {
                        result.res_id = self.uid;
                        self.do_action(result);
                    });
            },
        });
    },
})

return CustomUserMenu;

});