<%inherit file="/base.mako"/>\
\
<%def name="title()">IMAP Rules</%def>\
\
<%def name="toolbar()">
Rules for processing your email
</%def>\
\
<%def name="js()">
function refresh() {
    $('#addRule').click(function() {
        var from_ = $.trim($('#from_').val());
        var to_ = $.trim($('#to_').val());
        var subject_ = $.trim($('#subject_').val());
        if (!from_ && !to_ && !subject_) return; // Exit if fields are empty
        $.post("${h.url('rule_add')}", {
            action: $('#action_').val(),
            from: from_,
            to: to_,
            subject: subject_
        }, function(data) {
            if (data.isOk) {
                $('#main').html(data.content);
                $('#toolbar').html('It may take up to an hour for changes to take effect.');
                refresh();
            } else {
                alert(data.message);
            }
        }, 'json');
    });
    $('.removeRule').click(function() {
        var ruleID = getID(this);
        $.post("${h.url('rule_remove')}", {
            ruleID: ruleID
        }, function(data) {
            if (data.isOk) {
                $('#rule' + ruleID).hide();
            } else {
                alert(data.message);
            }
        }, 'json');
    });
}
refresh()
</%def>\
\
<%include file='/rules/rules.mako'/>
