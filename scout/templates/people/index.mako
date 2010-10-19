<%inherit file="/base.mako"/>

<%def name="title()">People</%def>

<%def name="toolbar()">${len(c.people)} people</%def>

<%def name="board()">
% if h.isPersonSuper():
<a href="${h.url('person_register')}" class=linkOFF>Register a new user</a>
% endif
</%def>


<table>
% for person in c.people:
<tr>
    <td>
    % if person.is_active:
        ${person.nickname}
    % else:
        <s>${person.nickname}</s>
    % endif
    </td>
    <td>
    % if h.isPersonSuper():
        <input type=button class=button_status id=status${person.id} value=\
        % if person.is_active:
            Deactivate
        % else:
            Activate
        % endif
        >
    % endif
    </td>
</tr>
% endfor
</table>
