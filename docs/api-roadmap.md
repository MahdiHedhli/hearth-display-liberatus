# Observed Hearth REST API roadmap

This page documents REST endpoints observed from the Hearth Android application's own HTTP cache on one owner-operated display. It is an interoperability map, not official Hearth API documentation.

Observed application: com.nativeapp 2.67.0.

No authentication values, family identifiers, profile names, task text, routine names, cookie values, or response payload values are published here. Identifiers in paths are normalized to placeholders.

## Scope and evidence

The Android app keeps an HTTP response cache. Its metadata records request URL, method, status, content type, and response headers. Cached JSON responses also let us infer field names and types without publishing their values.

The table below is the complete /api/hearth/ GET surface observed in the inspected cache. It is not a claim that these are all server endpoints. Mutation routes are generally not represented by an HTTP response cache, so POST, PATCH, and DELETE operations require separate mapping.

Base URL:

~~~text
https://app.hearthdisplay.com/api/hearth/
~~~

All 34 observed route shapes returned JSON. Representative successful entries returned HTTP 200 except one cached task-list stats request that returned 404.

## Endpoint inventory

| Method | Route | Query keys | Cache observations | Status |
| --- | --- | --- | ---: | ---: |
| GET | account/membership |  | 1 | 200 |
| GET | account/membership/link |  | 1 | 200 |
| GET | calendar |  | 1 | 200 |
| GET | device/location |  | 1 | 200 |
| GET | device/lock/status |  | 1 | 200 |
| GET | education |  | 1 | 200 |
| GET | event/v0/family/group_by_day | tf_start, tf_end | 44 | 200 |
| GET | family/device_timezone |  | 1 | 200 |
| GET | family/our |  | 1 | 200 |
| GET | family/our/invite |  | 1 | 200 |
| GET | family/our/member |  | 1 | 200 |
| GET | family/screen_saver/selected |  | 1 | 200 |
| GET | family/{family_id}/streaks |  | 7 | 200 |
| GET | features |  | 1 | 200 |
| GET | meals/categories |  | 1 | 200 |
| GET | meals | start, end | 16 | 200 |
| GET | polling |  | 1 | 200 |
| GET | rewards/by_user/{user_id} |  | 7 | 200 |
| GET | rewards/points/balance |  | 1 | 200 |
| GET | rewards/points/balance/{user_id} |  | 7 | 200 |
| GET | rewards/requests/{user_id} | status | 14 | 200 |
| GET | rewards/requests/{user_id} | status, sort_by | 6 | 200 |
| GET | routines/summary |  | 1 | 200 |
| GET | routines/{routine_id}/details |  | 6 | 200 |
| GET | routines | start_time, end_time | 106 | 200 |
| GET | session/web_discovery |  | 1 | 200 |
| GET | task/recurrence_rule/{rule_id} |  | 11 | 200 |
| GET | task | filter_by, sort_by | 1 | 200 |
| GET | tasklist/ | page, page_size | 1 | 200 |
| GET | tasklist/default |  | 1 | 200 |
| GET | tasklist/default/stats |  | 1 | 200 |
| GET | tasklist/summary | page, page_size | 2 | 200 |
| GET | tasklist/{list_id}/stats |  | 1 | 404 observed |
| GET | tasklist/{list_id} | include_tasks, task_page_size | 2 | 200 |

Observation counts describe only the inspected cache snapshot. They are not API traffic statistics.

## Routines

GET routines?start_time=&end_time= returns profiles with their routines for a time window. Observed routine data includes IDs, names, start/end times, active state, completed and total step counts, recurrence rules, past weekday progress, assigned users, iterations, completion records, and individual steps.

GET routines/summary returns compact per-profile routine state including available/completed steps, whether a routine is scheduled today, formatted recurrence details, week progress, streak length, and points-related fields.

GET routines/{routine_id}/details returns the routine and its individual steps. Step fields include ID, name, order, step type, completion/can-complete state, feeling-step state, recurrence, image metadata, and point value.

These reads are sufficient to answer questions such as "which routines are scheduled today?" and "how many steps are complete?" without screen scraping.

## Tasks and lists

GET task?filter_by=&sort_by= returns task objects. Observed fields include subject, description, assignee metadata, created/start/due/completion timestamps, priority, overdue state, recurrence information, and completion streak.

GET task/recurrence_rule/{rule_id} exposes frequency, interval, start/until, day/month-day constraints, and completion streak.

GET tasklist/summary provides compact list IDs, names, icons, paging information, and incomplete-task counts.

GET tasklist/ exposes richer list metadata: description, icon, ownership/sharing state, display visibility, incomplete count, grouping/view/sort/filter configuration, and action capabilities such as scheduling, points, streaks, priorities, categories, quantity, and sharing.

GET tasklist/{list_id}?include_tasks=&task_page_size= includes grouped sections and actual task objects. Observed task fields include assignee profile, timing, recurrence, priority/overdue state, points, quantity, reminders, streak metadata, and Hearth Helper metadata.

This route is a strong candidate for read-only chores/to-do integration.

## Family, streaks, rewards, and meals

GET family/our returns a family object plus primary-user metadata.

GET family/our/member returns member/profile objects with IDs, names, avatar/color metadata, birthday, responsible-adult state, independence level, notes, and contact records.

GET family/{family_id}/streaks returns a user ID plus routine and task streak collections. The representative cache entry had empty collections, so their inner schema remains open.

Reward reads include per-user rewards, point balance, and reward requests. The observed balance shape contains user_id and balance. Representative reward arrays were empty, so their item schema remains open.

GET meals?start=&end= returns a date span, meal categories, meal days/groups, and individual meals with ID, name, date, category, notes, link, color, and assigned profiles. GET meals/categories returns key, label, and icon fields.

## Feature flags and polling

GET features returns a large feature map. Each feature has is_available and is_enabled booleans.

Observed feature names include routines, todos, lists, meals, profile streaks, routine pausing, routine-step images, task reminders, points/reward gates, multiple Hearth Helper generations, recommendation features, and an mcp_server_enabled flag.

The presence of mcp_server_enabled is only evidence of a feature-flag name. It is not evidence that the tested display exposes an MCP server or that such a server is usable.

GET polling returns a rate, optional delay, and version/change counters for event, family, features, meal, reward, routine, and tasklist data. This appears suitable for deciding which feature families need refreshing.

## Authentication observation

The application's private Chromium/WebView cookie database contains a Secure, HttpOnly cookie named hearth_id scoped to .hearthdisplay.com.

The cookie value was not read or published during this mapping.

This shows that an authenticated Hearth web session exists on the display. It does not yet prove that every REST request uses that cookie or that no other credential is involved. Never put account cookies into source code, issue reports, shell history, or public logs.

## Interoperability direction

A conservative owner-controlled reader can begin with cache-only access, which requires no authentication credential at all, then add allow-listed live GET requests only after authentication behavior is independently verified.

Potential read tools include:

~~~text
get_family_members()
get_routines(start, end)
get_routine_details(routine_id)
get_open_tasks()
get_task_lists()
get_task_list(list_id)
get_streaks(profile)
get_reward_balance(profile)
get_meals(start, end)
~~~

Keep raw Hearth credentials local to the display. Treat mutation calls as a separate project requiring explicit owner intent and validation.

## Limits and update risk

This map is tied to one observed app version and one cache snapshot. Endpoints, parameters, schemas, feature flags, and authentication can change without notice.

The cache proves that the Android application successfully used these GET routes. It does not establish a supported public API contract or the existence of matching mutation endpoints.

Re-run the mapping after major Hearth app updates, and treat removed, renamed, or newly authenticated routes as compatibility changes instead of silently guessing.
