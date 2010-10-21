<%inherit file="/base.mako"/>

<%def name="title()">Email Accounts</%def>

<%def name="css()">
.deactivated {
    color: gray;
}
.right {
    text-align: right;
}
</%def>

<%def name="js()">
function loadAccount(button) {
    var accountObject = $(button.parentNode.parentNode);
    var accountButton = $(button);
    var accountID = /account(\d+)/.exec(accountObject.attr('id'))[1];
    return {
        button: accountButton,
        object: accountObject,
        id: accountID,
        is_active: accountButton.val() == 'Deactivate' ? 1 : 0,
        status: $('#account' + accountID + '_status')
    }
}
function activateAccount(button) {
    var account = loadAccount(button);
    var is_active_new = account.is_active ? 0 : 1; // Toggle
    $.post("${h.url_for('account_activate')}", {
        id: account.id,
        is_active: is_active_new
    }, function () {
        if (is_active_new) {
            account.object.removeClass('deactivated');
            account.button.val('Deactivate');
        } else {
            account.object.addClass('deactivated');
            account.button.val('Activate');
        }
    });
}
function checkAccount(account) {
    var statusText;
    if (!account.is_active) {
        account.status.html('Deactivated');
        return;
    } else {
        $.get("${h.url_for('account_check')}", {
            id: account.id
        }, function(data) {
            account.status.html(data.isOk ? 'OK' : 'Please change the password');
        }, 'json');
    }
}
$('.button_activate').click(function() {
    activateAccount(this);
}).each(function () {
    checkAccount(loadAccount(this));
});
$('.button_password_change').click(function() {
    var account = loadAccount(this);
    $(this).hide();
    $('#account' + account.id + '_password_input').show().focus();
});
$('.password').blur(function() {
    // Get
    var account = loadAccount(this);
    var password = $(this).val();
    // If the user typed a password,
    if (password) {
        $.post("${h.url_for('account_change')}", {
            id: account.id,
            password: password
        }, function(data) {
            account.status.html(data.isOk ? 'OK' : 'Please change the password');
            $('#account' + account.id + '_password_input').hide();
            $('#account' + account.id + '_password_button').show();
        }, 'json');
    } else {
        $('#account' + account.id + '_password_input').hide();
        $('#account' + account.id + '_password_button').show();
    }
}).hide();
$('#button_add').click(function() {
    // Load
    var ownerID = $('#new_ownerID').val();
    var host = $.trim($('#new_host').val());
    var username = $.trim($('#new_username').val());
    var password = $.trim($('#new_password').val());
    // If the user entered a value for each field,
    if (ownerID > 0 && host && username && password) {
        $.post("${h.url_for('account_add')}", {
            ownerID: ownerID,
            host: host,
            username: username,
            password: password
        }, function(data) {
            if (data.isOk) {
                window.location.reload(); // Reload page
            } else {
                $('#new_status').html('Please check your information');
                $('#new_host').focus();
            }
        }, 'json');
    } else {
        $('#new_status').html('All fields are required.');
    }
});
</%def>

<h2>Email accounts</h2>
<table class=maximumWidth>
    <tr>
        <td><b>Owner</b></td>
        <td><b>Host</b></td>
        <td><b>Username</b></td>
        <td><b>Password</b></td>
        <td><b>Action</b></td>
        <td><b>Archived</b></td>
        <td class=right><b>Statistics</b></td>
        <td class=right><b>Status</b></td>
    </tr>
<%
    import datetime
    from scout import model
    from scout.model import meta
%>
% for imapAccount in c.imapAccounts:
    <%
        divID = 'account%d' % imapAccount.id
    %>
    <tr id=${divID}\
    % if not imapAccount.is_active:
    class=deactivated\
    % endif
    >
        <td>
        % if imapAccount.owner.is_active:
            ${imapAccount.owner.nickname}
        % else:
            <s>${imapAccount.owner.nickname}</s>
        % endif
        </td>
        <td>${imapAccount.host}</td>
        <td>${imapAccount.username}</td>
        <td>
        % if h.isPersonSuper() or session['personID'] == imapAccount.owner_id:
            <input class=button_password_change type=button value=Change id=${divID}_password_button>
            <input class=password type=password id=${divID}_password_input>
        % endif
        </td>
        <td>
            <input class=button_activate value=\
        % if imapAccount.is_active:
            Deactivate\
        % else:
            Activate\
        % endif
        % if h.isPersonSuper() or session['personID'] == imapAccount.owner_id:
            type=button 
        % else:
            type=hidden 
        % endif
            >
        </td>
        <td>
        % if imapAccount.when_archived:
            ${(imapAccount.when_archived + datetime.timedelta(minutes=session['offset_in_minutes'])).strftime('%m/%d/%y %H:%M')}
        % endif
        </td>
        <td class=right>
            ${meta.Session.query(model.IMAPMessage).filter_by(imap_account_id=imapAccount.id).filter(model.IMAPMessage.message_status > model.message_incomplete).count()} messages
        </td>
        <td id=${divID}_status class=right></td>
    </tr>
% endfor
% if h.isPersonSuper():
    <tr>
        <td>
            <select id=new_ownerID>
                <option value=0></option>
            % for person in c.people:
                <option value=${person.id}>${person.nickname}</option>
            % endfor
            </select>
        </td>
        <td><input id=new_host></td>
        <td><input id=new_username></td>
        <td><input id=new_password type=password></td>
        <td class=center><input id=button_add type=button value=Add></td>
        <td colspan=3 id=new_status></td>
    </tr>
% endif
</table>
