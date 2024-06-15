<div align="center">
  <img alt="tribe" height="200px" src="./img/tribe-logo.png">
  <h1>Tribe AI</h1>
  <p>✨ <b>Low code tool to rapidly build and coordinate multi-agent teams</b> ✨</p>
  <a href="https://github.com/streetlamb/tribe/actions?query=workflow%3ATest" target="_blank"><img src="https://github.com/streetlamb/tribe/workflows/Test/badge.svg" alt="Test"></a>
  <a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/streetlamb/tribe" target="_blank"><img src="https://coverage-badge.samuelcolvin.workers.dev/streetlamb/tribe.svg" alt="Coverage"></a>
</div>

## Table of Conents
- [Table of Conents](#table-of-conents)
- [What is Tribe?](#what-is-tribe)
- [What are some use cases?](#what-are-some-use-cases)
- [Highlights](#highlights)
- [How to get started](#how-to-get-started)
  - [Generate Secret Keys](#generate-secret-keys)
  - [Deploy Tribe locally with Docker (simplest way)](#deploy-tribe-locally-with-docker-simplest-way)
  - [Deploy Tribe on a remote server](#deploy-tribe-on-a-remote-server)
- [Guides and concepts](#guides-and-concepts)
  - [Sequential vs Hierarchical workflows](#sequential-vs-hierarchical-workflows)
    - [Sequential workflows](#sequential-workflows)
    - [Hierarchical workflows](#hierarchical-workflows)
  - [Guides](#guides)
    - [Creating Your First Hierarchical Team](#creating-your-first-hierarchical-team)
    - [Equipping Your Team Member with Skills](#equipping-your-team-member-with-skills)
    - [Creating Your First Sequential Team](#creating-your-first-sequential-team)
    - [Requiring Human Approval Before Skill Execution in Sequential Workflows](#requiring-human-approval-before-skill-execution-in-sequential-workflows)
- [Contribution](#contribution)
- [Release Notes](#release-notes)
- [License](#license)
  

> [!WARNING]
> This project is currently under heavy development. Please be aware that significant changes may occur.

## What is Tribe?
Have you heard the saying, 'Two minds are better than one'? That's true for agents too. Tribe leverages on the langgraph framework to let you customize and coordinate teams of agents easily. By splitting up tough tasks among agents that are good at different things, each one can focus on what it does best. This makes solving problems faster and better.


## What are some use cases?
By teaming up, agents can take on more complex tasks. Here are a few examples of what they can do together:
- **⚽️ Footbal analysis**: Imagine a team of agents where one scours the web for the latest Premier League news, and another analyzes the data to write insightful reports on each team's performance in the new season.
- **🏝️ Trip Planning**:  For planning your next vacation, one agent could recommend the best local eateries, while another finds the top-rated hotels for you. This team makes sure every part of your trip is covered.
- **👩‍💻 Customer Service**:  A customer service team where one agent handles IT issues, another manages complaints, and a third takes care of product inquiries. Each agent specializes in a different area, making the service faster and more efficient.

and many many more!

## Highlights
- **Persistent conversations**: Save and maintain chat histories, allowing you to continue conversations.
- **Observability**: Monitor and track your agents’ performance and outputs in real-time using LangSmith to ensure they operate efficiently.
- **Tool Calling**: Enable your agents to utilize external tools and APIs.
- **Human-In-The-Loop**: Enable human approval before tool calling.
- **Easy Deployment**: Deploy Tribe effortlessly using Docker.
- **Multi-Tenancy**: Manage and support multiple users and teams.

## How to get started

Before deploying it, make sure you change at least the values for:

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`

You can (and should) pass these as environment variables from secrets.

### Generate Secret Keys

Some environment variables in the `.env` file have a default value of `changethis`.

You have to change them with a secret key, to generate secret keys you can run the following command:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the content and use that as password / secret key. And run that again to generate another secure key.


### Deploy Tribe locally with Docker (simplest way)

[Get up and started within minutes on your local machine.](./local-deployment.md)

### Deploy Tribe on a remote server

[Deploy Tribe on your remote server.](./deployment.md)

## Guides and concepts

### Sequential vs Hierarchical workflows

#### Sequential workflows

In a sequential workflow, your agents are arranged in an orderly sequence and execute tasks one after another. Each task can be dependent on the previous task. This is useful if you want to tasks to be completed one after another in a deterministic sequence. 

Use this if:
- Your project has clear, step-by-step tasks.
- The outcome of one task influences the next.
- You prefer a straightforward and predictable execution order.
- You need to ensure tasks are performed in a specific order.

#### Hierarchical workflows

In a hierarchical workflow, your agents are organised into a team-like structure comprising of 'team leader', 'team members' and even other 'sub-team leaders'. The team leader breaks down the task into smaller tasks and delegate them to its team members. After the team members complete these tasks, their responses will be passed to the team leader who then chooses to return the response to the user or delegate more tasks.

Use this if:
- Your tasks are complex and multifaceted.
- You need specialized agents to handle different subtasks.
- Task delegation and re-evaluation are crucial for your workflow.
- You want flexibility in task management and adaptability to changes.

### Guides

#### Creating Your First Hierarchical Team

Log into Tribe using the email and password you set during the installation step.

![login](./img/hierarchical-tutorial/login.png)

Navigate to the 'Teams' page and click on 'Add Team'. Enter a name for your team and click 'Save'.

![create team](./img/hierarchical-tutorial/create-team.png)

Create two additional team members by dragging the handle of the Team Leader node.

![create members](./img/hierarchical-tutorial/create-members.png)

Update the first team member as shown.

![update member 1](./img/hierarchical-tutorial/update-member-1.png)

Update the second team member as shown.

![update member 2](./img/hierarchical-tutorial/update-member-2.png)

Go to the 'Chat' tab and send a question to your team to see how they respond.

![chat](./img/hierarchical-tutorial/chat.png)

Congratulations! You’ve successfully built and communicated with your first multi-agent team on Tribe.

#### Equipping Your Team Member with Skills

Your team member can do more by providing it with a set of skills. Add a skill to your Foodie.

![add skill](./img/skills-tutorial/adding-skill.png)

Now, when you ask your Foodie a question, it will search the web for more up-to-date information!

![chat](./img/skills-tutorial/chat.png)

#### Creating Your First Sequential Team

Create a new team and select the 'Sequential' workflow.

![create team](./img/sequential-tutorial/create-team.png)

Drag and drop to create another team member below 'Worker0'.

![create members](./img/sequential-tutorial/create-members.png)

Update the first team member as shown. Provide the 'wikipedia' skill to this team member.

![update member 1](./img/sequential-tutorial/update-member-1.png)

Update the second team member as shown.

![update member 2](./img/sequential-tutorial/update-member-2.png)

Go to the 'Chat' tab and send a question to your team to see how they respond. Notice that the Researcher will use Wikipedia to do its research. Very cool!

![chat](./img/sequential-tutorial/chat.png)

#### Requiring Human Approval Before Skill Execution in Sequential Workflows

You can require your team members to wait for your approval before executing their skills. Edit your Researcher and select 'Require approval'.

![enable human approval](./img/human-approval-tutorial/enable-human-approval.png)

Now, before the Researcher executes its skills, it will ask you to approve or reject.

![chat before approval](./img/human-approval-tutorial/chat-before-approval.png)

If you approve, the Researcher will continue to execute its skills.

![chat after approval](./img/human-approval-tutorial/chat-after-approval.png)

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
