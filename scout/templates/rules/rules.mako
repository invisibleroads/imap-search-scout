<table>
    <tr>
        <th class=ruleAction>Action</th>
        <th class=ruleFrom>From</th>
        <th class=ruleTo>To</th>
        <th class=ruleSubject>Subject</th>
    </tr>
    <tr>
        <td class=ruleAction>
            <select id=action_>
                <option value='hide'>Make private</option>
            </select>
        </td>
        <td class=ruleFrom><input id=from_></td>
        <td class=ruleTo><input id=to_></td>
        <td class=ruleSubject><input id=subject_></td>
        <td class=ruleInterface>
            <input id=addRule type=button value=Add>
        </td>
    </tr>
<%
from scout import model
from scout.model import Session
%>
% for rule in Session.query(model.IMAPMessageRule).filter_by(owner_id=h.getPersonID()).order_by(model.IMAPMessageRule.priority, model.IMAPMessageRule.id):
    <tr id=rule${rule.id}>
        <td class=ruleAction>\
        % if rule.type == model.action_hide:
            Make private\
        % endif
        </td>
        <td class=ruleFrom>${rule.from_whom}</td>
        <td class=ruleTo>${rule.to_whom}</td>
        <td class=ruleSubject>${rule.subject}</td>
        <td class=ruleInterface><input class=removeRule id=removeRule${rule.id} type=button value=Remove></td>
    </tr>
% endfor
</table>
