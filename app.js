// JavaScript functionality for the Insurance AI Agent interface.

// Helper function to simulate agent responses
function getAgentResponse(module, inputData) {
    const responses = {
        'policy-comparison': `You selected policy type: ${inputData}`,
        'claims-filing': `Claim details received: ${inputData}`,
        'document-management': 'Your document has been uploaded successfully.'
    };
    return responses[module] || 'Processing your request...';
}

// Function to handle form submissions
function handleFormSubmit(event) {
    event.preventDefault(); // Prevent default form submission behavior

    const form = event.target;
    const moduleId = form.closest('.module').id; // Get the module ID
    const inputData = form.querySelector('input, textarea, file').value || 'No data';

    // Simulate agent response
    const response = getAgentResponse(moduleId, inputData);

    // Display the response
    const responseContainer = document.createElement('div');
    responseContainer.className = 'agent-response';
    responseContainer.textContent = response;
    form.appendChild(responseContainer);
}

// Attach event listeners to forms
function initializeEventListeners() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => form.addEventListener('submit', handleFormSubmit));
}

// Initialize the application
function initializeApp() {
    console.log('Initializing Insurance AI Agent Interface...');
    initializeEventListeners();
}

// Wait for DOM content to load
document.addEventListener('DOMContentLoaded', initializeApp);