
SkillHub is a Django-based web application for setting and managing skills, as well as setting and managing learning goals.
The application allows tracking progress over time. 
The features include: user registration, profile management, an admin dashboard, and group-based permission handling in terms of admin manipulation.

List of features:
* User authentication and registration (with email validation)
* Skill management (create, view, edit, delete)
* Learning goals (create, view, edit, delete) that have target dates and progress tracking
* Track progress updates (max 100% total progress)
* Admin groups:
  ** SuperAdmin: full CRUD permissions
  ** StaffAdmin: limited permissions (no delete / user access)
* User profile with biography and avatar
* Role management from the Django admin panel


Links
http://localhost:8000/
http://localhost:8000/about/
http://localhost:8000/login/
http://localhost:8000/register/
http://localhost:8000/dashboard/
http://localhost:8000/skills/
http://localhost:8000/skill/add/
http://localhost:8000/skill/<int:pk>/
http://localhost:8000/skill/<int:pk>/edit/
http://localhost:8000/progress/add/?goal_id=<int:pk>
http://localhost:8000/skill/<int:pk>/delete/
http://localhost:8000/profile/
http://localhost:8000/goal/add/<int:pk>/
http://localhost:8000/goal/edit/<int:pk>/
http://localhost:8000/resources/add/?skill_id=<int:pk>
http://localhost:8000/profile/edit/
http://localhost:8000/goal/<int:pk>/delete/