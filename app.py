from flask import Flask, render_template, request, jsonify
from datetime import datetime
import sqlite3
import json
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente para outras configurações se necessário
load_dotenv()

app = Flask(__name__)

# Configuração do banco de dados
DATABASE = 'kanban.db'

def init_db():
    """Inicializa o banco de dados com a tabela de tarefas"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            responsavel TEXT NOT NULL,
            cliente TEXT NOT NULL,
            descricao TEXT NOT NULL,
            data_entrega DATETIME NOT NULL,
            status TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    """Retorna uma conexão com o banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
    return conn

def dict_factory(cursor, row):
    """Converte as linhas do SQLite para dicionários"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/')
def index():
    """Rota principal que renderiza o template HTML"""
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Obtém todas as tarefas do banco de dados"""
    try:
        conn = get_db()
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
        tasks = cursor.fetchall()
        
        return jsonify(tasks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Cria uma nova tarefa"""
    try:
        task_data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (responsavel, cliente, descricao, data_entrega, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            task_data['responsavel'],
            task_data['cliente'],
            task_data['descricao'],
            task_data['data_entrega'],
            'servicos'  # Status inicial
        ))
        
        conn.commit()
        task_id = cursor.lastrowid
        
        # Retorna a tarefa criada
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        created_task = dict_factory(cursor, cursor.fetchone())
        
        return jsonify(created_task), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Atualiza o status de uma tarefa"""
    try:
        update_data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tasks 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (update_data['status'], task_id))
        
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
            
        # Retorna a tarefa atualizada
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        updated_task = dict_factory(cursor, cursor.fetchone())
        
        return jsonify(updated_task)
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Deleta uma tarefa"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
            
        return jsonify({'message': 'Tarefa deletada com sucesso'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.errorhandler(404)
def not_found(error):
    """Manipulador para erros 404"""
    return jsonify({'error': 'Recurso não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Manipulador para erros 500"""
    return jsonify({'error': 'Erro interno do servidor'}), 500

# Inicializa o banco de dados antes de iniciar o aplicativo
init_db()

# Configuração para desenvolvimento
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)