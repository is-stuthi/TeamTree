# TeamTREE --- Project Design Document

**Project title:** TeamTREE: A Skill-Based Project Team Formation and
Collaboration Platform\
**Project type:** End-to-end DBMS application\
**Primary database approach:** Relational SQL database\
**Document purpose:** Consolidate the product idea, scope, conceptual ER
model, business rules, workflows, relational-schema considerations,
analytics, and implementation ideas discussed for TeamTREE.

------------------------------------------------------------------------

## 1. Executive summary

TeamTREE is a platform where people discover potential collaborators,
create projects, recruit people with the skills they need, form teams,
and coordinate work through tasks.

A person can use the platform in different capacities:

-   As a **project owner**, they create a project, define its skill
    requirements, and review applications.
-   As an **applicant**, they discover projects and apply to join them.
-   As a **team member**, they contribute to an accepted project and
    complete assigned tasks.

These are roles played by the same `USER` entity. They do not need to be
separate user entities.

TeamTREE is more than a project-listing website. Its central idea is to
connect **people's skills** with **projects' requirements**. The
database should make it possible to discover suitable collaborators,
identify skill gaps, manage applications and team membership, track
tasks, and produce useful analytics.

The intended product flow is:

**Create profile → Add skills → Create or discover projects → Define or
inspect requirements → Apply → Owner reviews application → Form team →
Assign and complete tasks → Analyse activity and skill demand**

------------------------------------------------------------------------

## 2. Problem statement

People often have project ideas but struggle to find collaborators with
the right skills, interests, experience, and availability. At the same
time, people who want to contribute to projects may find it difficult to
discover opportunities that match what they can do.

TeamTREE addresses this by maintaining structured information about:

-   Users and their skills
-   Projects and their required skills
-   Applications submitted by potential collaborators
-   Project owners and their decisions
-   Teams and their members
-   Tasks and their assignments

This structured information supports both the application's operational
features and database-driven analysis.

------------------------------------------------------------------------

## 3. Goals and objectives

1.  Allow users to create and maintain profiles.
2.  Allow users to add skills and specify their proficiency.
3.  Allow users to create, browse, search, update, and close projects.
4.  Allow project owners to define the skills, proficiency levels,
    roles, and number of people required.
5.  Allow users to apply to projects.
6.  Allow the owner of a project to accept or reject applications.
7.  Form and maintain a team for each project.
8.  Allow teams to divide projects into tasks and assign responsibility.
9.  Support skill-based candidate matching and project recommendations.
10. Provide meaningful analytics using SQL queries.
11. Demonstrate DBMS concepts such as keys, relationships, constraints,
    normalization, joins, transactions, views, triggers, and indexes.

------------------------------------------------------------------------

## 4. Intended users and roles

There is one main type of account: `USER`. A user can have different
roles in different contexts.

  -----------------------------------------------------------------------
  Context                 Role                    What the user can do
  ----------------------- ----------------------- -----------------------
  A project created by    Project owner           Edit/manage the
  the user                                        project, define
                                                  requirements, review
                                                  applications, manage
                                                  the team

  A project created by    Applicant               Browse the project and
  someone else                                    submit an application

  A project whose         Team member             Participate in the team
  application was                                 and work on assigned
  accepted                                        tasks
  -----------------------------------------------------------------------

**Important modelling decision:** `Project Owner`, `Applicant`, and
`Team Member` are contextual roles, not necessarily separate entity
types.

A user may own Project A, apply to Project B, and be a member of Project
C at the same time.

------------------------------------------------------------------------

## 5. Scope

### 5.1 Core scope

The first version should cover:

-   Registration and login
-   User profiles
-   User skills and proficiency
-   Project creation and discovery
-   Project skill requirements
-   Applications and owner decisions
-   Team formation and membership
-   Task creation, assignment, and status tracking
-   Search, filtering, matching, and analytics

### 5.2 Optional enhancements

These can be added if time permits:

-   User-to-user reviews after collaboration
-   Project bookmarks
-   More detailed availability and interest matching
-   Notifications for application decisions and task changes
-   Ownership transfer
-   Team contribution summaries
-   Exportable reports

Reviews and bookmarks were discussed as possible extensions, but they
are **not part of the six-entity core model** described below.

### 5.3 Explicitly out of scope for the initial version

To keep the project manageable, the initial version does not need:

-   Real-time chat or video calls
-   Git hosting or source-code management
-   Payment processing
-   A social-media feed
-   Complex AI/ML models
-   Enterprise-scale project management functionality

A lightweight task-management feature is sufficient.

------------------------------------------------------------------------

## 6. Core conceptual entities

The current conceptual ER model has six main entities:

1.  `USER`
2.  `SKILL`
3.  `PROJECT`
4.  `APPLICATION`
5.  `TEAM`
6.  `TASK`

In a Chen-style conceptual ER diagram, relationships such as `HAS`,
`REQUIRES`, and `JOINS` can have attributes of their own. When the ER
model is converted into relational tables, some many-to-many
relationships will become separate junction relations. That conversion
does not mean the conceptual diagram must treat every junction relation
as an independent business entity.

### 6.1 USER

Represents a registered person using TeamTREE.

Suggested attributes:

  -----------------------------------------------------------------------
  Attribute                           Meaning
  ----------------------------------- -----------------------------------
  `User_ID`                           Unique user identifier; primary key

  `Name`                              User's name

  `Email`                             Unique email address

  `Password_Hash`                     Securely stored password hash;
                                      never store plaintext passwords

  `Bio`                               Short profile description

  `DOB`                               Date of birth

  `Address` or `Location`             General location, if needed

  `Availability`                      User's availability

  `Experience_Level`                  Broad experience level
  -----------------------------------------------------------------------

**Derived attribute:** Age can be derived from `DOB`; it generally
should not be stored because it changes over time.

The exact profile attributes should be limited to information that the
application genuinely needs. For example, a full postal address may be
unnecessary; a city or general location may be enough.

### 6.2 SKILL

Represents a skill that can be associated with users and required by
projects.

  Attribute      Meaning
  -------------- ------------------------------------------------------
  `Skill_ID`     Unique skill identifier; primary key
  `Skill_Name`   Name of the skill
  `Category`     Skill category, such as programming, design, or data

Examples include Python, SQL, Java, React, machine learning, UI/UX, and
cybersecurity.

Use a unique `Skill_ID` rather than relying on the skill name as the
primary key. A uniqueness constraint on a normalized skill name can
prevent duplicate entries such as `Python` and `python`.

### 6.3 PROJECT

Represents a project posted on TeamTREE.

  Attribute         Meaning
  ----------------- ----------------------------------------
  `Project_ID`      Unique project identifier; primary key
  `Project_Name`    Project title
  `Description`     Project description
  `Domain`          Project area or domain
  `Creation_Date`   Date the project was created
  `Deadline`        Target completion date
  `Status`          Project lifecycle status

The creator/owner is represented by the relationship:

**USER --- CREATES --- PROJECT**

In the eventual relational schema, this relationship will normally be
implemented by storing the owner's `User_ID` as a foreign key in
`PROJECT`.

Suggested project statuses include `Open`, `Ongoing`, `Completed`, and
`Closed`. Define the exact meaning of each status so they are not used
interchangeably.

### 6.4 APPLICATION

Represents a user's request to join a particular project.

  Attribute            Meaning
  -------------------- --------------------------------------------
  `Application_ID`     Unique application identifier; primary key
  `Application_Date`   Date/time submitted
  `Message`            Applicant's message or explanation
  `Status`             Current application status

Suggested statuses:

-   `Pending`
-   `Accepted`
-   `Rejected`
-   `Withdrawn`

An application connects one applicant to one project. The applicant and
target project are identified through the `SUBMITS` and `FOR`/`RECEIVES`
relationships.

### 6.5 TEAM

Represents the group working on a project.

  Attribute         Meaning
  ----------------- -------------------------------------
  `Team_ID`         Unique team identifier; primary key
  `Team_Name`       Team name
  `Creation_Date`   Date the team was formed

**Current assumption:** each project has one primary team. Therefore,
`PROJECT — HAS — TEAM` is modelled as 1:1.

If the requirements later change to allow multiple independent teams for
one project, the cardinality must be changed to 1:N.

### 6.6 TASK

Represents a unit of work within a project.

  Attribute       Meaning
  --------------- -------------------------------------
  `Task_ID`       Unique task identifier; primary key
  `Task_Name`     Task title
  `Description`   Task details
  `Priority`      Low, medium, high, etc.
  `Status`        To do, in progress, completed, etc.
  `Due_Date`      Task deadline

Each task belongs to one project. In the current scope, each task has
one responsible user, and that user must be a member of the project's
team.

------------------------------------------------------------------------

## 7. Relationships and cardinalities

The following are the proposed conceptual relationships. Cardinalities
describe how many instances can participate; participation constraints
should also be shown on the ER diagram where required.

### 7.1 USER --- HAS --- SKILL

**Cardinality: M:N**

-   A user can possess many skills.
-   A skill can be possessed by many users.

**Relationship attribute:** `Proficiency_Level`

Example: User U1 has Python at Advanced level and SQL at Intermediate
level.

`Proficiency_Level` belongs to the relationship because it describes how
proficient a particular user is in a particular skill. It is not an
attribute of the skill itself.

### 7.2 USER --- CREATES --- PROJECT

**Cardinality: 1:N**

-   One user can create many projects.
-   Each project has exactly one creator/owner.

The user participates in the `Project Owner` role.

No relationship attribute is required for the initial version.

### 7.3 PROJECT --- REQUIRES --- SKILL

**Cardinality: M:N**

-   A project can require many skills.
-   A skill can be required by many projects.

Suggested relationship attributes:

-   `Required_Level`
-   `Required_Count`
-   `Required_Role`

Example: Project P1 requires Python at Advanced level, for two people,
for the role of ML Developer.

This relationship is central to TeamTREE because it enables matching
between project requirements and user capabilities.

### 7.4 USER --- SUBMITS --- APPLICATION

**Cardinality: 1:N**

-   One user can submit many applications.
-   Each application is submitted by exactly one user.

The user participates in the `Applicant` role.

### 7.5 APPLICATION --- IS FOR / PROJECT --- RECEIVES --- APPLICATION

**Cardinality: PROJECT 1:N APPLICATION**

-   A project can receive many applications.
-   Each application is for exactly one project.

Together, `USER — SUBMITS — APPLICATION` and
`PROJECT — RECEIVES — APPLICATION` associate an applicant with the
project they want to join.

### 7.6 USER --- REVIEWS --- APPLICATION

**Cardinality: 1:N from the reviewing user to applications**

This is a second, distinct relationship between `USER` and
`APPLICATION`.

-   A user acting as a project owner can review many applications.
-   An application, once reviewed, is reviewed by the owner of its
    associated project.
-   The reviewing user must be the owner of the project to which the
    application belongs.

The same `USER` entity participates in two roles:

1.  `Applicant` in `SUBMITS`
2.  `Project Owner / Reviewer` in `REVIEWS`

This is valid ER modelling. The relationships are not redundant because
they represent different actions and roles.

**Possible relationship attribute:** `Decision_Date`.

The decision itself can be represented by `APPLICATION.Status`
(`Accepted` or `Rejected`). Do not store the same decision redundantly
in multiple places without a clear reason.

**Important implementation point:** the reviewer can be derived through
`APPLICATION → PROJECT → Project Owner`. A separate `Reviewer_ID` column
is not necessary in the basic relational schema. If an explicit reviewer
foreign key is stored for audit/history purposes, enforce that it
matches the project's owner at the time of the decision.

### 7.7 PROJECT --- HAS --- TEAM

**Cardinality: 1:1 under the current assumption**

-   Each project has one primary team.
-   Each team belongs to one project.

A project may be created before its team is formed. Therefore, in
practice, the project may have zero or one team during its lifecycle,
while each existing team must belong to one project. The ER diagram
should show the intended participation constraints rather than assuming
a team exists immediately at project creation.

### 7.8 USER --- JOINS / IS MEMBER OF --- TEAM

**Cardinality: M:N**

-   A team has multiple users.
-   A user can participate in multiple teams across different projects.

Suggested relationship attributes:

-   `Role`
-   `Join_Date`

The role belongs to the membership relationship, not permanently to the
user. A person could be a backend developer in one team and a team lead
in another.

### 7.9 PROJECT --- CONTAINS --- TASK

**Cardinality: 1:N**

-   A project can contain many tasks.
-   Each task belongs to exactly one project.

### 7.10 USER --- IS ASSIGNED --- TASK

**Cardinality: 1:N under the current assumption**

-   A user can be responsible for many tasks.
-   Each task has one responsible user.

**Current simplifying assumption:** one assigned user per task. If
collaborative tasks with multiple assignees are required later, change
this relationship to M:N and introduce an assignment relation.

**Business rule:** an assigned user must be a member of the team
belonging to the task's project.

------------------------------------------------------------------------

## 8. Relationship summary

  -----------------------------------------------------------------------------------
  Entity 1           Relationship   Entity 2       Cardinality    Relationship
                                                                  attributes
  ------------------ -------------- -------------- -------------- -------------------
  USER               HAS            SKILL          M:N            Proficiency_Level

  USER               CREATES        PROJECT        1:N            ---

  PROJECT            REQUIRES       SKILL          M:N            Required_Level,
                                                                  Required_Count,
                                                                  Required_Role

  USER               SUBMITS        APPLICATION    1:N            ---

  PROJECT            RECEIVES       APPLICATION    1:N            ---

  USER               REVIEWS        APPLICATION    1:N            Decision_Date, if
  (Owner/Reviewer)                                                modelled here

  PROJECT            HAS            TEAM           1:1            ---

  USER               JOINS / IS     TEAM           M:N            Role, Join_Date
                     MEMBER OF                                    

  PROJECT            CONTAINS       TASK           1:N            ---

  USER               IS ASSIGNED    TASK           1:N            ---
  -----------------------------------------------------------------------------------

------------------------------------------------------------------------

## 9. Application lifecycle and main workflows

### 9.1 User registration and profile setup

1.  A person registers.
2.  The system creates a `USER` record.
3.  The user adds skills.
4.  For each user-skill association, the user provides a proficiency
    level.
5.  The profile becomes available for project discovery and matching.

### 9.2 Project creation

1.  A user creates a project.
2.  The system records the user as its owner.
3.  The owner enters the title, description, domain, creation date,
    deadline, and initial status.
4.  The owner specifies required skills.
5.  Each project-skill association records the required level, role, and
    number of people where applicable.
6.  The project is made discoverable when its status is `Open`.

### 9.3 Project discovery

Users can browse and filter projects using:

-   Project domain
-   Required skills
-   Project status
-   Deadline
-   Other useful filters supported by the application

A project details page should display its description, owner, required
skills, required roles, and application status where relevant.

### 9.4 Applying to a project

1.  A user opens a project.
2.  The user submits an application with a message.
3.  The system records the applicant, project, submission date, and
    `Pending` status.
4.  The application becomes visible to the project owner.

### 9.5 Reviewing an application

1.  The project owner opens the project's application list.
2.  The owner reviews each application.
3.  The owner accepts or rejects it.
4.  The application status and decision time are updated.
5.  If accepted, the system adds the applicant to the project's team.

**Atomicity requirement:** accepting an application and adding the
applicant to the team should happen in one database transaction. If team
membership cannot be created, the application acceptance should be
rolled back.

### 9.6 Team formation

1.  The project has one primary team under the current design.
2.  The team is created when the project begins forming a working group,
    or at another clearly defined point in the workflow.
3.  Accepted applicants are added as team members.
4.  Each membership records the member's role and join date.

The project owner may also be included as a team member if the product
rules require owners to participate in the team. This needs to be
decided explicitly; ownership does not automatically imply membership
unless the application enforces it.

### 9.7 Task management

1.  The owner or an authorized team member creates tasks.
2.  Each task is associated with the project.
3.  A responsible team member is assigned.
4.  The assignee updates the task status as work progresses.
5.  The project dashboard aggregates task progress.

------------------------------------------------------------------------

## 10. Skill-based matching

Skill-based matching is the main differentiating feature of TeamTREE.

The system compares:

-   Skills a project requires
-   Proficiency levels required
-   Roles and number of people needed
-   Skills a user possesses
-   The user's proficiency in those skills

Example:

**Project requirements**

  Skill    Required level     People needed
  -------- ---------------- ---------------
  Python   Advanced                       1
  SQL      Intermediate                   1
  React    Intermediate                   1

**Candidate profile**

  Skill    User proficiency
  -------- ------------------
  Python   Advanced
  SQL      Advanced
  React    Beginner

The system can calculate a match score and show why the candidate is or
is not a strong match.

Possible matching factors:

  Factor                      Illustrative weight
  ------------------------- ---------------------
  Required-skill coverage                     50%
  Proficiency match                           20%
  Relevant experience                         15%
  Domain/interests                            10%
  Availability                                 5%

These weights are only a starting proposal. The team should define a
transparent scoring method, handle missing data, and avoid presenting a
score as an objective guarantee of suitability.

This feature can be implemented with SQL joins, conditional expressions,
aggregations, and application-side scoring. **Machine learning is not
required.**

### 10.1 Skill gap analysis

The system can compare the skills required by a project with the skills
represented in its current team.

Example:

  Required skill   Present in team?
  ---------------- ------------------
  Python           Yes
  SQL              Yes
  Docker           No

The dashboard can report:

**Missing skill: Docker**

This helps owners identify what kind of collaborator they still need.

The analysis should distinguish between: - A skill required by the
project - A skill possessed by at least one current member - The number
of members with that skill - Whether their proficiency meets the
required level

A simple yes/no check is useful for a demo, but a count and
proficiency-aware check is more informative.

------------------------------------------------------------------------

## 11. Analytics and reporting

The analytics module should derive its results from stored database
records rather than manually maintained totals.

### 11.1 Skill analytics

Possible questions:

-   Which skills are most commonly possessed by users?
-   Which skills are most frequently required by projects?
-   Which skills have high demand relative to their supply?
-   Which skill combinations occur frequently?
-   Which categories have the most activity?

Example report:

  Skill      Projects requiring it   Users possessing it
  -------- ----------------------- ---------------------
  Python                        42                    81
  SQL                           37                    65
  React                         29                    41
  Docker                        24                    18

This could highlight Docker as a skill with comparatively high demand
and lower supply. The example values are illustrative, not actual
platform data.

### 11.2 Project analytics

-   Number of open, ongoing, completed, and closed projects
-   Projects by domain
-   Applications received per project
-   Average applications per project
-   Average time to receive an application
-   Average project duration
-   Number of projects approaching deadlines

### 11.3 User analytics

-   Most active users
-   Projects created per user
-   Applications submitted per user
-   Applications accepted per user
-   Number of teams joined
-   Tasks completed
-   Skills represented on profiles

Be careful with rankings: a user who creates many projects is not
necessarily a better collaborator. Label each metric clearly.

### 11.4 Team analytics

-   Average team size
-   Largest teams
-   Distribution of team roles
-   Task completion by project/team
-   Number of outstanding tasks
-   Team skill coverage

### 11.5 Application analytics

-   Pending, accepted, rejected, and withdrawn application counts
-   Application acceptance rate
-   Projects receiving the most applications
-   Average decision time
-   Projects with no applications

Define the denominator for rates clearly. For example, an acceptance
rate might be accepted applications divided by all decided applications,
excluding pending and withdrawn applications.

------------------------------------------------------------------------

## 12. Business rules and integrity constraints

These rules should be enforced through database constraints,
transactions, backend validation, or a combination of these.

### 12.1 User rules

1.  Every user has a unique `User_ID`.
2.  Email addresses must be unique.
3.  Passwords must be stored as secure hashes, not plaintext.
4.  A user may have multiple skills.
5.  A user's proficiency is recorded for each user-skill association.
6.  A user may participate in multiple projects/teams.

### 12.2 Skill rules

7.  Each skill has a unique identifier.
8.  Skill names should be unique after case/whitespace normalization,
    where appropriate.
9.  The same user should not have duplicate associations with the same
    skill.

### 12.3 Project rules

10. Every project has exactly one owner.
11. A user may create multiple projects.
12. A project may require multiple skills.
13. A project has one primary team under the current scope.
14. A project can receive multiple applications.
15. A project deadline should not precede its creation date.
16. Only open projects accept new applications.

### 12.4 Application rules

17. Every application has exactly one applicant and one target project.
18. An application begins with `Pending` status.
19. A user cannot apply to their own project.
20. A user should not have duplicate active applications to the same
    project.
21. Only the owner of the target project can accept or reject its
    applications.
22. An accepted application should result in team membership.
23. A rejected application must not create team membership.
24. A withdrawn application must not be treated as accepted.
25. Applications cannot be submitted to projects that are closed or
    completed.

**Duplicate application policy:** a useful initial rule is to allow at
most one active application per user-project pair. If an application is
rejected or withdrawn, decide whether the user may reapply. If
reapplication is allowed, retain application history and enforce
uniqueness only for active statuses rather than imposing a permanent
unique constraint on `(User_ID, Project_ID)`.

### 12.5 Team rules

26. Each team belongs to exactly one project.
27. A user cannot be added to the same team more than once.
28. A user may join different teams for different projects.
29. Membership has a role and join date.
30. A user should only become a member through an authorized process,
    such as acceptance by the project owner.
31. The project owner may or may not be a team member; choose and
    document one policy.

### 12.6 Task rules

32. Every task belongs to exactly one project.
33. Every assigned task has one responsible user in the initial design.
34. The assigned user must be a member of the team for that task's
    project.
35. Task due dates should normally not exceed the project deadline.
36. Task status must be one of the permitted values.
37. Removing a team member requires handling their incomplete tasks.

------------------------------------------------------------------------

## 13. Exceptions and edge cases

A robust design should explain what happens when the normal workflow
cannot proceed.

### 13.1 User applies to their own project

Disallow this. The owner is already responsible for the project and
should not apply to join it as an applicant.

### 13.2 Duplicate application

Prevent multiple simultaneous active applications from the same user to
the same project. Decide whether reapplication is allowed after
rejection or withdrawal. Preserve historical applications if
reapplication is supported.

### 13.3 Project reaches capacity

If a project needs a fixed number of members and that capacity is
reached: - Stop accepting further applications, or - Allow the owner to
increase capacity, or - Keep a waitlist if that feature is deliberately
implemented.

For the first version, stop accepting applications when the configured
capacity is reached. If capacity is not modelled, do not claim that the
system automatically knows when a project is full.

### 13.4 No suitable candidates for a required skill

Do not silently lower the requirement. Display a skill gap and allow the
owner to: - Keep the requirement unchanged - Edit the required
proficiency - Increase the search scope - Remove or replace the
requirement

Any change to requirements should be reflected in matching results.

### 13.5 User withdraws an application

Change its status to `Withdrawn`. It should not create team membership.
Define whether a user can submit a new application afterward.

### 13.6 Owner rejects an application

Set the application to `Rejected`. Do not create team membership. Retain
the record for history and analytics.

### 13.7 Owner accepts an application but membership creation fails

Perform the status update and membership insertion in one transaction.
If either operation fails, roll back both.

### 13.8 Team member leaves

Do not necessarily delete the membership record. Mark it as inactive or
record a leave date so historical membership and contribution data are
preserved. This requires adding a membership status or `Leave_Date`
attribute to the membership relationship/table.

### 13.9 Team member is removed

Only an authorized owner/administrator should remove a member. Before or
during removal, reassign that person's incomplete tasks or leave them
explicitly unassigned for the owner to reassign. Preserve the membership
history.

### 13.10 Owner leaves or becomes unavailable

A project should not be left without an owner. Support ownership
transfer to another eligible user, or allow the project to be closed.
Ownership transfer should be recorded and authorized.

### 13.11 Project deadline passes

Do not assume that a project is completed just because its deadline
passed. It may be overdue. A more accurate status model can distinguish
`Open`, `Ongoing`, `Completed`, `Closed`, and an overdue condition
derived from deadline and status.

### 13.12 Project is deleted

Prefer soft deletion or a `Closed`/archived state once applications,
team memberships, or tasks exist. Hard deletion can destroy useful
history and may conflict with foreign-key references.

### 13.13 User account is deleted

Consider deactivation or anonymization rather than cascading deletion of
all historical projects, applications, reviews, and tasks. The exact
policy should account for privacy and audit requirements.

### 13.14 Task is assigned to a non-member

Reject the assignment. The assigned user must belong to the team
associated with the task's project.

### 13.15 Multiple assignees are requested

The current model supports one responsible user per task. If the product
needs multiple assignees, change `USER — ASSIGNED_TO — TASK` from 1:N to
M:N and represent assignments with a separate relation.

### 13.16 Project needs multiple teams

The current design assumes one primary team per project. If multiple
teams are needed, change `PROJECT — HAS — TEAM` from 1:1 to 1:N and
revisit task ownership and membership rules.

------------------------------------------------------------------------

## 14. Relational schema conversion

The conceptual ER model and relational schema are related but not
identical.

In the conceptual Chen ER diagram, `USER`, `SKILL`, `PROJECT`,
`APPLICATION`, `TEAM`, and `TASK` are the six main entities.
Relationships can have attributes.

When mapping to relational tables:

-   A 1:N relationship is generally implemented by placing the primary
    key from the 1-side as a foreign key on the N-side.
-   An M:N relationship is generally implemented as a separate junction
    relation containing foreign keys to both participating entities.
-   The foreign keys in a junction relation commonly form a composite
    primary key, provided one association per pair is allowed.
-   A 1:1 relationship can be implemented using a foreign key with a
    `UNIQUE` constraint, usually on the side with total participation or
    where it best fits the lifecycle.
-   A relationship with its own identifier or history requirements may
    need a surrogate primary key instead of only a composite key.

### 14.1 Illustrative relational mapping

The following is a starting point, not a final SQL DDL script.

``` text
USER(
    User_ID PK,
    Name,
    Email UNIQUE,
    Password_Hash,
    Bio,
    DOB,
    Location,
    Availability,
    Experience_Level
)

SKILL(
    Skill_ID PK,
    Skill_Name UNIQUE,
    Category
)

PROJECT(
    Project_ID PK,
    Owner_ID FK -> USER.User_ID,
    Project_Name,
    Description,
    Domain,
    Creation_Date,
    Deadline,
    Status
)

APPLICATION(
    Application_ID PK,
    Applicant_ID FK -> USER.User_ID,
    Project_ID FK -> PROJECT.Project_ID,
    Application_Date,
    Message,
    Status,
    Decision_Date
)

TEAM(
    Team_ID PK,
    Project_ID FK -> PROJECT.Project_ID UNIQUE,
    Team_Name,
    Creation_Date
)

TASK(
    Task_ID PK,
    Project_ID FK -> PROJECT.Project_ID,
    Assigned_User_ID FK -> USER.User_ID,
    Task_Name,
    Description,
    Priority,
    Status,
    Due_Date
)
```

The M:N relationships become junction relations:

``` text
USER_SKILL(
    User_ID PK/FK -> USER.User_ID,
    Skill_ID PK/FK -> SKILL.Skill_ID,
    Proficiency_Level
)

PROJECT_SKILL(
    Project_ID PK/FK -> PROJECT.Project_ID,
    Skill_ID PK/FK -> SKILL.Skill_ID,
    Required_Level,
    Required_Count,
    Required_Role
)

TEAM_MEMBER(
    Team_ID PK/FK -> TEAM.Team_ID,
    User_ID PK/FK -> USER.User_ID,
    Role,
    Join_Date
)
```

In `USER_SKILL`, `(User_ID, Skill_ID)` is the composite primary key if a
user can have only one current proficiency record per skill.

In `PROJECT_SKILL`, `(Project_ID, Skill_ID)` is the composite primary
key if a project can have only one requirement entry per skill. If a
project needs the same skill for multiple distinct roles, include a role
identifier in the key or model project-role requirements more
explicitly.

In `TEAM_MEMBER`, `(Team_ID, User_ID)` is the composite primary key if a
user can join a given team only once. If membership history must
preserve multiple join/leave periods, use a separate membership
identifier and appropriate uniqueness rules for active membership.

### 14.2 Application reviewer mapping

The conceptual ER diagram may show:

-   `USER (Applicant) — SUBMITS — APPLICATION`
-   `USER (Project Owner/Reviewer) — REVIEWS — APPLICATION`

In the basic relational schema, the reviewer is derived by joining:

`APPLICATION.Project_ID → PROJECT.Project_ID → PROJECT.Owner_ID`

Therefore, a separate `Reviewer_ID` in `APPLICATION` is not required.

`Decision_Date` can be stored as an attribute of `APPLICATION` or
treated as an attribute of the review/decision relationship in the
conceptual model. If the system needs a full decision audit trail,
create a separate decision-history relation in a later version.

### 14.3 Composite primary-key principle

For an M:N relationship such as `USER — HAS — SKILL`, the junction
relation stores both participating primary keys:

``` text
USER_SKILL(User_ID, Skill_ID, Proficiency_Level)
```

-   `User_ID` is a foreign key to `USER`.
-   `Skill_ID` is a foreign key to `SKILL`.
-   `(User_ID, Skill_ID)` is normally the composite primary key.

The combination is unique even though each individual foreign key can
repeat many times.

This rule should not be applied blindly to every relationship. For a 1:N
relationship such as `USER — CREATES — PROJECT`, the usual mapping is to
put `Owner_ID` as a foreign key in `PROJECT`, not to create a separate
`CREATES` table.

------------------------------------------------------------------------

## 15. Normalization considerations

Aim for a schema that satisfies at least Third Normal Form (3NF),
subject to the final functional dependencies.

Examples:

-   Do not store a comma-separated list of skills in `USER`.
-   Do not store a comma-separated list of required skills in `PROJECT`.
-   Store each skill once in `SKILL`.
-   Store proficiency on the user-skill association.
-   Store required proficiency/count/role on the project-skill
    association.
-   Store team role on team membership, not as a permanent user
    attribute.
-   Store application status with the application.
-   Avoid storing derived values such as age when they can be calculated
    from DOB.

Normalization reduces duplication and update anomalies, while the
junction relations make M:N relationships queryable.

------------------------------------------------------------------------

## 16. Transactions and consistency

Several workflows require multiple database operations to succeed or
fail together.

### 16.1 Accept application

A transaction should:

1.  Verify that the logged-in user owns the target project.
2.  Verify that the project is still open and has capacity, if capacity
    is enforced.
3.  Verify that the application is pending.
4.  Update the application status to `Accepted` and record the decision
    time.
5.  Insert the applicant into the project's team.
6.  Commit only if all operations succeed.

If any step fails, roll back the transaction.

### 16.2 Reject application

1.  Verify project ownership.
2.  Verify the application is pending.
3.  Update status to `Rejected`.
4.  Record decision time.
5.  Commit.

No team membership should be created.

### 16.3 Assign task

1.  Verify the task belongs to the project.
2.  Verify the assigned user is an active member of that project's team.
3.  Update the assignment.
4.  Commit.

### 16.4 Transfer project ownership

1.  Verify the current owner is authorized.
2.  Verify the new owner is eligible.
3.  Update the project owner.
4.  Record the transfer if audit history is required.
5.  Commit.

------------------------------------------------------------------------

## 17. Constraints, triggers, procedures, views, and indexes

These features should be selected to demonstrate DBMS concepts
meaningfully rather than added only for their names.

### 17.1 Constraints

Useful constraints include:

-   Primary keys on all entity tables.
-   Foreign keys for references.
-   Unique email address.
-   Unique skill name, where appropriate.
-   Unique `(User_ID, Skill_ID)` in `USER_SKILL`.
-   Unique `(Project_ID, Skill_ID)` in `PROJECT_SKILL`, subject to the
    role modelling decision.
-   Unique `(Team_ID, User_ID)` for current team membership.
-   Unique `TEAM.Project_ID` to enforce one team per project.
-   Check constraints for valid status, priority, proficiency, and
    rating ranges.
-   Date checks such as deadline not preceding creation date.

Some business rules, such as "only the project owner may accept an
application" and "the task assignee must be a member of the
corresponding project team," require transactional backend logic,
triggers, or carefully designed database procedures. A simple foreign
key alone does not enforce them.

### 17.2 Triggers

Possible trigger use cases:

-   Reject an application if its project is not open.
-   Prevent duplicate active membership.
-   Validate task assignment against project-team membership.
-   Record changes to important project/application fields in an audit
    table.
-   Maintain derived counters only if necessary.

Do not use a trigger where a normal constraint or transaction is
clearer. Be careful about triggers that silently change several records,
because they can make application behaviour difficult to understand.

### 17.3 Stored procedures

Potential procedures:

-   `CreateProject`
-   `ApplyToProject`
-   `AcceptApplication`
-   `RejectApplication`
-   `AssignTask`
-   `TransferProjectOwnership`

`AcceptApplication` is a particularly useful procedure because it can
validate ownership, update application status, and add team membership
atomically.

### 17.4 Views

Potential views:

-   `OpenProjects`
-   `ProjectApplicationSummary`
-   `UserSkillProfiles`
-   `ProjectSkillRequirements`
-   `TeamMemberDetails`
-   `TaskProgressSummary`
-   `TopInDemandSkills`

### 17.5 Indexes

Potential indexes:

-   `USER.Email`
-   `USER.Name`
-   `SKILL.Skill_Name`
-   `PROJECT.Status`
-   `PROJECT.Domain`
-   `APPLICATION.Project_ID`
-   `APPLICATION.Status`
-   `TASK.Project_ID`
-   `TASK.Assigned_User_ID`

Indexes should be selected based on actual search and join patterns.
Primary-key and unique constraints commonly create indexes
automatically, depending on the DBMS.

------------------------------------------------------------------------

## 18. CRUD functionality

  -------------------------------------------------------------------------------------------------
  Entity         Create         Read                  Update                 Delete / lifecycle
                                                                             action
  -------------- -------------- --------------------- ---------------------- ----------------------
  USER           Register       View profile          Edit profile           Deactivate/anonymize
                                                                             account

  SKILL          Add skill      Browse skills         Edit category/name     Retire skill if
                 (admin or                                                   referenced
                 controlled                                                  
                 workflow)                                                   

  PROJECT        Create project Browse/view projects  Edit                   Close/archive project
                                                      details/requirements   

  APPLICATION    Apply          View                  Update status or       Retain history; avoid
                                applicant's/owner's   withdraw               unnecessary hard
                                applications                                 deletion

  TEAM           Form team      View team             Edit team details      Disband/archive team

  TASK           Create task    View project tasks    Update                 Delete only when
                                                      status/assignment      appropriate; otherwise
                                                                             archive
  -------------------------------------------------------------------------------------------------

A skill catalogue may be managed by an administrator or by a controlled
user-submission process. Avoid allowing arbitrary duplicate skill names.

------------------------------------------------------------------------

## 19. Suggested application pages

### Public pages

-   Landing page
-   Browse projects
-   Project details
-   Registration
-   Login

### User dashboard

-   Profile
-   My skills
-   My projects
-   My applications
-   My teams
-   My tasks

### Project owner dashboard

-   Project overview
-   Skill requirements
-   Applications received
-   Application review actions
-   Team management
-   Task management
-   Project analytics

### Analytics dashboard

-   Skill demand and supply
-   Project status distribution
-   Application statistics
-   User activity
-   Team size and task progress
-   Skill gaps

------------------------------------------------------------------------

## 20. Suggested technology direction

The project is intended to be a relational DBMS application. A
reasonable implementation could use:

-   **Database:** MySQL or PostgreSQL
-   **Backend:** Python with Flask/FastAPI, or another familiar backend
    framework
-   **Frontend:** React, or a simpler HTML/CSS/JavaScript frontend if
    time is limited
-   **Charts:** a frontend charting library for analytics

The exact stack is a team decision. Choose tools the team can explain
and debug. The database design, constraints, transactions, and SQL
analysis should remain the centre of the academic demonstration.

------------------------------------------------------------------------

## 21. Testing plan

Test both normal flows and exceptions.

### User and skill tests

-   Register with a new email.
-   Attempt registration with a duplicate email.
-   Add multiple skills.
-   Attempt to add the same skill twice.
-   Update proficiency.

### Project tests

-   Create a project.
-   Add multiple skill requirements.
-   Attempt to set a deadline before the creation date.
-   Close a project and verify that new applications are blocked.

### Application tests

-   Submit a valid application.
-   Attempt to apply to one's own project.
-   Attempt a duplicate active application.
-   Attempt to apply to a closed project.
-   Accept an application as the owner.
-   Attempt to accept it as a different user.
-   Reject an application and verify that no team membership is created.
-   Withdraw an application.

### Team tests

-   Verify accepted users become members.
-   Attempt duplicate membership.
-   Verify the one-team-per-project rule.
-   Verify membership roles and dates.

### Task tests

-   Create a task.
-   Assign it to a project team member.
-   Attempt to assign it to a non-member.
-   Update task status.
-   Remove a member and verify that their incomplete tasks are handled.

### Analytics tests

-   Check that counts and rates match known test data.
-   Verify that pending applications are excluded from
    decided-application acceptance-rate denominators.
-   Verify skill demand and supply counts.
-   Verify that a skill gap is reported when no team member satisfies a
    requirement.

------------------------------------------------------------------------

## 22. Important design decisions still to finalize

These decisions should be agreed upon before writing the final SQL
schema.

  ------------------------------------------------------------------------
  Decision                Current proposal        Why it matters
  ----------------------- ----------------------- ------------------------
  Database                SQL relational database Supports relationships,
                                                  constraints,
                                                  transactions, and
                                                  analytics

  Main entities           USER, SKILL, PROJECT,   Keeps the conceptual
                          APPLICATION, TEAM, TASK model focused

  Teams per project       One primary team        Makes PROJECT--TEAM 1:1

  Assignees per task      One responsible user    Keeps USER--TASK 1:N

  Application review      Project owner reviews   Reviewer is the owner of
                                                  the target project

  Reviewer storage        Derive reviewer through Avoids redundant
                          PROJECT owner           reviewer data in
                                                  APPLICATION

  Application history     Preserve records and    Supports audit and
                          statuses                analytics

  Reapplication           Allow only after a      Requires a precise
                          previous active         uniqueness rule
                          application ends, if    
                          desired                 

  Owner membership        Decide whether owner is Affects team size and
                          automatically a team    task eligibility
                          member                  

  Team member departure   Preserve membership     Requires membership
                          history                 status or leave date

  Project capacity        Decide whether to store Needed to enforce a
                          a maximum team size     full-project rule

  Skill catalogue         Admin-managed or        Avoids
                          controlled user         duplicate/inconsistent
                          submissions             skills

  Matching                Transparent weighted    Avoids unnecessary ML
                          SQL/application logic   complexity

  Reviews/bookmarks       Optional later features Would expand the model
                                                  beyond six core entities
  ------------------------------------------------------------------------

------------------------------------------------------------------------

## 23. Recommended implementation order

1.  Finalize the six-entity conceptual ER diagram and relationship
    cardinalities.
2.  Confirm participation constraints and the outstanding decisions in
    Section 22.
3.  Convert the ER model into relational tables.
4.  Identify primary keys, foreign keys, candidate keys, and composite
    keys.
5.  Normalize the schema and document functional dependencies.
6.  Create tables and constraints in the selected SQL DBMS.
7.  Implement registration, profiles, and skills.
8.  Implement project creation and skill requirements.
9.  Implement project discovery and matching queries.
10. Implement applications and owner decisions using transactions.
11. Implement team membership.
12. Implement tasks and assignment validation.
13. Build CRUD screens and dashboards.
14. Add views, selected triggers/procedures, and indexes.
15. Add analytics and test all exception cases.

------------------------------------------------------------------------

## 24. Final project definition

**TeamTREE is a skill-based project team formation and collaboration
platform that enables users to create projects, specify required skills,
discover and recruit suitable collaborators, form teams, manage project
tasks, and analyse project, skill, application, and team activity
through a centralized relational database.**

The defining idea is the connection between **USER skills** and
**PROJECT skill requirements**. Applications provide the recruitment
workflow, teams represent accepted collaboration, and tasks provide a
lightweight way to track the work that follows.

The database should not merely store these records. It should enforce
the rules that connect them and support useful decisions through SQL
queries and analytics.
