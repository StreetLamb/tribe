# Tribe

![Tribe Logo](./frontend/src/assets/images/fastapi-logo.svg)

## What is Tribe?
Tribe is an interface that helps you to rapidly build agents and coordinate them to work together in teams. By working in teams, agents are able to tackle more complex tasks. It is built on top of langgraph.

## ✨ What can I use Tribe for?
By working together in teams, agents can perform more complex tasks as each agent have more focused roles. Such tasks include:
- **⚽️ Footbal analysis**: Forming a multi-agent team to analayse the situation of each Premier League team in the new season based on the standings by having one agent search the web for the latest news and another analyse the data and write his analysis.
- **🏝️ Trip Planning**:  Create a trip planning multi-agent team, where one agent can provide you with food recommendations and another agent provide you with hotel recommendations.
- **👩‍💻 Customer Service**:  Forming a multi-agent customer service team, where an agent could be assigned to tackle IT related issues, another could be assigned to handle complains, and another to handle product enquiries.

and many many more!

## Some cool features of Tribe
- Design and build your teams rapidly using drag and drop. No code required.
- Support multiple commercial models (e.g. OpenAI, Google, Anthropic) and local models (In progress).
- Monitor and test your agents using LangSmith.
- Equip your agents with skills to search the web and easily create your own customised skills using Python and LangChain.
- Multi user instance support and oversight.
- Deploy Tribe easily using Docker.

## Quick Start

### Configure

Update configs in the `.env` files to customise your configurations.

Before deploying it, make sure you change at least the values for:

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`

You can (and should) pass these as environment variables from secrets.

Read the [deployment.md](./deployment.md) docs for more details.

### Generate Secret Keys

Some environment variables in the `.env` file have a default value of `changethis`.

You have to change them with a secret key, to generate secret keys you can run the following command:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the content and use that as password / secret key. And run that again to generate another secure key.


### Creating your first tribe

Log into Tribe using the email and password you defined during the installation step.

Navigate to the 'Teams' page, click on 'Create Team', fill in a name for your team, and click 'Create'.

Create two additional team members by dragging the handle of the Team Leader node.

Update the first team member as shown.

Update the second team member as shown.

Navigate to the 'Chat' tab and ask your team a question.

You have just created your first tribe!

## Contribution

Tribe is open sourced and welcome contributions from the community! Check out our [contribution guide](./CONTRIBUTING.md) to get started.

Some ways to contribute:
- Report bugs and issues.
- Enhance our documentation.
- Suggest or contribute new features or enhancements.

## Release Notes

Check the file [release-notes.md](./release-notes.md).

## License

Tribe is licensed under the terms of the MIT license.
