// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(event) {
            const isValid = validateForm();
            if (!isValid) {
                event.preventDefault();
            }
        });
    }
    
    // Input validation for date fields
    const arrivalMonth = document.getElementById('arrival_month');
    const arrivalDate = document.getElementById('arrival_date');
    
    if (arrivalMonth && arrivalDate) {
        arrivalMonth.addEventListener('change', function() {
            validateDate();
        });
        
        arrivalDate.addEventListener('change', function() {
            validateDate();
        });
    }
    
    // Automatically scroll to the prediction result if it exists
    const predictionResult = document.querySelector('.prediction-result');
    if (predictionResult) {
        setTimeout(() => {
            predictionResult.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
    }
});

// Form validation function
function validateForm() {
    let isValid = true;
    
    // Validate arrival date based on month
    if (!validateDate()) {
        isValid = false;
    }
    
    // Price validation
    const priceInput = document.getElementById('avg_price_per_room');
    if (priceInput && parseFloat(priceInput.value) < 0) {
        alert('Average price per room cannot be negative');
        priceInput.focus();
        isValid = false;
    }
    
    return isValid;
}

// Date validation function
function validateDate() {
    const month = parseInt(document.getElementById('arrival_month').value);
    const date = parseInt(document.getElementById('arrival_date').value);
    
    // Check if date is valid for the selected month
    let maxDate = 31;
    
    if (month === 2) {
        // February (simplified, not accounting for leap years)
        maxDate = 28;
    } else if ([4, 6, 9, 11].includes(month)) {
        // April, June, September, November
        maxDate = 30;
    }
    
    if (date > maxDate) {
        alert(`Invalid date: ${month}/${date}. The month selected has a maximum of ${maxDate} days.`);
        document.getElementById('arrival_date').focus();
        return false;
    }
    
    return true;
}

// Function to copy API example to clipboard
function copyApiExample() {
    const codeBlock = document.querySelector('.code-block');
    if (codeBlock) {
        const textArea = document.createElement('textarea');
        textArea.value = codeBlock.textContent.trim();
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        // Show success message
        const tooltip = document.createElement('div');
        tooltip.textContent = 'Copied to clipboard!';
        tooltip.style.position = 'absolute';
        tooltip.style.backgroundColor = '#4caf50';
        tooltip.style.color = 'white';
        tooltip.style.padding = '5px 10px';
        tooltip.style.borderRadius = '5px';
        tooltip.style.zIndex = '1000';
        
        // Position the tooltip
        const rect = codeBlock.getBoundingClientRect();
        tooltip.style.top = `${rect.top + window.scrollY - 30}px`;
        tooltip.style.left = `${rect.left + window.scrollX + rect.width / 2 - 70}px`;
        
        document.body.appendChild(tooltip);
        
        // Remove the tooltip after 2 seconds
        setTimeout(() => {
            document.body.removeChild(tooltip);
        }, 2000);
    }
}

// Add a copy button next to the code block after page load
window.addEventListener('load', function() {
    const codeBlock = document.querySelector('.code-block');
    if (codeBlock) {
        // Create wrapper for position relative
        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        
        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.textContent = 'Copy';
        copyButton.className = 'btn btn-sm btn-outline-secondary';
        copyButton.style.position = 'absolute';
        copyButton.style.top = '10px';
        copyButton.style.right = '10px';
        
        // Add click event
        copyButton.addEventListener('click', function() {
            copyApiExample();
        });
        
        // Insert elements into DOM
        codeBlock.parentNode.insertBefore(wrapper, codeBlock);
        wrapper.appendChild(codeBlock);
        wrapper.appendChild(copyButton);
    }
});