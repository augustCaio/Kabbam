// Modal
const modal = document.getElementById('taskModal');
const btn = document.getElementById('newTaskBtn');
const span = document.getElementsByClassName('close')[0];

btn.onclick = () => modal.style.display = 'block';
span.onclick = () => modal.style.display = 'none';
window.onclick = (event) => {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

// Form submission
const form = document.getElementById('taskForm');
form.onsubmit = async (e) => {
    e.preventDefault();
    
    const formData = new FormData(form);
    const data = {
        responsavel: formData.get('responsavel'),
        cliente: formData.get('cliente'),
        descricao: formData.get('descricao'),
        data_entrega: `${formData.get('data')}T${formData.get('hora')}`
    };
    
    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            modal.style.display = 'none';
            form.reset();
            loadTasks();
        }
    } catch (error) {
        console.error('Error:', error);
    }
};

// Load tasks
async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        const tasks = await response.json();
        
        document.getElementById('servicos').innerHTML = '';
        document.getElementById('servicos-iniciados').innerHTML = '';
        document.getElementById('servicos-finalizados').innerHTML = '';
        
        tasks.forEach(task => {
            const column = document.getElementById(task.status);
            const card = createTaskCard(task);
            column.appendChild(card);
        });
    } catch (error) {
        console.error('Error:', error);
    }
}

function createTaskCard(task) {
    const card = document.createElement('div');
    card.className = 'task-card';
    card.draggable = true;
    card.innerHTML = `
        <strong>${task.cliente}</strong>
        <p>Responsável: ${task.responsavel}</p>
        <p>${task.descricao}</p>
        <p>Entrega: ${new Date(task.data_entrega).toLocaleString()}</p>
    `;
    
    // Adicionar eventos de drag and drop
    card.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', task._id);
    });
    
    return card;
}

// Drag and Drop
document.querySelectorAll('.tasks').forEach(column => {
    column.addEventListener('dragover', (e) => {
        e.preventDefault();
    });
    
    column.addEventListener('drop', async (e) => {
        e.preventDefault();
        const taskId = e.dataTransfer.getData('text/plain');
        const newStatus = column.id;
        
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status: newStatus })
            });
            
            if (response.ok) {
                loadTasks();
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });
});

// Carregar tarefas inicialmente
loadTasks();