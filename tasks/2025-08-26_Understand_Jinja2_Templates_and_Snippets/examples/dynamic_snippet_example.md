# Example Dynamic Snippet

## User Info
Hello {{ username | default('Guest') }}!

{% if items %}
## Items:
{% for item in items %}
- {{ item }}
{% endfor %}
{% else %}
No items provided.
{% endif %}
