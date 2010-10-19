<%
    maximum_bound = max(0, c.totalCount - h.RESULTS_PER_PAGE)
    less = max(0, c.startIndex - h.RESULTS_PER_PAGE)
    more = min(maximum_bound, c.startIndex + h.RESULTS_PER_PAGE)
%>

% if c.startIndex > 0:
    <a class="jump linkOFF" id=jump${0}>0</a>
    <a class="jump linkOFF" id=jump${less}">&lt;&lt;</a>
% else:
    0
    &lt;&lt;
% endif

<input id=startIndex class=normalFONT value=${c.startIndex}>

% if c.startIndex < maximum_bound:
    <a class="jump linkOFF" id=jump${more}">&gt;&gt;</a>
    <a class="jump linkOFF" id=jump${maximum_bound}">${c.totalCount}</a>
% else:
    &gt;&gt;
    ${c.totalCount}
% endif
