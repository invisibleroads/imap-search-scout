<%inherit file='/base.mak'/>

<%def name='title()'>IMAP Accounts</%def>

<%def name='css()'>
</%def>

<%def name='toolbar()'>IMAP Accounts</%def>

<%def name='root()'>
<link rel=stylesheet href="${request.static_url('scout:static/dataTables/style.css')}">
<script src="${request.static_url('scout:static/dataTables/jquery.dataTables.min.js')}"></script>
<script src="${request.static_url('scout:static/dataTables/jquery.dataTables.titleString.min.js')}"></script>
</%def>

<%def name='js()'>
</%def>

<%!
import whenIO
%>

<table>
	<thead>
		<tr>
			<th>Host</th>
			<th>Username</th>
		<tr>
	</thead>
	<tbody>
	% for imapAccount in imapAccounts:
		<tr>
			<td>${imapAccount.host}</td>
			<td>${imapAccount.username}</td>
		<tr>
	% endfor
	</tbody>
</table>


<%doc>
<%def name="css()">
.right {text-align: right}
.deactivated {color: gray}
.passwordInput {display: none}
</%def>

<%def name="js()">
function loadAccount(button) {
    var accountID = getID(button);
    return {
        button: $(button),
        object: $(button.parentNode.parentNode),
        id: accountID,
        is_active: $('#account' + accountID + 'Activate').val() == 'Deactivate' ? 1 : 0,
        status: $('#account' + accountID + 'Status')
    };
}
function checkAccount(button) {
    var account = loadAccount(button);
    if (!account.is_active) {
        account.status.html('Deactivated');
        return;
    } else {
        account.status.html('Testing...');
        $.get("${h.url('account_check', accountID='XXX')}".replace('XXX', account.id), function(data) {
            account.status.html(data.isOk ? 'OK' : 'Please check password');
        }, 'json');
    }
}
$('.accountActivate').click(function() {
    var account = loadAccount(this);
    var is_active = account.is_active ? 0 : 1; // Toggle
    $.post("${h.url('account_update', accountID='XXX')}".replace('XXX', account.id), {
        is_active: is_active
    }, function () {
        if (is_active) {
            account.object.removeClass('deactivated');
            account.button.val('Deactivate');
            checkAccount(account.button[0]);
        } else {
            account.object.addClass('deactivated');
            account.button.val('Activate');
            account.status.html('Deactivated');
        }
    });
}).each(function () {
    checkAccount(this);
});
$('.passwordChange').click(function() {
    var account = loadAccount(this),
        accountPasswordInput = $('#account' + account.id + 'PasswordInput'),
        accountPasswordChange = $('#account' + account.id + 'PasswordChange');
    accountPasswordChange.hide();
    accountPasswordInput.show().focus();
});
$('.passwordInput').blur(function() {
    // Get
    var account = loadAccount(this),
        accountStatus = account.status,
        accountPasswordInput = $('#account' + account.id + 'PasswordInput'),
        accountPasswordChange = $('#account' + account.id + 'PasswordChange'),
        accountPassword = accountPasswordInput.val(); 
    if (accountPassword == '') {
        accountPasswordInput.hide();
        accountPasswordChange.show();
        return;
    }
    $.post("${h.url('account_update', accountID='XXX')}".replace('XXX', account.id), {
        password: accountPassword
    }, function(data) {
        if (data.isOk) {
            accountStatus.html('OK');
            accountPasswordInput.hide();
            accountPasswordChange.show();
        } else {
            accountStatus.html('Please check password');
            accountPasswordInput.val('').focus();
        }
    }, 'json');
});
$('#accountAdd').click(function() {
    // Lock
    $('.lockOnSave').attr('disabled', 'disabled');
    // Load
    var ownerID = $('#accountOwnerID').val(),
        host = $.trim($('#accountHost').val())
        username = $.trim($('#accountUsername').val()),
        password = $('#accountPassword').val();
    // Show feedback
    $('#accountStatus').html('Testing...');
    // If the user entered a value for each field,
    if (ownerID > 0 && host && username && password) {
        $.post("${h.url('account_add')}", {
            ownerID: ownerID,
            host: host,
            username: username,
            password: password
        }, function(data) {
            if (data.isOk) {
                window.location.reload();
            } else {
                $('#accountStatus').html('Please check credentials');
            }
        });
    } else {
        $('#accountStatus').html('All fields are required');
    }
    // Unlock
    $('.lockOnSave').removeAttr('disabled');
    // Focus
    $('#accountOwnerID').focus();
});
</%def>

<%
import datetime
from scout import model
from scout.model import Session
personID = h.getPersonID()
%>
<table>
    <tr>
        <td><b>Owner</b></td>
        <td><b>Password</b></td>
        <td><b>Action</b></td>
        <td><b>Archived</b></td>
        <td class=right><b>Statistics</b></td>
        <td class=right><b>Status</b></td>
    </tr>
% for imapAccount, imapMessageCount in c.imapAccounts:
<%
    divID = 'account%d' % imapAccount.id
    userCanUpdate = h.isPersonSuper() or personID == imapAccount.owner_id
%>
    <tr id=${divID} class=${'' if imapAccount.is_active else 'deactivated'}>
        <td>${('%s' if imapAccount.owner.is_active else '<s>%s</s>') % imapAccount.owner.nickname}</td>
        <td>
        % if userCanUpdate:
            <input id=${divID}PasswordChange class=passwordChange type=button value=Change>
            <input id=${divID}PasswordInput class=passwordInput type=password>
        % endif
        </td>
        <td>
            <input id=${divID}Activate class=accountActivate type=${'button' if userCanUpdate else 'hidden'} value=${'Deactivate' if imapAccount.is_active else 'Activate'}>
        </td>
        <td>
        % if imapAccount.when_archived:
            ${h.getWhenIO().format(imapAccount.when_archived)}
        % endif
        </td>
        <td class=right>${imapMessageCount or 0} messages</td>
        <td id=${divID}Status class=right></td>
    </tr>
% endfor
% if h.isPersonSuper():
    <tr>
        <td>
            <select id=accountOwnerID class=lockOnSave>
                <option value=0></option>
            % for person in c.people:
                <option value=${person.id}>${person.nickname}</option>
            % endfor
            </select>
        </td>
        <td><input id=accountHost class=lockOnSave></td>
        <td><input id=accountUsername class=lockOnSave></td>
        <td><input id=accountPassword type=password class=lockOnSave></td>
        <td class=center><input id=accountAdd type=button value=Add class=lockOnSave></td>
        <td colspan=3 id=accountStatus></td>
    </tr>
% endif
</table>


</%doc>
