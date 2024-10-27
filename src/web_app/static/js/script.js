document.getElementById('uploadForm').onsubmit = async function(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('fileUpload');
    const questionInput = document.getElementById('questionInput');
    const resultDiv = document.getElementById('infoOutput');
    const answerDiv = document.getElementById('modelAnswer');
    const submitButton = this.querySelector('button[type="submit"]');
    
    if (!fileInput.files[0]) {
        alert("Please select a file to upload.");
        return;
    }
    
    submitButton.disabled = true;
    submitButton.innerText = 'Processing...';
    resultDiv.innerHTML = '<div class="loading">Analyzing document...</div>';
    answerDiv.innerHTML = ''; 
    
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("question", questionInput.value); 
    
    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });
        
        const result = await response.json();
        
        if (result.answer) {
            answerDiv.innerHTML = result.answer;
        } else {
            answerDiv.innerHTML = 'No answer could be determined from the document.';
        }
        
    } catch (error) {
        console.error("Error uploading file:", error);
        resultDiv.innerHTML = '<div class="error">An error occurred while processing the file. Please try again.</div>';
    } finally {
        submitButton.disabled = false;
        submitButton.innerText = 'Extract Information';
    }
};
