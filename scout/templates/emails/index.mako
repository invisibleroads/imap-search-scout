<%inherit file="/base.mako"/>\

<%def name="title()">Emails</%def>

<%def name="head()">
${h.javascript_link('/files/jquery.bgiframe.min.js')}
${h.javascript_link('/files/jquery.dimensions.min.js')}
${h.javascript_link('/files/jquery.tooltip.min.js')}
</%def>

<%def name="css()">
#startIndex {width: 5em}
#content {position: absolute; top: 0; bottom: 0; left: 0; right: 0; font-size: small}

.hLeft1 {position: absolute; width: 50%; height: 65%; overflow: auto; left: 0; top: 0}
.hLeft2 {position: absolute; width: 50%; height: 35%; overflow: auto; left: 0; bottom: 0}
.hRight {position: absolute; width: 50%; height: 100%; overflow: auto; right: 0; top: 0}
.vTop {position: absolute; width: 100%; height: 40%; overflow: auto; left: 0; top: 0}
.vBottom1 {position: absolute; width: 25%; height: 60%; overflow: auto; left: 0; bottom: 0}
.vBottom2 {position: absolute; width: 75%; height: 60%; overflow: auto; right: 0; bottom: 0}

#select_messageTag {width: 10em}
#select_attachmentExtension {width: 10em}
#summary {background-color: lightgreen}
#detail {}
.detail {display: none}
.info {display: none}

.highlight {background-color: yellow}

.attachmentCount {width: 2%}
.subject {width: 53%}
.from {width: 15%}
.to {width: 15%}
.date {width: 15%; text-align: right}

.subjectOFF {color: black; background-color: lightgreen}
.subjectON {color: black; background-color: white} 

#tooltip {position: absolute; z-index: 3000; border: 1px solid #111; background-color: #eee; padding: 5px; font-size: small}
</%def>

<%def name="js()">
<%
    from scout import model
%>

function adjustLayout() {
    var summary = $('#summary'), detail = $('#detail'), info = $('#info');
    summary.removeClass('vTop hLeft1');
    detail.removeClass('vBottom2 hRight');
    info.removeClass('vBottom1 hLeft2');
    switch($('#layout').val()) {
        case 'v':
            summary.addClass('vTop'); 
            detail.addClass('vBottom2'); 
            info.addClass('vBottom1');
            break;
        case 'h':
            summary.addClass('hLeft1'); 
            detail.addClass('hRight'); 
            info.addClass('hLeft2');
            break;
    };
    // Adjust content height based on whether help is visible
    if ($('.help:visible').length) {
        $('#content').css('top', $('#help').height() + 'px');
    } else {
        $('#content').css('top', 0);
    }
}
$('#layout').change(adjustLayout);
$('#help_button').click(adjustLayout);

function getButtonNumber(button) { return /\d+/.exec(button.id)[0]; }

var totalCount = 0;
function ajax_search(startIndex) {
    var queryString = $('#input_search').val();
    // If the user did not enter a query,
    if (!$.trim(queryString)) {
        // Browse
        return ajax_browse(startIndex);
    }
    // Initialize
    var arguments = {
        q: queryString,
        startIndex: startIndex,
        totalCount: totalCount,
        sortBy: $('#select_sortBy').val(),
        attachmentExtensionID: $('#select_attachmentExtension').val(),
        messageTagID: $('#select_messageTag').val()
    };
    // Send
    $.getJSON("${h.url_for('mail_search')}", arguments, function (data) {
        if (!data.isOk) {
            alert(data.message);
        }
        refresh_method = ajax_search;
        loadResults(data);
        totalCount = data.totalCount;
        $('#select_sortBy').val(data.sortBy);
        $('.searchResult').show();
    });
};

function loadResults(data) {
    $('#content').html(data.payload); 
    $('#pagination').html(data.pagination);
    $('#startIndex').val(data.startIndex);
    $('.help').hide();
    polishResults();
}

function cleanSubject(subject) { 
    return subject.replace(/^((?:re|fwd|fw):\s*)+/i, ''); 
} 
function prepareBody(body) {
    var oldLines = body.split('\n');
    var newLines = [];
    for (var i=0; i < oldLines.length; i++) {
        newLines.push('> ' + oldLines[i]);
    }
    return newLines.join('%0A');
}

var last_summary, last_detail, last_info;
function polishResults() {
    // Vitalize layout
    adjustLayout();

    // Vitalize summary
    $('.subject').hover(
        function () {
            // Hide old
            if (last_summary && last_detail && last_info) {
                last_summary.className = last_summary.className.replace('ON', 'OFF');
                last_detail.hide();
                last_info.hide();
            }
            // Get documentID
            var documentID = getButtonNumber(this);
            // Show new
            last_summary = this; this.className = this.className.replace('OFF', 'ON');
            last_detail = $('#detail' + documentID); last_detail.show();
            last_info = $('#info' + documentID); last_info.show();
        }, 
        function () {}
    );
    $('.attachmentCount').tooltip({
        bodyHandler: function() {
            return 'Attachment count';
        },
        showURL: false
    });

    // Vitalize pagination
    $('#startIndex').change(function() {refresh_method($('#startIndex').val())});
    $('.jump').click(function() {refresh_method(getButtonNumber(this))});

    // Vitalize actions
    $('.reply').click(function() {
        $.get("${h.url_for('mail_get_plain')}" + '/' + getButtonNumber(this), {}, function(data) {
            if (data.isOk) {
                window.location = 'mailto:' + data.from_whom + '?subject=Re: ' + cleanSubject(data.subject) + '&body=' + prepareBody(data.body);
            } else {
                alert(data.message);
            }
        });
    }).tooltip({
        bodyHandler: function() {
            return 'Reply using your default mail client.  Does not include attachments.';
        },
        showURL: false
    });
    $('.forward').click(function() {
        $.get("${h.url_for('mail_get_plain')}" + '/' + getButtonNumber(this), function(data) {
            if (data.isOk) {
                window.location = 'mailto:?subject=Fwd: ' + cleanSubject(data.subject) + '&body=' + prepareBody(data.body);
            } else {
                alert(data.message);
            }
        });
    }).tooltip({
        bodyHandler: function() {
            return 'Forward message using your default mail client.  Does not include attachments.';
        },
        showURL: false
    });
    $('.revive').click(function() {
        $.post("${h.url_for('mail_revive_plain')}" + '/' + getButtonNumber(this), {
            'whichAccount': $('#select_whichAccount').val()
        }, function(data) {
            if (data.isOk) {
                alert('Message revived in the "' + data.folder + '" folder for ' + data.email);
            } else {
                alert(data.message);
            }
        }, 'json');
    }).tooltip({
        bodyHandler: function() {
            return 'Revive message and attachments to your mail server.';
        },
        showURL: false
    });
    $('.delete').click(function() {
        var documentID = getButtonNumber(this);
        var subjectObj = $('#subject' + documentID);
        if (prompt('Please note that the message will reappear as long as it exists on your mail server. To delete the message permanently, please delete the message on your mail server first, then delete it here. To delete the message entitled "' + $.trim(subjectObj.text()) + '" from the database, type YES and press ENTER.') == 'YES') {
            $.post("${h.url_for('mail_change_plain')}" + '/' + documentID, {
                'status': ${model.message_delete}
            }, function(data) {
                if (data.isOk) {
                    $('#visibilityMode' + documentID).replaceWith('(deletion pending)');
                    $('#delete' + documentID).hide();
                } else {
                    alert(data.message);
                }
            }, 'json');
        }
    }).tooltip({
        bodyHandler: function() {
            return 'Delete message from database.';
        },
        showURL: false
    });;
    $('.visibilityMode').change(function() {
        var documentID = getButtonNumber(this);
        var message_status = $(this).val();
        $.post("${h.url_for('mail_change_plain')}" + '/' + documentID, {
            'status': message_status
        }, function(data) {
            if (data.isOk) {
                $('#visibility' + documentID).html((data.privacy == 0 ? 'Public' : 'Private') + ' (pending)');
            } else {
                alert(data.message);
            }
        }, 'json');
    }).css('font-size', 'small');
    // Hyperlink
    $('#content a, #pagination a').hover(
        function () {this.className = this.className.replace('OFF', 'ON');}, 
        function () {this.className = this.className.replace('ON', 'OFF');}
    );
    $('#input_search').select();
}


function ajax_browse(startIndex) {
    var queryString = $('#input_search').val();
    // If the user entered a query,
    if ($.trim(queryString)) {
        // Search
        return ajax_search(startIndex);
    }
    $.getJSON("${h.url_for('mail_index')}", {
        startIndex: startIndex,
        format: 'json',
        attachmentExtensionID: $('#select_attachmentExtension').val(),
        messageTagID: $('#select_messageTag').val()
    }, function (data) {
        refresh_method = ajax_browse;
        loadResults(data);
    });
}


$('.searchResult').hide();
$('#select_sortBy').change(function() {
    refresh_method(0);
});
$('#select_attachmentExtension').change(function() {
    refresh_method(0);
});
$('#select_messageTag').change(function() {
    refresh_method(0);
});
$('#button_search').click(function() {
    ajax_search(0);
});
$('#input_search').keydown(function(event) {
    switch(event.keyCode) { 
        case 13: 
            ajax_search(0);
            break;
    };
}).focus();


var refresh_method = ajax_browse;
polishResults();
</%def>\

<%def name="toolbar()">\
<input id=input_search class=normalFONT>
<input id=button_search type=button value=Search class=normalFONT>
<select id=select_messageTag>
    <option value='any'>With any tag</option>
% for messageTag in c.messageTags:
    <option value="${messageTag.id}">${messageTag.text}</option>
% endfor
</select>
<select id=select_attachmentExtension>
    <option value='can'>Can have attachment</option>
    <option value='must'> Must have attachment</option>
% for attachmentExtension in c.attachmentExtensions:
    <option value="${attachmentExtension.id}">${attachmentExtension.text}</option>
% endfor
</select>
<select id=select_sortBy class=searchResult>
    <option value=relevance>By relevance</option>
    <option value=date>By date</option>
</select>
</%def>\

<%def name="navigation()">\
% if c.imapAccounts:
    <select id=select_whichAccount>
    % for whichAccount, imapAccount in enumerate(c.imapAccounts):
        <option value=${whichAccount}>${imapAccount.username}@${imapAccount.host}</option>
    % endfor
    </select>
    &nbsp;
% endif
</%def>\

<%def name="board()">\
<select id=layout>
    <option value=v>Vertical</option>
    <option value=h>Horizontal</option>
</select>
&nbsp;
<span id=pagination>
<%include file="pagination.mako"/>
</span>
</%def>\

<div id=help class=help>
<table>
    <tr>
        <td>learning prefrontal</td>
        <td>Match messages containing the word "learning" OR the word "prefrontal"</td>
    </tr>
    <tr>
        <td>+local +neurotransmitter</td>
        <td>Emphasize that every match must contain "local" AND "neurotransmitter"</td>
    </tr>
    <tr>
        <td>prefrontal -neurotransmitter</td>
        <td>Exclude matches containing the word "neurotransmitter"</td>
    </tr>
    <tr>
        <td>"enhances learning" -"causes pain"</td>
        <td>Match phrase "enhances learning" while excluding matches with phrase "causes pain"</td>
    </tr>
    <tr>
        <td>earth NEAR/6 energy</td>
        <td>Match documents with "earth" and "energy" within six words of each other</td>
    </tr>
    <tr>
        <td>earth ADJ/3 energy</td>
        <td>Match documents with "earth" and "energy" within three words of each other in that order</td>
    </tr>
    <tr>
        <td></td>
        <td><a class=helpOFF href=/docs target="_blank"><b>Click here to read the documentation</b></a></td>
    </tr>
</table>
</div>

<div id=content>
<%include file="payload.mako"/>
</div>
