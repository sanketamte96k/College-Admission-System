const form = document.getElementById("admissionForm");
const urlParams = new URLSearchParams(window.location.search);
const editId = urlParams.get("edit");

// Check if form is in Edit mode
if (editId !== null) {
    // Fetch student data from REST API
    fetch(`/api/students/${editId}`)
        .then(response => {
            if (!response.ok) throw new Error("Student not found");
            return response.json();
        })
        .then(student => {
            // Update Page Headings
            document.querySelector(".container h2").textContent = "Edit Student Admission Form";
            document.querySelector(".submit-btn").textContent = "Update Student";

            // Pre-fill form fields with student data from MySQL
            document.getElementById("fullName").value = student.fullName || "";
            document.getElementById("fatherName").value = student.fatherName || "";
            document.getElementById("motherName").value = student.motherName || "";
            document.getElementById("dob").value = student.dob || "";
            document.getElementById("gender").value = student.gender || "";
            document.getElementById("bloodGroup").value = student.bloodGroup || "";

            document.getElementById("mobile").value = student.mobile || "";
            document.getElementById("altMobile").value = student.altMobile || "";
            document.getElementById("email").value = student.email || "";
            document.getElementById("aadhaar").value = student.aadhaar || "";
            document.getElementById("address").value = student.address || "";
            document.getElementById("city").value = student.city || "";
            document.getElementById("state").value = student.state || "";
            document.getElementById("pincode").value = student.pincode || "";
            document.getElementById("nationality").value = student.nationality || "";

            document.getElementById("board10").value = student.board10 || "";
            document.getElementById("percentage10").value = student.percentage10 || "";
            document.getElementById("board12").value = student.board12 || "";
            document.getElementById("percentage12").value = student.percentage12 || "";
            document.getElementById("entranceExam").value = student.entranceExam || "";
            document.getElementById("entranceScore").value = student.entranceScore || "";

            document.getElementById("department").value = student.department || "";
            document.getElementById("admissionType").value = student.admissionType || "";

            document.getElementById("declaration").checked = true;

            // Display existing file status under document inputs
            const docs = [
                { id: "photo", label: "Passport Photo", val: student.photo },
                { id: "marksheet10", label: "10th Marksheet", val: student.marksheet10 },
                { id: "marksheet12", label: "12th Marksheet", val: student.marksheet12 },
                { id: "leavingCertificate", label: "Leaving Certificate", val: student.leavingCertificate }
            ];

            docs.forEach(doc => {
                const el = document.getElementById(doc.id);
                if (el && doc.val) {
                    let helper = el.parentElement.querySelector(".file-helper");
                    if (!helper) {
                        helper = document.createElement("small");
                        helper.className = "file-helper";
                        helper.style.display = "block";
                        helper.style.marginTop = "4px";
                        helper.style.color = "#0d9488";
                        helper.style.fontWeight = "600";
                        el.parentElement.appendChild(helper);
                    }
                    helper.innerHTML = `✓ Existing: <a href="/uploads/${escapeHtml(doc.val)}" target="_blank" style="color:#0d9488;">${escapeHtml(doc.val)}</a> (Upload new file to replace)`;
                }
            });
        })
        .catch(err => {
            console.error("Error loading student details:", err);
        });
}

form.addEventListener("submit", function (e) {
    e.preventDefault();

    // Hide previous error
    const errorBox = document.getElementById("errorMessage");
    errorBox.style.display = "none";
    errorBox.innerHTML = "";

    // Document Validation (Required for new admissions, optional for edit mode)
    if (editId === null) {
        let missingDocs = [];

        if (document.getElementById("photo").files.length === 0)
            missingDocs.push("Passport Photo");

        if (document.getElementById("marksheet10").files.length === 0)
            missingDocs.push("10th Marksheet");

        if (document.getElementById("marksheet12").files.length === 0)
            missingDocs.push("12th Marksheet");

        if (document.getElementById("leavingCertificate").files.length === 0)
            missingDocs.push("Leaving Certificate");

        if (missingDocs.length > 0) {
            let html = `
                <strong>⚠ Please upload the following required documents:</strong>
                <ul>
            `;

            missingDocs.forEach(doc => {
                html += `<li>${doc}</li>`;
            });

            html += "</ul>";

            errorBox.innerHTML = html;
            errorBox.style.display = "block";

            errorBox.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });

            return;
        }
    }

    // Collect student data in FormData object to support file uploads
    const formData = new FormData();
    formData.append("fullName", document.getElementById("fullName").value);
    formData.append("fatherName", document.getElementById("fatherName").value);
    formData.append("motherName", document.getElementById("motherName").value);
    formData.append("dob", document.getElementById("dob").value);
    formData.append("gender", document.getElementById("gender").value);
    formData.append("bloodGroup", document.getElementById("bloodGroup").value);

    formData.append("mobile", document.getElementById("mobile").value);
    formData.append("altMobile", document.getElementById("altMobile").value);
    formData.append("email", document.getElementById("email").value);
    formData.append("aadhaar", document.getElementById("aadhaar").value);
    formData.append("address", document.getElementById("address").value);
    formData.append("city", document.getElementById("city").value);
    formData.append("state", document.getElementById("state").value);
    formData.append("pincode", document.getElementById("pincode").value);
    formData.append("nationality", document.getElementById("nationality").value);

    formData.append("board10", document.getElementById("board10").value);
    formData.append("percentage10", document.getElementById("percentage10").value);
    formData.append("board12", document.getElementById("board12").value);
    formData.append("percentage12", document.getElementById("percentage12").value);
    formData.append("entranceExam", document.getElementById("entranceExam").value);
    formData.append("entranceScore", document.getElementById("entranceScore").value);

    formData.append("department", document.getElementById("department").value);
    formData.append("admissionType", document.getElementById("admissionType").value);

    // Append file inputs if selected
    const photoInput = document.getElementById("photo");
    if (photoInput && photoInput.files.length > 0) {
        formData.append("photo", photoInput.files[0]);
    }

    const marksheet10Input = document.getElementById("marksheet10");
    if (marksheet10Input && marksheet10Input.files.length > 0) {
        formData.append("marksheet10", marksheet10Input.files[0]);
    }

    const marksheet12Input = document.getElementById("marksheet12");
    if (marksheet12Input && marksheet12Input.files.length > 0) {
        formData.append("marksheet12", marksheet12Input.files[0]);
    }

    const lcInput = document.getElementById("leavingCertificate");
    if (lcInput && lcInput.files.length > 0) {
        formData.append("leavingCertificate", lcInput.files[0]);
    }

    // Determine whether to create (POST) or update (PUT) via REST API
    const apiUrl = editId !== null ? `/api/students/${editId}` : "/api/students";
    const apiMethod = editId !== null ? "PUT" : "POST";

    fetch(apiUrl, {
        method: apiMethod,
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error("Failed to save student record");
        return response.json();
    })
    .then(data => {
        alert(editId !== null ? "Admission Record Updated Successfully!" : "Admission Form Submitted Successfully!");
        form.reset();
        window.location.href = "view.html";
    })
    .catch(error => {
        alert("Error saving record: " + error.message);
        console.error("API Submit Error:", error);
    });
});

/**
 * Escape HTML helper function
 */
function escapeHtml(text) {
    if (!text && text !== 0) return "";
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}