"""
To-Do List - Backend Flask
Auteur : Grâce Destinée LEBIKI LAVANYA
Description : API REST avec 4 routes pour gérer les tâches
              Base de données SQLite intégrée
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

# ── INITIALISATION ──
app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'todo.db')

# ── BASE DE DONNÉES ──
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS taches (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            texte   TEXT    NOT NULL,
            faite   INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ════════════════════════════════════════
#   ROUTES DE L'API
# ════════════════════════════════════════

@app.route('/taches', methods=['GET'])
def get_taches():
    conn = get_db()
    taches = conn.execute('SELECT * FROM taches ORDER BY id DESC').fetchall()
    conn.close()
    resultat = [{'id': t['id'], 'texte': t['texte'], 'faite': bool(t['faite'])} for t in taches]
    return jsonify(resultat), 200


@app.route('/taches', methods=['POST'])
def add_tache():
    data = request.get_json()
    if not data or 'texte' not in data or data['texte'].strip() == '':
        return jsonify({'erreur': 'Le texte de la tâche est obligatoire'}), 400
    texte = data['texte'].strip()
    conn = get_db()
    cursor = conn.execute('INSERT INTO taches (texte) VALUES (?)', (texte,))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id, 'texte': texte, 'faite': False}), 201


@app.route('/taches/<int:id>', methods=['PATCH'])
def toggle_tache(id):
    conn = get_db()
    tache = conn.execute('SELECT * FROM taches WHERE id = ?', (id,)).fetchone()
    if not tache:
        conn.close()
        return jsonify({'erreur': 'Tâche introuvable'}), 404
    nouvel_etat = 0 if tache['faite'] else 1
    conn.execute('UPDATE taches SET faite = ? WHERE id = ?', (nouvel_etat, id))
    conn.commit()
    conn.close()
    return jsonify({'id': id, 'texte': tache['texte'], 'faite': bool(nouvel_etat)}), 200


@app.route('/taches/<int:id>', methods=['DELETE'])
def delete_tache(id):
    conn = get_db()
    tache = conn.execute('SELECT * FROM taches WHERE id = ?', (id,)).fetchone()
    if not tache:
        conn.close()
        return jsonify({'erreur': 'Tâche introuvable'}), 404
    conn.execute('DELETE FROM taches WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Tâche supprimée'}), 200


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'API To-Do List - Grâce Destinée LEBIKI LAVANYA',
        'routes': {
            'GET    /taches':         'Récupérer toutes les tâches',
            'POST   /taches':         'Ajouter une tâche',
            'PATCH  /taches/<id>':    'Cocher / décocher une tâche',
            'DELETE /taches/<id>':    'Supprimer une tâche'
        }
    }), 200


# ── LANCEMENT ──
init_db()  # Appelé au démarrage même avec gunicorn

if __name__ == '__main__':
    print("🚀 Serveur démarré sur http://localhost:5000")
    app.run(debug=True, port=5000)
