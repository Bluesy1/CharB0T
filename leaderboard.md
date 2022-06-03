---
title: Leaderboard
layout: default
---


<h1 style="text-align: center">Charlie's Leaderboard</h1>

<table>
<tr>
<th>Level 1</th>
<th>Level 5</th>
<th>Level 10</th>
<th>Level 15</th>
<th>Level 25</th>
<th>Level 30</th>
</tr>
<tr>
<td style="color: #be6782">Supermax</td>
<td style="color: #fd6a5f">Maximum Security</td>
<td style="color: #E67E22FF">Medium Security</td>
<td style="color: #daeeaf">Minimum Security</td>
<td style="color: #6dbee7">Parole Eligible</td>
<td style="color: #8bbff5">Released</td>
</table>


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
{% else %}
{{ nil }}
{% endcase %}
{% assign num = {{  user.prestige  }} %}
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
