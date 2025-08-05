import datetime

from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth import get_user_model

from tracker.forms import RegisterForm, SkillForm, GoalForm
from tracker.models import Skill, LearningGoal
from tracker.signals import User

UserModel = get_user_model()

class TestTrackerUserModel(TestCase):
    def setUp(self):
        self.username = "TestUsername"
        self.user = UserModel.objects.create_user(
            username=self.username,
            email="test@test.com",
            password="12Test34"
        )

        self.skill = Skill.objects.create(
            name="TestSkillName",
            description="TestSkillDescription for testing purposes",
            category="TestSkillCategory",
            difficulty="TestDiff",
            owner=self.user
        )

    def test_valid_str_method_returns_username(self):
        self.assertEqual(self.username, str(self.user))

    def test_valid_str_method_returns_skill_name(self):
        self.assertEqual(self.skill.name, str(self.skill))

    def test_second_user_with_same_username(self):
        with self.assertRaises(IntegrityError) as ie:
            UserModel.objects.create_user(
                username=self.username,
                email="testNew@test.com",
                password="12Test345"
            )
        self.assertIn('duplicate key value violates unique constraint', str(ie.exception))


class TestRegisterForm(TestCase):
    def setUp(self):
        # Create and existing user to test duplicate email validation
        self.existing_user = UserModel.objects.create_user(
            username="TestUsernameOne",
            email="UserOne@test.com",
            password="SomePassword123"
        )

    def test_register_form_valid_data(self):
        # Form should be valid when all data is correct and email is unique.
        form_data = {
            "username": "NewUser",
            "email": "NewUser@test.com",
            "password1": "SomePassword123",
            "password2": "SomePassword123"
        }

        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.username, "NewUser")
        self.assertEqual(user.email, "NewUser@test.com")

    def test_register_form_duplicate_email(self):
        # Form should be invalid if email is already in use.
        form_data = {
            "username": "AnotherUser",
            "email": "UserOne@test.com",
            "password1": "testPassword123",
            "password2": "testPassword123"
        }

        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn("An account with this email already exists.", form.errors['email'])

    def test_register_form_password_mismatch(self):
        # Form should be invalid if there is a mismatch between passwords.
        form_data = {
            "username": "SecondUser",
            'email': "second_user@test.com",
            'password1': "testPassword123",
            'password2': "testPassword1234"
        }

        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

class TestSkillForm(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="TestUsername",
            email="User@test.com",
            password="SomePass123"
        )

    def test_skill_form_valid_data(self):
        # Form is expected to be valid with correct data
        form_data = {
            "name": "Test Skill Name",
            "description": "Test Skill Description",
            "category": "Test Skill Category",
            "difficulty": "Test Diff",
        }

        form = SkillForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

        skill = form.save(commit=False)  # commit is False as "owner" is excluded
        skill.owner = self.user
        skill.save()

        self.assertEqual(Skill.objects.count(), 1)
        self.assertEqual(skill.name, "Test Skill Name")
        self.assertEqual(skill.description, "Test Skill Description")
        self.assertEqual(skill.category, "Test Skill Category")
        self.assertEqual(skill.difficulty, "Test Diff")
        self.assertEqual(skill.owner, self.user)

    def test_skill_form_missing_required_fields(self):
        # Form should be invalid if some of the required fields are missing
        form = SkillForm(data={})  # no data provided
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('description', form.errors)
        self.assertIn('category', form.errors)
        self.assertIn('difficulty', form.errors)

    def test_owner_field_excluded(self):
        # The "owner" field should not be part of the form.
        form = SkillForm()
        self.assertNotIn('owner', form.fields)


class TestGoalForm(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="TestUsername",
            email="test@test.com",
            password="12Test34"
        )
    def test_goal_form_valid_data(self):
        # Create a skill
        skill = Skill.objects.create(
            name="Test Skill Name",
            description="Test Skill Description",
            category= "Test Goal Category",
            difficulty= 'Test Diff',
            owner=self.user
        )

        # Form should be valid with correct data
        form_data = {
            "name": "Test Goal",
            "description": "Test Goal Description",
            'target_date': datetime.date.today(),
            'progress': 0,
        }

        form = GoalForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

        goal = form.save(commit=False)
        goal.owner = self.user
        goal.skill = skill
        goal.save()

        self.assertEqual(LearningGoal.objects.count(), 1)
        self.assertEqual(goal.name, "Test Goal")
        self.assertEqual(goal.skill, skill)

    def test_goal_from_missing_required_fields(self):
        # Form is expected to be invalid when required fields are missing
        form = GoalForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('description', form.errors)
        self.assertIn('target_date', form.errors)
        self.assertIn('progress', form.errors)

    def test_goal_form_target_date_widget(self):
        # The target_date widget should be a date input
        form = GoalForm()
        widget = form.fields['target_date'].widget
        self.assertEqual(widget.input_type, 'date')