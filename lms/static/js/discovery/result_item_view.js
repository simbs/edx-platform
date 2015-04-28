;(function (define) {

define([
    'jquery',
    'underscore',
    'backbone',
    'gettext',
], function ($, _, Backbone, gettext) {
    'use strict';

    return Backbone.View.extend({

        tagName: 'li',
        templateId: '#result_item-tpl',
        className: 'courses-listing-item',

        initialize: function () {
            this.tpl = _.template($(this.templateId).html());
        },

        render: function () {
            var data = _.clone(this.model.attributes);
            // JS dates are always local time, convert to universal time
            data.start = dateUTC(new Date(data.start)).toLocaleDateString();
            data.enrollment_start = dateUTC(new Date(data.enrollment_start)).toLocaleDateString();
            this.$el.html(this.tpl(data));
            return this;
        }

    });

    function  dateUTC(date) {
        return new Date(
            date.getUTCFullYear(),
            date.getUTCMonth(),
            date.getUTCDate(),
            date.getUTCHours(),
            date.getUTCMinutes(),
            date.getUTCSeconds()
        );
    }

});

})(define || RequireJS.define);