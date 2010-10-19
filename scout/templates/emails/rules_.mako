<%
    # Import custom modules
    from scout import model
    from scout.model import meta
    # Get rules
    rules = meta.Session.query(model.IMAPMessageRule).filter_by(owner_id=session['personID']).order_by(model.IMAPMessageRule.priority, model.IMAPMessageRule.id)
%>

<table>
    <tr>
        <th class=ruleAction>Action</th>
        <th class=ruleFrom>From</th>
        <th class=ruleTo>To</th>
        <th class=ruleSubject>Subject</th>
        <th class=ruleTag>Tag</th>
    </tr>
    <tr>
        <td class=ruleAction>
            <select id=actionNew>
                <option value='hide'>Make private</option>
            </select>
        </td>
        <td class=ruleFrom><input id=fromNew></td>
        <td class=ruleTo><input id=toNew></td>
        <td class=ruleSubject><input id=subjectNew></td>
        <td class=ruleTag><input id=tagNew></td>
        <td class=ruleInterface>
            <input id=buttonAdd type=button value=Add>
        </td>
    </tr>
% for rule in rules:
    <tr id=rule${rule.id}>
        <td class=ruleAction>\
        % if rule.type == model.action_hide:
            Make private\
        % endif
        </td>
        <td class=ruleFrom>${rule.from_whom}</td>
        <td class=ruleTo>${rule.to_whom}</td>
        <td class=ruleSubject>${rule.subject}</td>
        <td class=ruleTag>${rule.tag}</td>
        <td class=ruleInterface><input class=buttonRemove id=remove${rule.id} type=button value="Remove"></td>
    </tr>
% endfor
</table>
