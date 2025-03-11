from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from docx import Document
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'exports'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- МОДЕЛИ ---
class TestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)

    steps = db.relationship('Step', backref='test_case', cascade="all, delete-orphan")

class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_case.id'), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    expected_result = db.Column(db.String(500), nullable=False)

with app.app_context():
    db.create_all()

# --- ГЛАВНАЯ СТРАНИЦА ---
@app.route('/')
def index():
    return render_template('index.html')

# --- API: Получение всех тест-кейсов ---
@app.route('/testcases', methods=['GET'])
def get_test_cases():
    test_cases = TestCase.query.all()
    return jsonify([
        {
            "id": tc.id,
            "name": tc.name,
            "description": tc.description,
            "steps": [
                {"description": step.description, "expected_result": step.expected_result}
                for step in tc.steps
            ]
        }
        for tc in test_cases
    ])

# --- API: Создание тест-кейса + шагов ---
@app.route('/testcases', methods=['POST'])
def create_test_case():
    data = request.json  # Теперь принимаем JSON

    test_case = TestCase(name=data['name'], description=data['description'])
    db.session.add(test_case)
    db.session.commit()

    # Добавляем шаги, если они есть
    for step in data.get('steps', []):
        new_step = Step(test_case_id=test_case.id, description=step['description'], expected_result=step['expected_result'])
        db.session.add(new_step)

    db.session.commit()
    return jsonify({"message": "Test Case Created"}), 201

# --- API: Удаление тест-кейса + шагов ---
@app.route('/testcases/<int:test_case_id>', methods=['POST'])
def delete_test_case(test_case_id):
    test_case = TestCase.query.get_or_404(test_case_id)
    db.session.delete(test_case)
    db.session.commit()
    return jsonify({"message": "Test Case Deleted"}), 200

# --- API: Экспорт тест-кейса в Word ---
@app.route('/export/<int:test_case_id>', methods=['GET'])
def export_to_word(test_case_id):
    test_case = TestCase.query.get_or_404(test_case_id)
    steps = Step.query.filter_by(test_case_id=test_case.id).all()

    doc = Document()
    doc.add_heading(f" {test_case.name}", level=1)
    doc.add_paragraph(f"Описание: {test_case.description}")

    doc.add_paragraph(f"Предусловие: ...")  # Можно дополнить данными
    doc.add_paragraph(f"Постусловие: ...")  # Можно дополнить данными
    doc.add_paragraph(f"Комментарий: ...")  # Можно дополнить данными

    # --- Создаем таблицу ---
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"

    # Заголовки колонок
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Шаги"
    hdr_cells[1].text = "Ожидаемый результат"
    hdr_cells[2].text = "Полученный результат"

    # Заполняем таблицу шагами из БД
    for step in steps:
        row_cells = table.add_row().cells
        row_cells[0].text = step.description
        row_cells[1].text = step.expected_result
        row_cells[2].text = ""  # Пустой "Полученный результат"

    filename = f"{UPLOAD_FOLDER}/TestCase_{test_case_id}.docx"
    doc.save(filename)
    return send_from_directory(UPLOAD_FOLDER, f"TestCase_{test_case_id}.docx", as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
