// Function to handle approval
function approveCompany(companyName) {
    // Make an AJAX request to your server to mark the company as approved
    // Send the companyName as a parameter to identify which company to approve

    // Example using Fetch API:
    fetch(`/api/approveCompany/${encodeURIComponent(companyName)}`, {
        method: 'POST',
        // Add headers and other necessary information
    })
    .then(response => {
        if (response.ok) {
            // Update the UI to indicate approval (e.g., change button color)
            document.getElementById(`approveButton${companyName}`).disabled = true;
            document.getElementById(`rejectButton${companyName}`).disabled = true;
        } else {
            // Handle error
            console.error('Failed to approve company');
        }
    })
    .catch(error => {
        // Handle network error
        console.error('Network error:', error);
    });
}

// Function to handle rejection
function rejectCompany(companyName) {
    // Make an AJAX request to your server to mark the company as rejected
    // Send the companyName as a parameter to identify which company to reject

    // Example using Fetch API:
    fetch(`/api/rejectCompany/${encodeURIComponent(companyName)}`, {
        method: 'POST',
        // Add headers and other necessary information
    })
    .then(response => {
        if (response.ok) {
            // Update the UI to indicate rejection (e.g., change button color)
            document.getElementById(`approveButton${companyName}`).disabled = true;
            document.getElementById(`rejectButton${companyName}`).disabled = true;
        } else {
            // Handle error
            console.error('Failed to reject company');
        }
    })
    .catch(error => {
        // Handle network error
        console.error('Network error:', error);
    });
}

// Add event listeners to approve and reject buttons
document.addEventListener('DOMContentLoaded', () => {
    const approveButtons = document.querySelectorAll('.approve-button');
    const rejectButtons = document.querySelectorAll('.reject-button');

    approveButtons.forEach(button => {
        button.addEventListener('click', () => {
            const companyName = button.dataset.companyName;
            approveCompany(companyName);
        });
    });

    rejectButtons.forEach(button => {
        button.addEventListener('click', () => {
            const companyName = button.dataset.companyName;
            rejectCompany(companyName);
        });
    });
});
