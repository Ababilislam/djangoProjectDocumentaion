from django.test import TestCase

import datetime
from django.utils import timezone
from .models import Question
from django.urls import reverse


# Create your tests here.
class QuestionModelTests(TestCase):
    def test_was_published_recently(self):
        """was published recently return false if it was in future"""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_args(self):
        """was_published_recently returns False for question whose pub_date us older than 1days."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """was published recently returns true for question whose published date with in last 24 hour"""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """create a question with given "question text"
    and published the given number of days offset to now
    negative for question published in the past, positive for question that have yet to published.
     """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """if no questions exist, and appropriate message is displayed."""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """question with a pub_date in the past are displayed on the index page."""
        question = create_question(question_text="past question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """question with a pub_date in the future aren't displayed on the index page."""
        create_question(question_text="future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "no polls are available.")
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [],
        )

    def test_future_question_and_past_question(self):
        """even if both past and future questions exists, only past question are displayed."""
        question = create_question(question_text="past question", days=-30)
        create_question(question_text="future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """the questions index page may display multiple questions."""
        question1 = create_question(question_text="past question_1.", days=-30)
        question2 = create_question(question_text="past question_2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        the detail view of a question with a pub_date in the future returns a 404 not found.
        :return:
        """
        future_question = create_question(question_text="future question", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        the detail view of a question with a pub date in the pas displays the questions text.
        :return:
        """
        past_question = create_question(question_text="past question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
