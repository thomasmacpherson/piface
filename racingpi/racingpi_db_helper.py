#!/usr/bin/env python
"""
racingpi_db_helper.py
A database wrapper for the RacingPi question database

TODO
Make it so that connections can be passed in for quicker database access
"""
import sqlite3


VERBOSE_MODE = True
DATABASE_NAME = "racingpi_db"


class Question(object):
	def __init__(self, question_text, correct_answer, incorrect_answer,
			difficulty, category):
		self.text = question_text
		self.correct_answer = correct_answer
		self.incorrect_answer = incorrect_answer
		self.difficulty = difficulty
		self.category = category

	def write_to_db(self):
		"""Writes the question to the database"""
		connection = get_connection()
		cursor = connection.cursor()
		self.category.write_to_db()
		sql = """
			INSERT INTO question
				(question_text, correct_answer, incorrect_answer, difficulty,
				category_id)
			VALUES (?,?,?,?,?)
		"""

		cursor.execute(sql, (
			self.text,
			self.correct_answer,
			self.incorrect_answer,
			self.difficulty,
			self.category.category_id)
		)

		self.question_id = cursor.lastrowid

		commit_connection(connection)

class Category(object):
	def __init__(self, name):
		self.cetegory_id = None
		self.name = name

	def write_to_db(self):
		"""Writes the category to the database"""
		connection = get_connection()
		cursor = connection.cursor()

		# check the category doesn't already exist
		sql = "SELECT id FROM category WHERE name=? LIMIT 1"
		cursor.execute(sql, (self.name,))
		print cursor.fetchone()[0]

		# if it doesnt then insert the category
		if count < 1:
			sql = "INSERT INTO category (name) VALUES (?)"
			cursor.execute(sql, (self.name,))
			self.category_id = cursor.lastrowid
			commit_connection(connection)


def get_connection():
	"""Returns a databse connection"""
	return sqlite3.connect(DATABASE_NAME)

def commit_connection(connection):
	"""Saves all changes to the database"""
	connection.commit()

def init_db():
	"""Initialises the RacingPi database"""
	connection = get_connection()
	cursor = connection.cursor()

	sql = """CREATE TABLE IF NOT EXISTS category (
		id integer,
		name text,
		PRIMARY KEY (id)
	)"""
	cursor.execute(sql)

	sql = """CREATE TABLE IF NOT EXISTS question (
		id integer,
		question_text text,
		correct_answer text,
		incorrect_answer text,
		difficulty integer,
		category_id integer,
		deleted integer DEFAULT 0,
		PRIMARY KEY (id)
		FOREIGN KEY (category_id) REFERENCES category(id)
	)"""
	cursor.execute(sql)

	commit_connection(connection)

def add_question(question=None):
	"""Adds a question to the database"""
	if question:
		question.write_to_db()
	else:
		question_text = raw_input("Question: ")
		correct_answer = raw_input("Correct answer: ")
		incorrect_answer = raw_input("Incorrect answer: ")
		difficulty = raw_input("Difficulty (number): ")
		category_name = raw_input("Category: ")

		question = Question(
				question_text,
				correct_answer,
				incorrect_answer,
				difficulty,
				Category(category_name))
		question.write_to_db()

def delete_question(question_id):
	"""Sets the delete flag high on a question"""
	connection = get_connection()
	cursor = connection.cursor()
	sql = """
		UPDATE question
		   SET deleted = 1
		 WHERE id = ?
	"""
	cursor.execute(sql, (question_id,))
	commit_connection(connection)

def get_question(question_id):
	"""Return a single question"""
	connection = get_connection()
	cursor = connection.cursor()
	sql = """
		SELECT question_text, correct_answer, incorrect_answer,
			   difficulty, category_id
		  FROM question
		 WHERE id = ?
		   AND deleted = 0
		 LIMIT 1
	"""
	cursor.execute(sql, (question_id,))
	row = cursor.fetchone()
	print row

def get_all_questions(category=None):
	pass

def get_all_categories():
	pass
