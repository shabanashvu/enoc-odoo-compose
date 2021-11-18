odoo.define('user_recent_log.action_manager', function (require) {
"use strict";
var AbstractAction = require('web.AbstractAction');
var concurrency = require('web.concurrency');
var Context = require('web.Context');
var session = require('web.session');
var core = require('web.core');
var Dialog = require('web.Dialog');
var dom = require('web.dom');
var framework = require('web.framework');
var pyUtils = require('web.py_utils');
var Widget = require('web.Widget');
var ActionManager = require('web.ActionManager');
var CustomActionManager = ActionManager.include({

    _executeActionInDialog: function (action, options) {
        var self = this;
        var controller = this.controllers[action.controllerID];
        var widget = controller.widget;

        return this._startController(controller).then(function (controller) {
            var prevDialogOnClose;
            if (self.currentDialogController) {
                prevDialogOnClose = self.currentDialogController.onClose;
                self._closeDialog({ silent: true });
            }

            controller.onClose = prevDialogOnClose || options.on_close;
            var dialog = new Dialog(self, _.defaults({}, options, {
                buttons: [],
                dialogClass: controller.className,
                title: action.name,
                size: action.context.dialog_size,
            }));
            /**
             * @param {Object} [options={}]
             * @param {Object} [options.infos] if provided and `silent` is
             *   unset, the `on_close` handler will pass this information,
             *   which gives some context for closing this dialog.
             * @param {boolean} [options.silent=false] if set, do not call the
             *   `on_close` handler.
             */
            dialog.on('closed', self, function (options) {
                options = options || {};
                self._removeAction(action.jsID);
                self.currentDialogController = null;
                if (options.silent !== true) {
                    controller.onClose(options.infos);
                }
                session.user_context['popup'] = true
            });
            controller.dialog = dialog;

            return dialog.open().opened(function () {
                self.currentDialogController = controller;

                dom.append(dialog.$el, widget.$el, {
                    in_DOM: true,
                    callbacks: [{widget: dialog}, {widget: controller.widget}],
                });
                widget.renderButtons(dialog.$footer);
                dialog.rebindButtonBehavior();

                return action;
            });
        }).guardedCatch(function () {
            self._removeAction(action.jsID);
        });
    },
})

return CustomActionManager;

});
