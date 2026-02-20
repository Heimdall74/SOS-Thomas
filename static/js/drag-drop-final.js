/**
 * DRAG & DROP FINAL - VERSION CORRIGÉE
 */

console.log('🚀 CHARGEMENT DU DRAG & DROP CORRIGÉ');

let draggedElement = null;
let isDragging = false;

function initMinimalDragDrop() {
    console.log('📋 Initialisation du drag & drop corrigé');
    
    const taskCards = document.querySelectorAll('.task-card');
    console.log('Tâches trouvées:', taskCards.length);
    
    if (taskCards.length === 0) {
        console.log('⚠️ Aucune tâche trouvée');
        return;
    }
    
    taskCards.forEach(card => {
        // Éviter les double initialisations
        if (card.hasAttribute('data-drag-initialized')) {
            return;
        }
        
        // Rendre la carte dragable
        card.draggable = true;
        card.style.cursor = 'grab';
        
        // Événements
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
        
        // Marquer comme initialisée
        card.setAttribute('data-drag-initialized', 'true');
        
        console.log('✅ Tâche configurée:', card.dataset.taskId);
    });
    
    // Configurer les colonnes
    const columns = document.querySelectorAll('.task-list');
    columns.forEach(column => {
        column.addEventListener('dragover', handleDragOver);
        column.addEventListener('drop', handleDrop);
        column.addEventListener('dragleave', handleDragLeave);
    });
    
    console.log('✅ Drag & drop corrigé initialisé');
}

function handleDragStart(e) {
    console.log('🎯 Début du drag:', e.target.dataset.taskId);
    
    draggedElement = e.target;
    isDragging = true;
    
    e.target.style.opacity = '0.5';
    e.target.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', e.target.innerHTML);
    
    // Désactiver l'icône d'interdiction
    e.dataTransfer.setDragImage(new Image(), 0, 0);
}

function handleDragEnd(e) {
    console.log('🏁 Fin du drag');
    
    if (draggedElement) {
        draggedElement.style.opacity = '1';
        draggedElement.classList.remove('dragging');
        draggedElement = null;
    }
    
    isDragging = false;
    
    // Nettoyer tous les placeholders et classes
    document.querySelectorAll('.drag-placeholder').forEach(p => p.remove());
    document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    
    // Ajouter la classe visuelle
    e.currentTarget.classList.add('drag-over');
    
    // Créer un placeholder si nécessaire
    const placeholder = e.currentTarget.querySelector('.drag-placeholder');
    if (!placeholder && draggedElement) {
        const dragPlaceholder = document.createElement('div');
        dragPlaceholder.className = 'drag-placeholder';
        dragPlaceholder.innerHTML = '📋 Déposez ici';
        e.currentTarget.appendChild(dragPlaceholder);
    }
}

function handleDragLeave(e) {
    // Retirer la classe visuelle
    e.currentTarget.classList.remove('drag-over');
    
    // Nettoyer le placeholder si on quitte la colonne
    const placeholder = e.currentTarget.querySelector('.drag-placeholder');
    if (placeholder) {
        placeholder.remove();
    }
}

function handleDrop(e) {
    e.preventDefault();
    
    const targetList = e.currentTarget;
    console.log('📍 Drop dans:', targetList.id);
    
    // Retirer la classe visuelle
    targetList.classList.remove('drag-over');
    
    if (!draggedElement) return;
    
    // Nettoyer le placeholder
    const placeholder = targetList.querySelector('.drag-placeholder');
    if (placeholder) {
        placeholder.remove();
    }
    
    // Déterminer le nouveau statut
    let newStatus = 'a-faire';
    if (targetList.id === 'kanbanProgressList') {
        newStatus = 'en-cours';
    } else if (targetList.id === 'kanbanReviewList') {
        newStatus = 'terminé';
    } else if (targetList.id === 'kanbanTodoList') {
        newStatus = 'a-faire';
    }
    
    console.log('📊 Nouveau statut:', newStatus);
    
    // Vérifier que l'élément n'est pas déjà dans cette colonne
    if (draggedElement.parentNode !== targetList) {
        // Ajouter la tâche à la nouvelle colonne
        targetList.appendChild(draggedElement);
        
        // Ajouter une animation de succès
        draggedElement.classList.add('success-animation');
        setTimeout(() => {
            draggedElement.classList.remove('success-animation');
        }, 600);
        
        // Mettre à jour le statut sur le serveur
        updateTaskStatus(draggedElement.dataset.taskId, newStatus);
        
        // Mettre à jour les compteurs
        updateColumnCounters();
        
        console.log('✅ Tâche déplacée avec succès');
    } else {
        console.log('ℹ️ Tâche déjà dans cette colonne');
    }
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
        } else {
            console.error('❌ Erreur:', data.error);
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
    
    // Observer les changements dans le DOM pour les nouvelles tâches
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                const newCards = [];
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.classList && node.classList.contains('task-card')) {
                        newCards.push(node);
                    }
                    // Vérifier aussi les enfants des nouveaux nœuds
                    if (node.nodeType === 1 && node.querySelectorAll) {
                        const cards = node.querySelectorAll('.task-card');
                        cards.forEach(card => newCards.push(card));
                    }
                });
                
                if (newCards.length > 0) {
                    console.log('🆕 Nouvelles tâches détectées:', newCards.length);
                    newCards.forEach(card => {
                        if (!card.hasAttribute('data-drag-initialized')) {
                            card.draggable = true;
                            card.style.cursor = 'grab';
                            card.addEventListener('dragstart', handleDragStart);
                            card.addEventListener('dragend', handleDragEnd);
                            card.setAttribute('data-drag-initialized', 'true');
                            console.log('✅ Nouvelle tâche configurée:', card.dataset.taskId);
                        }
                    });
                }
            }
        });
    });
    
    // Observer tout le document pour les changements
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

// Réinitialiser quand on change d'onglet
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('tab-btn') && e.target.getAttribute('data-tab') === 'tasks') {
        setTimeout(() => {
            initMinimalDragDrop();
        }, 300);
    }
});

console.log('🎯 Drag & Drop corrigé chargé!');
