<%inherit file='/base.mak'/>
<%namespace name='form' file='/form.mak'/>

<%def name='title()'>IMAP Accounts</%def>

<%def name='css()'>
.left {text-align: left}
.right {text-align: right}
th.right {padding-right: 20px}
</%def>

<%def name='toolbar()'>IMAP Accounts</%def>

<%def name='root()'>
<link rel=stylesheet href="${request.static_url('scout:static/dataTables/style.css')}">
<script src="${request.static_url('scout:static/dataTables/jquery.dataTables.min.js')}"></script>
<script src="${request.static_url('scout:static/dataTables/jquery.dataTables.titleString.min.js')}"></script>
</%def>

<%def name='js()'>
$('#accountAdd').click(function() {
	// Lock controls
	$('.lockOnSave').attr('disabled', 'disabled');

	// Load
	var accountUserID = $('#accountUserID').val();
	var accountHost = $.trim($('#accountHost').val());
	var accountUsername = $.trim($('#accountUsername').val());
	var accountPassword = $('#accountPassword').val();
	var accountStatus = 'Testing...';
	var accountFocus;

	// Check for errors
	if (!accountUsername) {
		accountStatus = 'Username required';
		accountFocus = $('#accountUsername');
	}
	if (!accountHost) {
		accountStatus = 'Host required';
		accountFocus = $('#accountHost');
	}
	$('#accountStatus').html(accountStatus);
	if (accountFocus) {
		$('.lockOnSave').removeAttr('disabled');
		accountFocus.focus();
		return;
	}

	// Add account
	post("${request.route_path('account_add')}", {
		token: token,
		accountUserID: accountUserID,
		accountHost: accountHost,
		accountUsername: accountUsername,
		accountPassword: accountPassword
	}, function(data) {
		$('.lockOnSave').removeAttr('disabled');
		if (data.isOk) {
			$('#imapAccounts').html(data.content);
		} else {
			$('#accountStatus').html(data.message);
		}
	});
});

function computeTableHeight() {return $(window).height() - 100}
var imapAccountsTable = $('#imapAccounts').dataTable({
	'bInfo': false,
	'bPaginate': false,
	'oLanguage': {'sSearch': 'Filter'},
	'sScrollY': computeTableHeight()
});
$(window).bind('resize', function() {
	$('.dataTables_scrollBody').height(computeTableHeight());
	imapAccountsTable.fnAdjustColumnSizing();
});
$('.dataTables_filter input').focus();
</%def>

<%!
import whenIO
%>

<table id=imapAccounts>
	<thead>
		<tr>
			<th class=left>User</th>
			<th class=left>Host</th>
			<th class=left>Username</th>
			<th class=left>Password</th>
			<th class=right>Action</th>
			<th class=right>Status</th>
			<th class=right>Archived Inbox</th>
			<th class=right>Archived Total</th>
			<th class=right>Statistics</th>
		</tr>
	</thead>
	<tbody>
	% if IS_SUPER:
		<tr>
			<td class=left>${form.formatSelect('accountUserID', USER_ID, personPacks)}</td>
			<td class=left><input id=accountHost class=lockOnSave></td>
			<td class=left><input id=accountUsername class=lockOnSave></td>
			<td class=left><input id=accountPassword class=lockOnSave type=password></td>
			<td class=right><input id=accountAdd class=lockOnSave type=button value=Add></td>
			<td class=right id=accountStatus></span></td>
			<td class=right></td>
			<td class=right></td>
			<td class=right></td>
		</tr>
	% endif
	</tbody>
	<tbody id=imapAccounts>
		<%include file='accounts.mak'/>
	</tbody>
</table>


<%doc>
<%def name="css()">
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
</%def>

<table>
% for imapAccount, imapMessageCount in c.imapAccounts:
<%
    divID = 'account%d' % imapAccount.id
    userCanUpdate = h.isPersonSuper() or personID == imapAccount.owner_id
%>
    <tr id=${divID} class=${'' if imapAccount.is_active else 'deactivated'}>

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
</table>
</%doc>
