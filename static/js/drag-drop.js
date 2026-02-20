/**
 * DRAG & DROP MINIMALISTE - GARANTI FONCTIONNEL
 */

console.log('🚀 CHARGEMENT DU DRAG & DROP MINIMALISTE');

// État global
let draggedElement = null;
let placeholder = null;

// Initialisation
function initMinimalDragDrop() {
    console.log('📋 Initialisation du drag & drop minimaliste');
    
    const taskCards = document.querySelectorAll('.task-card');
    console.log('📊 Tâches trouvées:', taskCards.length);
    
    if (taskCards.length === 0) {
        console.log('⚠️ Aucune tâche trouvée');
        return;
    }
    
    taskCards.forEach(card => {
        // Rendre la carte dragable
        card.draggable = true;
        card.style.cursor = 'grab';
        
        // Événements
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
        
        console.log('✅ Tâche configurée:', card.dataset.taskId);
    });
    
    // Configurer les colonnes
    const columns = document.querySelectorAll('.task-list');
    columns.forEach(column => {
        column.addEventListener('dragover', handleDragOver);
        column.addEventListener('drop', handleDrop);
        column.addEventListener('dragleave', handleDragLeave);
    });
    
    console.log('✅ Drag & drop minimaliste initialisé avec succès');
}

function handleDragStart(e) {
    console.log('🎯 Début du drag:', e.target.dataset.taskId);
    
    draggedElement = e.target;
    e.target.style.opacity = '0.5';
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', e.target.innerHTML);
    
    // Désactiver l'icône d'interdiction
    document.body.style.cursor = 'grabbing';
    document.body.style.userSelect = 'none';
    
    console.log('🚀 Drag commencé - icône d\'interdiction désactivée');
}

function handleDragEnd(e) {
    console.log('🏁 Fin du drag');
    
    if (draggedElement) {
        draggedElement.style.opacity = '1';
        draggedElement = null;
    }
    
    // Nettoyer tous les placeholders
    document.querySelectorAll('.drag-placeholder').forEach(p => p.remove());
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
}

function handleDragLeave(e) {
    // Nettoyer le placeholder si on quitte la colonne
    const placeholder = e.currentTarget.querySelector('.drag-placeholder');
    if (placeholder) {
        placeholder.remove();
    }
}

function handleDrop(e) {
    e.preventDefault();
    
    const targetList = e.currentTarget;
    console.log('📍 Drop dans la colonne:', targetList.id);
    
    if (!draggedElement) return;
    
    // Déterminer le nouveau statut selon la colonne cible
    let newStatus = 'a-faire'; // défaut
    if (targetList.id === 'kanbanTodoList') {
        newStatus = 'a-faire';
    } else if (targetList.id === 'kanbanProgressList') {
        newStatus = 'en-cours';
    } else if (targetList.id === 'kanbanReviewList') {
        newStatus = 'terminé';
    }
    
    console.log('📊 Nouveau statut à appliquer:', newStatus);
    
    // Créer un placeholder visuel
    if (!placeholder) {
        placeholder = document.createElement('div');
        placeholder.className = 'drag-placeholder';
        placeholder.innerHTML = '📋 Déposez la tâche ici';
        placeholder.style.cssText = `
            background: #f3f4f6;
            border: 2px dashed #3b82f6;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
            text-align: center;
            color: #3b82f6;
            font-weight: bold;
        `;
    }
    
    // Insérer le placeholder
    const rect = draggedElement.getBoundingClientRect();
    const afterElement = getDragAfterElement(targetList, e.clientY);
    
    if (afterElement == null) {
        targetList.appendChild(placeholder);
    } else {
        targetList.insertBefore(placeholder, afterElement);
    }
    
    // Animer l'insertion
    setTimeout(() => {
        if (placeholder && placeholder.parentNode) {
            // Remplacer le placeholder par la tâche
            placeholder.parentNode.replaceChild(draggedElement, placeholder);
            
            // Mettre à jour le statut IMMÉDIATEMENT
            updateTaskStatus(draggedElement.dataset.taskId, newStatus);
            
            // Mettre à jour les compteurs
            updateColumnCounters();
            
            console.log('✅ Tâche déplacée avec succès - Statut changé à:', newStatus);
            
            // Afficher un message de confirmation
            showStatusMessage(newStatus);
        }
    }, 100);
}

// Fonction pour afficher un message de statut
function showStatusMessage(status) {
    let message = '';
    let columnName = '';
    
    switch(status) {
        case 'a-faire':
            columnName = 'À faire';
            message = '📋 Tâche déplacée vers "À faire"';
            break;
        case 'en-cours':
            columnName = 'En cours';
            message = '⚡ Tâche déplacée vers "En cours"';
            break;
        case 'terminé':
            columnName = 'Réalisées';
            message = '✅ Tâche déplacée vers "Réalisées"';
            break;
        default:
            message = '📝 Tâche déplacée';
    }
    
    console.log('🎯', message);
    
    // Créer un message flash
    const flashDiv = document.createElement('div');
    flashDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #10b981;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 99999;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        animation: slideIn 0.3s ease;
    `;
    flashDiv.textContent = message;
    
    document.body.appendChild(flashDiv);
    
    // Auto-suppression après 3 secondes
    setTimeout(() => {
        if (flashDiv.parentNode) {
            flashDiv.remove();
        }
    }, 3000);
}

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.task-card:not(.dragging)')];
    
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return child;
        } else {
            return closest;
        }
    }, null);
}

function updateTaskStatus(taskId, newStatus) {
    console.log('🔄 Mise à jour du statut:', taskId, '->', newStatus);
    
    fetch('/api/update_task/' + taskId, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('✅ Statut mis à jour:', data.progress + '%');
        }
    })
    .catch(error => {
        console.error('❌ Erreur:', error);
    });
}

function updateColumnCounters() {
    document.querySelectorAll('.kanban-column').forEach(column => {
        const taskCount = column.querySelectorAll('.task-card').length;
        const counter = column.querySelector('.task-count');
        if (counter) {
            counter.textContent = taskCount;
        }
    });
}

// Auto-initialisation
document.addEventListener('DOMContentLoaded', () => {
    console.log('📱 DOM chargé');
    
    // Initialiser immédiatement
    initMinimalDragDrop();
    
    // Réinitialiser quand on change d'onglet
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('tab-btn') && e.target.getAttribute('data-tab') === 'tasks') {
            setTimeout(() => {
                initMinimalDragDrop();
            }, 300);
        }
    });
});

console.log('🎯 Drag & Drop Minimaliste chargé!');
