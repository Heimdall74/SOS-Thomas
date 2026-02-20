// Script de test pour vérifier que les boutons fonctionnent
// À copier-coller dans la console du navigateur sur la page de détails du projet

console.log('🔍 Test de débogage des boutons de gestion des membres');

// Vérifier que les fonctions existent
console.log('Fonctions disponibles:');
console.log('- openManageRolesModal:', typeof window.openManageRolesModal);
console.log('- openAddMemberModal:', typeof window.openAddMemberModal);
console.log('- openEditMemberModal:', typeof window.openEditMemberModal);
console.log('- openEditRoleModal:', typeof window.openEditRoleModal);

// Vérifier que les éléments DOM existent
console.log('Éléments DOM:');
console.log('- manageRolesModal:', !!document.getElementById('manageRolesModal'));
console.log('- addMemberModal:', !!document.getElementById('addMemberModal'));
console.log('- roleModal:', !!document.getElementById('roleModal'));
console.log('- editMemberModal:', !!document.getElementById('editMemberModal'));

// Vérifier que les boutons existent
console.log('Boutons:');
console.log('- Bouton "Gérer les rôles":', !!document.querySelector('button[onclick*="openManageRolesModal"]'));
console.log('- Bouton "Ajouter un membre":', !!document.querySelector('button[onclick*="openAddMemberModal"]'));

// Test direct des fonctions
console.log('🧪 Test direct des fonctions:');
try {
    if (typeof window.openManageRolesModal === 'function') {
        console.log('✅ openManageRolesModal est une fonction');
        // Test d'ouverture (commenté pour ne pas ouvrir réellement)
        // window.openManageRolesModal();
    } else {
        console.log('❌ openManageRolesModal n\'est pas une fonction');
    }
    
    if (typeof window.openAddMemberModal === 'function') {
        console.log('✅ openAddMemberModal est une fonction');
        // Test d'ouverture (commenté pour ne pas ouvrir réellement)
        // window.openAddMemberModal();
    } else {
        console.log('❌ openAddMemberModal n\'est pas une fonction');
    }
} catch (error) {
    console.error('❌ Erreur lors du test des fonctions:', error);
}

// Vérifier les écouteurs d'événements
console.log('📡 Écouteurs d\'événements:');
const roleForm = document.getElementById('roleForm');
const addMemberForm = document.getElementById('addMemberForm');

if (roleForm) {
    console.log('- roleForm trouvé');
    // Vérifier s'il a des écouteurs
    const listeners = getEventListeners ? getEventListeners(roleForm) : 'Non disponible';
    console.log('- Écouteurs sur roleForm:', listeners);
} else {
    console.log('- roleForm NON trouvé');
}

if (addMemberForm) {
    console.log('- addMemberForm trouvé');
    // Vérifier s'il a des écouteurs
    const listeners = getEventListeners ? getEventListeners(addMemberForm) : 'Non disponible';
    console.log('- Écouteurs sur addMemberForm:', listeners);
} else {
    console.log('- addMemberForm NON trouvé');
}

// Test de clic manuel sur les boutons
console.log('🖱️ Test de clic sur les boutons:');
const manageRolesBtn = document.querySelector('button[onclick*="openManageRolesModal"]');
const addMemberBtn = document.querySelector('button[onclick*="openAddMemberModal"]');

if (manageRolesBtn) {
    console.log('✅ Bouton "Gérer les rôles" trouvé, test de clic...');
    // manageRolesBtn.click(); // Décommenter pour tester réellement
} else {
    console.log('❌ Bouton "Gérer les rôles" NON trouvé');
}

if (addMemberBtn) {
    console.log('✅ Bouton "Ajouter un membre" trouvé, test de clic...');
    // addMemberBtn.click(); // Décommenter pour tester réellement
} else {
    console.log('❌ Bouton "Ajouter un membre" NON trouvé');
}

console.log('🏁 Test terminé!');
