% for imapAccount in imapAccountPacks:
	<%
	user, host, username = [getattr(imapAccount, x) for x in 'user', 'host', 'username']
	%>
	<tr>
		<td class=left>
		% if user.is_active:
			${user.nickname}
		% else:
			<s>${user.nickname}</s>
		% endif
		</td>
		<td class=left>${host}</td>
		<td class=left>${username}</td>
		<td class=left></td>
		<td class=right></td>
		<td class=right></td>
		<td class=right></td>
		<td class=right></td>
		<td class=right></td>
	</tr>
% endfor
