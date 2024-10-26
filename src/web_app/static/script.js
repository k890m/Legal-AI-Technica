// script.js
document.getElementById('uploadForm').onsubmit = async function(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('fileUpload');
    const resultDiv = document.getElementById('infoOutput');
    const submitButton = this.querySelector('button[type="submit"]');
    
    if (!fileInput.files[0]) {
        alert("Please select a file to upload.");
        return;
    }
    
    // Disable submit button and show loading state
    submitButton.disabled = true;
    submitButton.innerText = 'Processing...';
    resultDiv.innerHTML = '<div class="loading">Analyzing document...</div>';
    
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    
    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Format and display results
            let output = '<div class="results-container">';
            
            // Dates
            if (result.dates && result.dates.length > 0) {
                output += '<div class="result-section"><h3>Important Dates</h3><ul>';
                result.dates.forEach(date => output += `<li>${date}</li>`);
                output += '</ul></div>';
            }
            
            // Amounts
            if (result.amounts && result.amounts.length > 0) {
                output += '<div class="result-section"><h3>Financial Values</h3><ul>';
                result.amounts.forEach(amount => output += `<li>${amount}</li>`);
                output += '</ul></div>';
            }
            
            // Parties
            if (result.parties && result.parties.length > 0) {
                output += '<div class="result-section"><h3>Parties Involved</h3><ul>';
                result.parties.forEach(party => output += `<li>${party}</li>`);
                output += '</ul></div>';
            }
            
            // Contact Information
            if ((result.emails && result.emails.length > 0) || (result.phone_numbers && result.phone_numbers.length > 0)) {
                output += '<div class="result-section"><h3>Contact Information</h3><ul>';
                result.emails?.forEach(email => output += `<li>📧 ${email}</li>`);
                result.phone_numbers?.forEach(phone => output += `<li>📞 ${phone}</li>`);
                output += '</ul></div>';
            }
            
            // Key Clauses
            if (result.key_clauses && Object.keys(result.key_clauses).length > 0) {
                output += '<div class="result-section"><h3>Key Clauses</h3>';
                for (const [type, clauses] of Object.entries(result.key_clauses)) {
                    output += `<div class="clause-type"><h4>${type.charAt(0).toUpperCase() + type.slice(1)}</h4><ul>`;
                    clauses.forEach(clause => output += `<li>${clause}</li>`);
                    output += '</ul></div>';
                }
                output += '</div>';
            }
            
            output += '</div>';
            resultDiv.innerHTML = output;
        } else {
            resultDiv.innerHTML = `<div class="error">Error: ${result.error}</div>`;
        }
    } catch (error) {
        console.error("Error uploading file:", error);
        resultDiv.innerHTML = '<div class="error">An error occurred while processing the file. Please try again.</div>';
    } finally {
        // Re-enable submit button
        submitButton.disabled = false;
        submitButton.innerText = 'Extract Information';
    }
};
