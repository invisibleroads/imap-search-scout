<%
    # Import custom modules
    from scout import model
    from scout.lib import mail_format
%>

<div id=summary class=hLeft1>
<table class=maximumWidth>
    <tr>
        <td class=attachmentCount><b>&amp;</b></td>
        <td class=subject><b>Subject</b></td>
        <td class=from><b>From</b></td>
        <td class=to><b>To</b></td>
        <td class=date><b>Date</b></td>
    </tr>
% for match in c.matches:
<%
    message = match['message']
    documentID = message.id
    attachmentCount = len(match['attachmentPacks'])
%>
    <tr id=summary${documentID} class="summary">
        <td id=attachmentCount${documentID} class=attachmentCount>
        % if attachmentCount:
            ${attachmentCount}
        % endif
        </td>
        <td id=subject${documentID} class="subject subjectOFF">
            ${h.clipString(message.subject, 60)}
        </td>
        <td id=from${documentID} class=from>
            ${h.clipString(mail_format.formatNameString(message.from_whom), 20)}
        </td>
        <td id=to${documentID} class=to>
            ${h.clipString(mail_format.formatNameString(message.to_cc_bcc), 20)}
        </td>
        <td id=date${documentID} class=date>
            ${message.when.strftime('%b %d %Y %I%p')}
        </td>
    </tr>
% endfor
</table>
</div>

<div id=info class=hLeft2>
% for match in c.matches:
<%
    message = match['message']
    document = match['document']
    documentID = message.id
%>
<div id=info${documentID} class=info>


<div class=info_visibility>
<b>Visibility</b><br>
<span id=visibility${documentID} class=visibility>
    % if document.getPrivacy():
        Private
    % else:
        Public
    % endif
</span>
% if model.message_delete == message.message_status:
(deletion pending)
% else:
<select id=visibilityMode${documentID} class=visibilityMode>
<%
    valuePacks = [
        (model.message_ok, 'Via rules and tags'),
        (model.message_hide, 'Force private'),
        (model.message_show, 'Force public'),
    ]
%>
% for value, option in valuePacks:
    <option value=${value} 
    % if value != message.message_status:
        >${option}
    % else:
        selected>${option}
        % if message.message_status_changed:
            (pending)\
        % endif
    % endif
    </option>
% endfor
</select>
% endif
</div>
<br>


<div class=info_actions>
<b>Actions</b><br>
<a class="linkOFF reply" id=reply${documentID}>Reply</a>
<a class="linkOFF forward" id=reply${documentID}>Forward</a>
<a class="linkOFF revive" id=revive${documentID}>Revive</a>
% if model.message_delete != message.message_status:
<a class="linkOFF delete" id=delete${documentID}>Delete</a>
% endif
</div>
<br>


% if match['attachmentPacks']:
<div class=info_attachments>
<b>Attachments</b><br>
% for fileNumber, attachmentName, attachmentExtension in match['attachmentPacks']:
    <a href="${url('mail_download', documentID=documentID, fileNumber=fileNumber)}" class=linkOFF target="_blank">${attachmentName}</a><br>
% endfor
</div>
<br>
% endif


% if match['partPacks']:
<div class=info_formats>
<b>Formats</b><br>
% for fileNumber, partName, partExtension in match['partPacks']:
    <a href="${url('mail_download', documentID=documentID, fileNumber=fileNumber)}" class=linkOFF target="_blank">${partExtension}</a>
% endfor
</div>
<br>
% endif


<div class=info_tags>
<b>Tags</b><br>
% for tag in message.tags:
    ${tag.text}<br>
% endfor
</div>


</div>
% endfor
</div>

<div id=detail class=hRight>
% for match in c.matches:
<%
    message = match['message']
    documentID = message.id
    document = match['document']
%>
    <div id="detail${documentID}" class=detail>
        ${h.literal(c.highlight(document))}
    </div>
% endfor
</div>
