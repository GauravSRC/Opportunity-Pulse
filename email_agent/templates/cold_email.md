{# Cold email template — RESEARCH / LAB / PROFESSOR opportunities ONLY.
   Rendered with RAG context (lab page + recent papers) + the user's profile.
   Keep it short, specific, and grounded; never invent publications. #}
Subject: {{ subject }}

Dear Prof. {{ professor_last_name }},

I'm {{ user_name }}, {{ user_headline }}. I read your recent work on
{{ paper_topic }} ({{ paper_citation }}) and was particularly drawn to
{{ specific_point }}.

{{ relevant_background }}  {# 2-3 sentences tying the user's projects/skills to the lab #}

I would be grateful for the chance to contribute to {{ lab_focus }} as
{{ desired_role }}. I've attached my CV and can share code/portfolio on request.

Thank you for your time and consideration.

Best regards,
{{ user_name }}
{{ user_contact }}
