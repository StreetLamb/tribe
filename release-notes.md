# Release Notes

## Latest Changes

* ⬆ Bump dawidd6/action-download-artifact from 4 to 5. PR [#46](https://github.com/StreetLamb/tribe/pull/46) by [@dependabot[bot]](https://github.com/apps/dependabot).
* Upgrade dependencies to fix agent calling wiki tool incorrectly. PR [#35](https://github.com/StreetLamb/tribe/pull/35) by [@StreetLamb](https://github.com/StreetLamb).
* Bump requests from 2.31.0 to 2.32.0 in /backend. PR [#28](https://github.com/StreetLamb/tribe/pull/28) by [@dependabot[bot]](https://github.com/apps/dependabot).

### Security Fixes

* Migrate from python-jose to pyjwt. PR [#30](https://github.com/StreetLamb/tribe/pull/30) by [@StreetLamb](https://github.com/StreetLamb).
* Bump gunicorn from 21.2.0 to 22.0.0 in /backend. PR [#20](https://github.com/StreetLamb/tribe/pull/20) by [@dependabot[bot]](https://github.com/apps/dependabot).
* Bump vite from 5.0.12 to 5.0.13 in /frontend. PR [#18](https://github.com/StreetLamb/tribe/pull/18) by [@dependabot[bot]](https://github.com/apps/dependabot).
* Bump tqdm from 4.66.2 to 4.66.3 in /backend. PR [#19](https://github.com/StreetLamb/tribe/pull/19) by [@dependabot[bot]](https://github.com/apps/dependabot).
* Bump jinja2 from 3.1.3 to 3.1.4 in /backend. PR [#16](https://github.com/StreetLamb/tribe/pull/16) by [@dependabot[bot]](https://github.com/apps/dependabot).

### Features

* Update graph logic to work with anthropic. PR [#45](https://github.com/StreetLamb/tribe/pull/45) by [@StreetLamb](https://github.com/StreetLamb).
* Show errors that occur during streaming. PR [#43](https://github.com/StreetLamb/tribe/pull/43) by [@StreetLamb](https://github.com/StreetLamb).
* Add button to start new chat. PR [#40](https://github.com/StreetLamb/tribe/pull/40) by [@StreetLamb](https://github.com/StreetLamb).
* Add persistence for hierarchical workflow. PR [#39](https://github.com/StreetLamb/tribe/pull/39) by [@StreetLamb](https://github.com/StreetLamb).
* Implement persistent chats and enable continuation of past conversations. PR [#36](https://github.com/StreetLamb/tribe/pull/36) by [@StreetLamb](https://github.com/StreetLamb).
* Enhance onboarding for running production locally. PR [#33](https://github.com/StreetLamb/tribe/pull/33) by [@StreetLamb](https://github.com/StreetLamb).
* Show agent's tool usage in chat. PR [#29](https://github.com/StreetLamb/tribe/pull/29) by [@StreetLamb](https://github.com/StreetLamb).
* Enhance nodes and edges ui. PR [#26](https://github.com/StreetLamb/tribe/pull/26) by [@StreetLamb](https://github.com/StreetLamb).
* Add gpt-4o in available models. PR [#24](https://github.com/StreetLamb/tribe/pull/24) by [@StreetLamb](https://github.com/StreetLamb).
* Enable subgraph's team members messages to be displayed too. PR [#22](https://github.com/StreetLamb/tribe/pull/22) by [@StreetLamb](https://github.com/StreetLamb).
* Feature/sequential flow: Allow creating teams that work sequentially. PR [#17](https://github.com/StreetLamb/tribe/pull/17) by [@StreetLamb](https://github.com/StreetLamb).
* Make chat area scrollable. PR [#13](https://github.com/StreetLamb/tribe/pull/13) by [@StreetLamb](https://github.com/StreetLamb).

### Fixes

* set refetchOnWindowFocus to False for readThread. PR [#41](https://github.com/StreetLamb/tribe/pull/41) by [@StreetLamb](https://github.com/StreetLamb).
* Fix error when last_checkpoint is None. PR [#38](https://github.com/StreetLamb/tribe/pull/38) by [@StreetLamb](https://github.com/StreetLamb).
* Fix edit button in node not properly aligned when description is short. PR [#31](https://github.com/StreetLamb/tribe/pull/31) by [@StreetLamb](https://github.com/StreetLamb).
* Fix isDisabled logic for skills multiselect. PR [#27](https://github.com/StreetLamb/tribe/pull/27) by [@StreetLamb](https://github.com/StreetLamb).
* Ensure complete JSON objects are parsed from streamed data to prevent unterminated string errors. PR [#25](https://github.com/StreetLamb/tribe/pull/25) by [@StreetLamb](https://github.com/StreetLamb).
* Fix issue where subgraph is using main graph's team name. PR [#21](https://github.com/StreetLamb/tribe/pull/21) by [@StreetLamb](https://github.com/StreetLamb).
* Fix first initialisation issues. PR [#12](https://github.com/StreetLamb/tribe/pull/12) by [@StreetLamb](https://github.com/StreetLamb).
* Fix lint errors. PR [#9](https://github.com/StreetLamb/tribe/pull/9) by [@StreetLamb](https://github.com/StreetLamb).
* Fix test workflow due to missing .env file. PR [#8](https://github.com/StreetLamb/tribe/pull/8) by [@StreetLamb](https://github.com/StreetLamb).

### Refactors

* Update teams table row logic and update actionsMenu to stop event propagation. PR [#42](https://github.com/StreetLamb/tribe/pull/42) by [@StreetLamb](https://github.com/StreetLamb).
* Improve test coverage. PR [#37](https://github.com/StreetLamb/tribe/pull/37) by [@StreetLamb](https://github.com/StreetLamb).
* Remove items management. PR [#11](https://github.com/StreetLamb/tribe/pull/11) by [@StreetLamb](https://github.com/StreetLamb).
* Update user in issue-manager workflow. PR [#10](https://github.com/StreetLamb/tribe/pull/10) by [@StreetLamb](https://github.com/StreetLamb).

### Docs

* Add test and coverage status in readme. PR [#15](https://github.com/StreetLamb/tribe/pull/15) by [@StreetLamb](https://github.com/StreetLamb).

### Internal

* ⬆ Bump dawidd6/action-download-artifact from 3.1.4 to 4. PR [#44](https://github.com/StreetLamb/tribe/pull/44) by [@dependabot[bot]](https://github.com/apps/dependabot).
* Refactor docker compose file. PR [#34](https://github.com/StreetLamb/tribe/pull/34) by [@StreetLamb](https://github.com/StreetLamb).
* Update icons, update name color. PR [#32](https://github.com/StreetLamb/tribe/pull/32) by [@StreetLamb](https://github.com/StreetLamb).
* Cleanup release notes. PR [#14](https://github.com/StreetLamb/tribe/pull/14) by [@StreetLamb](https://github.com/StreetLamb).
