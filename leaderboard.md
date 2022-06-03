---
title: Leaderboard
layout: default
---


# Charlie's Leaderboard


<table>
	<tr>
		<th>Rank</th>
		<th></th>
		<th></th>
		<th>Name</th>
		<th>Messages</th>
		<th>Experience</th>
		<th style="text-align: center">Level</th>
	</tr>
{% for user in site.data.users %}
<tr>
<td><b>{{ user.rank }} </b></td>
<td>
{% case {{user.gang}} %}
{% when "green" %}
{{ site.data.gangs.emoji.green }}
{% when "blue" %}
{{ site.data.gangs.emoji.blue }}
{% when "red" %}
{{ site.data.gangs.emoji.red }}
{% when "yellow" %}
{{ site.data.gangs.emoji.yellow }}
{% when "purple" %}
{{ site.data.gangs.emoji.purple }}
{% when "orange" %}
{{ site.data.gangs.emoji.orange }}
{% when "pink" %}
{{ site.data.gangs.emoji.pink }}
{% when "black" %}
{{ site.data.gangs.emoji.black }}
{% when "white" %}
{{ site.data.gangs.emoji.white }}
{% when "gray" %}
{{ site.data.gangs.emoji.gray }}
{% when "brown" %}
{{ site.data.gangs.emoji.brown }}
{5 else %}
{{ nil }}
{% endcase %}
{% assign num = {{user.prestige}} %}
{% for i in (1..num) %}🏅{% endfor %}
</td>
<td><img alt="pfp" src="{{ user.avatar }}" width="50" /></td>
<td>{{ user.name }}</td>
<td>{{ user.messages }}</td>
<td>{{ user.xp }}</td>
<td>
	{{ user.level }}
	<progress value="{{ user.detailed_xp[0] }}" max="{{ user.detailed_xp[1] }}"></progress>
</td>
</tr>
{% endfor %}
</table>
