// Add an event listener to handle form submission
document.getElementById('uploadForm').onsubmit = async function(event) {
    event.preventDefault();  // Prevent the default form submission behavior
    
    // Get references to form elements and output areas
    const fileInput = document.getElementById('fileUpload');  // File upload input
    const questionInput = document.getElementById('questionInput');  // Text input for user's question
    const resultDiv = document.getElementById('infoOutput');  // Div to display loading or error messages
    const answerDiv = document.getElementById('modelAnswer');  // Div to display the extracted answer
    const submitButton = this.querySelector('button[type="submit"]');  // Form's submit button
    
    // Check if a file is selected; if not, alert the user and exit the function
    if (!fileInput.files[0]) {
        alert("Please select a file to upload.");  // Alert message for missing file selection
        return;
    }
    
    // Disable the submit button and update text to indicate processing
    submitButton.disabled = true;
    submitButton.innerText = 'Processing...';  // Provide feedback to the user
    resultDiv.innerHTML = '<div class="loading">Analyzing document...</div>';  // Display loading message
    answerDiv.innerHTML = '';  // Clear any previous answer
    
    // Prepare form data to send with the request
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);  // Add the selected file
    formData.append("question", questionInput.value);  // Add the user's question
    
    try {
        // Send an asynchronous POST request to the server with the form data
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });
        
        const result = await response.json();  // Parse the JSON response from the server
        
        // Display the answer in the answerDiv or a message if no answer was found
        if (result.answer) {
            answerDiv.innerHTML = result.answer;  // Display extracted answer
        } else {
            answerDiv.innerHTML = 'No answer could be determined from the document.';  // Message for no answer found
        }
        
    } catch (error) {
        // Log any errors and display an error message in the resultDiv
        console.error("Error uploading file:", error);
        resultDiv.innerHTML = '<div class="error">An error occurred while processing the file. Please try again.</div>';
    } finally {
        // Re-enable the submit button and reset text to its original state
        submitButton.disabled = false;
        submitButton.innerText = 'Extract Information';
    }
};
