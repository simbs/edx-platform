// Backbone Application View: CertificateBulkWhitelist View
/*global define, RequireJS */

;(function(define){
    'use strict';

    define([
            'jquery',
            'underscore',
            'gettext',
            'backbone'
        ],

        function($, _, gettext, Backbone){
            var DOM_SELECTORS = {
                bulk_exception: ".bulk-white-list-exception",
                upload_csv_button: ".upload-csv-button",
                browse_file: ".browse-file",
                bulk_white_list_exception_form: "form#bulk-white-list-exception-form"
            };

            return Backbone.View.extend({
                el: DOM_SELECTORS.bulk_exception,
                events: {
                    'change #browseBtn': 'chooseFile',
                    'click .upload-csv-button': 'uploadCSV'
                },

                initialize: function(options){
                    // Re-render the view when an item is added to the collection
                    this.bulk_exception_url = options.bulk_exception_url
                },

                render: function(){
                    var template = this.loadTemplate('certificate-bulk-white-list');
                    this.$el.html(template(
                        {
                            bulk_exception_url: this.bulk_exception_url
                        }
                    ));
                },

                loadTemplate: function(name) {
                    var templateSelector = "#" + name + "-tpl",
                    templateText = $(templateSelector).text();
                    return _.template(templateText);
                },

                uploadCSV: function(event) {
                    var form = this.$el.find(DOM_SELECTORS.bulk_white_list_exception_form);
                    form.submit(function(event) {
                        event.preventDefault();
                        var data = new FormData(event.currentTarget);
                        data['csrfmiddlewaretoken'] = '{{ csrf_token }}';
                          $.ajax({
                            dataType: 'json',
                            type: form.attr('method'),
                            url: form.attr('action'),
                            data: data,
                            processData: false,
                            contentType: false,
                            success: function(data) {

                            }
                          });
                    });
                },

                chooseFile: function(event) {
                    if (event && event.preventDefault) { event.preventDefault(); }
                    if (event.currentTarget.files.length == 1) {
                        this.$el.find(DOM_SELECTORS.upload_csv_button).removeClass('is-disabled');
                        this.$el.find(DOM_SELECTORS.browse_file).val(
                            event.currentTarget.value.substring(event.currentTarget.value.lastIndexOf("\\") + 1));
                    }
                },


                showSuccess: function(caller_object){
                    return function(xhr){
                        var response = xhr;
                    };
                },

                showError: function(caller_object){
                    return function(xhr){
                        var response = JSON.parse(xhr.responseText);
                    };
                }
            });
        }
    );
}).call(this, define || RequireJS.define);