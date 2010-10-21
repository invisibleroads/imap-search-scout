<%inherit file="/base.mako"/>\
\
<%def name="title()">Email Rules</%def>\
\
<%def name="toolbar()">
Rules for processing your email
</%def>\
\
<%def name="js()">
function refresh() {
    $('#buttonAdd').click(function() {
        var fromNew = $.trim($('#fromNew').val());
        var toNew = $.trim($('#toNew').val());
        var subjectNew = $.trim($('#subjectNew').val());
        var tagNew = $.trim($('#tagNew').val());
        if (fromNew || toNew || subjectNew || tagNew) {
            var input = {action: $('#actionNew').val(), from: fromNew, to: toNew, subject: subjectNew, tag: tagNew};
            $.post("${h.url_for('rule_add')}", input, function(data) {
                $('#main').html(data);
                $('#toolbar').html('It may take up to an hour for changes to take effect.');
                refresh();
            });
        }
    });
    $('.buttonRemove').click(function() {
        var ruleID = /remove(\d+)/.exec(this.id)[1];
        $.post("${h.url_for('rule_remove')}", {
            id: ruleID
        }, function(data) {
            if (data.isOk) {
                $('#rule' + ruleID).hide();
            }
        }, 'json');
    });
}
refresh()
</%def>\
\
<%include file='/emails/rules_.mako'/>
