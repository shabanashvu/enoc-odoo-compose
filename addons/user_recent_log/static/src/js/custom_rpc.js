odoo.define('user_recent_log.CustomBasicModel', function (require) {

var BasicModel = require('web.BasicModel');
var Session = require('web.session');
var Changes = false;

var CustomBasicModel = BasicModel.include({

    _fetchRecord: function (record, options) {
        var _super = this._super.bind(this);
        var changes = window.Changes;
        window.Changes = false;
        if (!('popup' in Session.user_context)){
            this._rpc({
                        model: 'user.recent.log',
                        method: 'get_recent_log',
                        args: [record.model, record.res_id, changes],
                    });
        }
        return _super(record, options);
    },

    _generateChanges: function (record, options) {
        var _super = this._super.bind(this);
        var res = _super(record, options);
        window.Changes = res
        return res
    },
})

return CustomBasicModel;

});
