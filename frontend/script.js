const form = document.getElementById("admissionForm");

const urlParams = new URLSearchParams(window.location.search);
const editId = urlParams.get("edit");

// ============================================================
// GLOBAL SUBMISSION PROTECTION
// ============================================================

let isSubmitting = false;


// ============================================================
// EDIT MODE
// ============================================================

if (editId !== null) {

    // Fetch existing student data
    fetch(`/api/students/${editId}`)
        .then(response => {

            if (!response.ok) {
                throw new Error("Student not found");
            }

            return response.json();
        })

        .then(student => {

            // ------------------------------------------------
            // Update page heading
            // ------------------------------------------------

            const heading = document.querySelector(".container h2");

            if (heading) {
                heading.textContent =
                    "Edit Student Admission Form";
            }

            const submitButton =
                document.querySelector(".submit-btn");

            if (submitButton) {
                submitButton.textContent =
                    "Update Student";
            }


            // ------------------------------------------------
            // Personal Information
            // ------------------------------------------------

            document.getElementById("fullName").value =
                student.fullName || "";

            document.getElementById("fatherName").value =
                student.fatherName || "";

            document.getElementById("motherName").value =
                student.motherName || "";

            document.getElementById("dob").value =
                student.dob || "";

            document.getElementById("gender").value =
                student.gender || "";

            document.getElementById("bloodGroup").value =
                student.bloodGroup || "";


            // ------------------------------------------------
            // Contact Information
            // ------------------------------------------------

            document.getElementById("mobile").value =
                student.mobile || "";

            document.getElementById("altMobile").value =
                student.altMobile || "";

            document.getElementById("email").value =
                student.email || "";

            document.getElementById("aadhaar").value =
                student.aadhaar || "";

            document.getElementById("address").value =
                student.address || "";

            document.getElementById("city").value =
                student.city || "";

            document.getElementById("state").value =
                student.state || "";

            document.getElementById("pincode").value =
                student.pincode || "";

            document.getElementById("nationality").value =
                student.nationality || "";


            // ------------------------------------------------
            // Academic Information
            // ------------------------------------------------

            document.getElementById("board10").value =
                student.board10 || "";

            document.getElementById("percentage10").value =
                student.percentage10 || "";

            document.getElementById("board12").value =
                student.board12 || "";

            document.getElementById("percentage12").value =
                student.percentage12 || "";

            document.getElementById("entranceExam").value =
                student.entranceExam || "";

            document.getElementById("entranceScore").value =
                student.entranceScore || "";


            // ------------------------------------------------
            // Course Selection
            // ------------------------------------------------

            document.getElementById("department").value =
                student.department || "";

            document.getElementById("admissionType").value =
                student.admissionType || "";


            // ------------------------------------------------
            // Declaration
            // ------------------------------------------------

            const declaration =
                document.getElementById("declaration");

            if (declaration) {
                declaration.checked = true;
            }


            // ------------------------------------------------
            // Existing Documents
            // ------------------------------------------------

            const docs = [

                {
                    id: "photo",
                    label: "Passport Photo",
                    val: student.photo
                },

                {
                    id: "marksheet10",
                    label: "10th Marksheet",
                    val: student.marksheet10
                },

                {
                    id: "marksheet12",
                    label: "12th Marksheet",
                    val: student.marksheet12
                },

                {
                    id: "leavingCertificate",
                    label: "Leaving Certificate",
                    val: student.leavingCertificate
                }

            ];


            docs.forEach(doc => {

                const element =
                    document.getElementById(doc.id);

                if (!element || !doc.val) {
                    return;
                }


                let helper =
                    element.parentElement.querySelector(
                        ".file-helper"
                    );


                if (!helper) {

                    helper =
                        document.createElement("small");

                    helper.className =
                        "file-helper";

                    helper.style.display =
                        "block";

                    helper.style.marginTop =
                        "4px";

                    helper.style.color =
                        "#0d9488";

                    helper.style.fontWeight =
                        "600";

                    element.parentElement.appendChild(
                        helper
                    );
                }


                helper.innerHTML =
                    `✓ Existing: 
                    <a 
                        href="/uploads/${escapeHtml(doc.val)}"
                        target="_blank"
                        style="color:#0d9488;"
                    >
                        ${escapeHtml(doc.val)}
                    </a>
                    (Upload new file to replace)`;
            });

        })

        .catch(error => {

            console.error(
                "Error loading student details:",
                error
            );

        });
}


// ============================================================
// FORM SUBMISSION
// ============================================================

if (form) {

    form.addEventListener(
        "submit",
        async function (e) {

            // ------------------------------------------------
            // IMPORTANT
            // ------------------------------------------------

            e.preventDefault();
            e.stopPropagation();


            // ------------------------------------------------
            // BLOCK DOUBLE SUBMISSION
            // ------------------------------------------------

            if (isSubmitting) {

                console.log(
                    "Duplicate submission blocked."
                );

                return;
            }


            isSubmitting = true;


            // ------------------------------------------------
            // SUBMIT BUTTON
            // ------------------------------------------------

            const submitButton =
                document.querySelector(".submit-btn");


            const originalButtonText =
                submitButton
                    ? submitButton.textContent
                    : "Submit Application";


            if (submitButton) {

                submitButton.disabled = true;

                submitButton.textContent =
                    editId !== null
                        ? "Updating..."
                        : "Submitting...";
            }


            try {

                // ====================================================
                // ERROR BOX
                // ====================================================

                const errorBox =
                    document.getElementById(
                        "errorMessage"
                    );


                if (errorBox) {

                    errorBox.style.display =
                        "none";

                    errorBox.innerHTML =
                        "";
                }


                // ====================================================
                // REQUIRED DOCUMENT VALIDATION
                // ====================================================

                if (editId === null) {

                    const missingDocs = [];


                    const photo =
                        document.getElementById(
                            "photo"
                        );

                    const marksheet10 =
                        document.getElementById(
                            "marksheet10"
                        );

                    const marksheet12 =
                        document.getElementById(
                            "marksheet12"
                        );

                    const leavingCertificate =
                        document.getElementById(
                            "leavingCertificate"
                        );


                    if (
                        !photo ||
                        photo.files.length === 0
                    ) {
                        missingDocs.push(
                            "Passport Photo"
                        );
                    }


                    if (
                        !marksheet10 ||
                        marksheet10.files.length === 0
                    ) {
                        missingDocs.push(
                            "10th Marksheet"
                        );
                    }


                    if (
                        !marksheet12 ||
                        marksheet12.files.length === 0
                    ) {
                        missingDocs.push(
                            "12th Marksheet"
                        );
                    }


                    if (
                        !leavingCertificate ||
                        leavingCertificate.files.length === 0
                    ) {
                        missingDocs.push(
                            "Leaving Certificate"
                        );
                    }


                    // ------------------------------------------------
                    // Missing Documents
                    // ------------------------------------------------

                    if (missingDocs.length > 0) {

                        let html = `
                            <strong>
                                ⚠ Please upload the following required documents:
                            </strong>
                            <ul>
                        `;


                        missingDocs.forEach(doc => {

                            html +=
                                `<li>${doc}</li>`;

                        });


                        html +=
                            "</ul>";


                        if (errorBox) {

                            errorBox.innerHTML =
                                html;

                            errorBox.style.display =
                                "block";


                            errorBox.scrollIntoView({
                                behavior: "smooth",
                                block: "center"
                            });
                        }


                        // Allow user to fix documents
                        isSubmitting = false;


                        if (submitButton) {

                            submitButton.disabled =
                                false;

                            submitButton.textContent =
                                originalButtonText;
                        }


                        return;
                    }
                }


                // ====================================================
                // CREATE FORMDATA
                // ====================================================

                const formData =
                    new FormData();


                // ------------------------------------------------
                // Personal Information
                // ------------------------------------------------

                formData.append(
                    "fullName",
                    document.getElementById(
                        "fullName"
                    ).value.trim()
                );


                formData.append(
                    "fatherName",
                    document.getElementById(
                        "fatherName"
                    ).value.trim()
                );


                formData.append(
                    "motherName",
                    document.getElementById(
                        "motherName"
                    ).value.trim()
                );


                formData.append(
                    "dob",
                    document.getElementById(
                        "dob"
                    ).value
                );


                formData.append(
                    "gender",
                    document.getElementById(
                        "gender"
                    ).value
                );


                formData.append(
                    "bloodGroup",
                    document.getElementById(
                        "bloodGroup"
                    ).value
                );


                // ------------------------------------------------
                // Contact Information
                // ------------------------------------------------

                formData.append(
                    "mobile",
                    document.getElementById(
                        "mobile"
                    ).value.trim()
                );


                formData.append(
                    "altMobile",
                    document.getElementById(
                        "altMobile"
                    ).value.trim()
                );


                formData.append(
                    "email",
                    document.getElementById(
                        "email"
                    ).value.trim()
                );


                formData.append(
                    "aadhaar",
                    document.getElementById(
                        "aadhaar"
                    ).value.trim()
                );


                formData.append(
                    "address",
                    document.getElementById(
                        "address"
                    ).value.trim()
                );


                formData.append(
                    "city",
                    document.getElementById(
                        "city"
                    ).value.trim()
                );


                formData.append(
                    "state",
                    document.getElementById(
                        "state"
                    ).value.trim()
                );


                formData.append(
                    "pincode",
                    document.getElementById(
                        "pincode"
                    ).value.trim()
                );


                formData.append(
                    "nationality",
                    document.getElementById(
                        "nationality"
                    ).value.trim()
                );


                // ------------------------------------------------
                // Academic Information
                // ------------------------------------------------

                formData.append(
                    "board10",
                    document.getElementById(
                        "board10"
                    ).value.trim()
                );


                formData.append(
                    "percentage10",
                    document.getElementById(
                        "percentage10"
                    ).value
                );


                formData.append(
                    "board12",
                    document.getElementById(
                        "board12"
                    ).value.trim()
                );


                formData.append(
                    "percentage12",
                    document.getElementById(
                        "percentage12"
                    ).value
                );


                formData.append(
                    "entranceExam",
                    document.getElementById(
                        "entranceExam"
                    ).value.trim()
                );


                formData.append(
                    "entranceScore",
                    document.getElementById(
                        "entranceScore"
                    ).value
                );


                // ------------------------------------------------
                // Course Selection
                // ------------------------------------------------

                formData.append(
                    "department",
                    document.getElementById(
                        "department"
                    ).value
                );


                formData.append(
                    "admissionType",
                    document.getElementById(
                        "admissionType"
                    ).value
                );


                // ====================================================
                // FILE UPLOADS
                // ====================================================

                const photoInput =
                    document.getElementById(
                        "photo"
                    );


                if (
                    photoInput &&
                    photoInput.files.length > 0
                ) {

                    formData.append(
                        "photo",
                        photoInput.files[0]
                    );
                }


                const marksheet10Input =
                    document.getElementById(
                        "marksheet10"
                    );


                if (
                    marksheet10Input &&
                    marksheet10Input.files.length > 0
                ) {

                    formData.append(
                        "marksheet10",
                        marksheet10Input.files[0]
                    );
                }


                const marksheet12Input =
                    document.getElementById(
                        "marksheet12"
                    );


                if (
                    marksheet12Input &&
                    marksheet12Input.files.length > 0
                ) {

                    formData.append(
                        "marksheet12",
                        marksheet12Input.files[0]
                    );
                }


                const leavingCertificateInput =
                    document.getElementById(
                        "leavingCertificate"
                    );


                if (
                    leavingCertificateInput &&
                    leavingCertificateInput.files.length > 0
                ) {

                    formData.append(
                        "leavingCertificate",
                        leavingCertificateInput.files[0]
                    );
                }


                // ====================================================
                // API URL + METHOD
                // ====================================================

                const apiUrl =
                    editId !== null
                        ? `/api/students/${editId}`
                        : "/api/students";


                const apiMethod =
                    editId !== null
                        ? "PUT"
                        : "POST";


                console.log(
                    "================================="
                );

                console.log(
                    "Submitting student..."
                );

                console.log(
                    "Method:",
                    apiMethod
                );

                console.log(
                    "URL:",
                    apiUrl
                );

                console.log(
                    "================================="
                );


                // ====================================================
                // SEND REQUEST
                // ====================================================

                const response =
                    await fetch(
                        apiUrl,
                        {
                            method: apiMethod,
                            body: formData
                        }
                    );


                // ------------------------------------------------
                // Read response
                // ------------------------------------------------

                let data;

                try {

                    data =
                        await response.json();

                } catch (jsonError) {

                    data = {
                        error:
                            "Server returned an invalid response."
                    };
                }


                console.log(
                    "Server status:",
                    response.status
                );

                console.log(
                    "Server response:",
                    data
                );


                // ====================================================
                // ERROR RESPONSE
                // ====================================================

                if (!response.ok) {

                    throw new Error(
                        data.error ||
                        data.message ||
                        `Request failed with status ${response.status}`
                    );
                }


                // ====================================================
                // SUCCESS
                // ====================================================

                console.log(
                    "Student saved successfully."
                );


                alert(
                    editId !== null
                        ? "Admission Record Updated Successfully!"
                        : "Admission Form Submitted Successfully!"
                );


                // Reset form
                form.reset();


                // Redirect
                window.location.href =
                    "/view.html";
            }


            // ========================================================
            // ERROR HANDLING
            // ========================================================

            catch (error) {

                console.error(
                    "================================="
                );

                console.error(
                    "API Submit Error:",
                    error
                );

                console.error(
                    "================================="
                );


                alert(
                    "Error saving record: " +
                    error.message
                );


                // Allow retry
                isSubmitting = false;


                if (submitButton) {

                    submitButton.disabled =
                        false;

                    submitButton.textContent =
                        editId !== null
                            ? "Update Student"
                            : "Submit Application";
                }
            }

        }
    );
}


// ============================================================
// ESCAPE HTML HELPER
// ============================================================

function escapeHtml(text) {

    if (
        text === null ||
        text === undefined
    ) {
        return "";
    }


    return String(text)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );
}

// ============================================================
// ADMIN HEADER SYNC & AUTHENTICATION
// ============================================================

(async function initAdminHeader() {
    try {
        const res = await fetch("/api/check-auth");
        if (res.ok) {
            const data = await res.json();
            if (data.authenticated && data.user_type === "admin") {
                const adminName = data.username || "Administrator";
                const adminRole = data.role || "Administrator";
                const avatarSrc = data.avatar || "images/admin-avatar.svg";

                const nameEl = document.getElementById("formAdminName");
                const roleEl = document.getElementById("formAdminRole");
                const avatarEl = document.getElementById("formAdminAvatar");

                if (nameEl) nameEl.textContent = adminName;
                if (roleEl) roleEl.textContent = adminRole;
                if (avatarEl) avatarEl.src = avatarSrc;
            }
        }
    } catch (e) {
        // Guest or applicant mode
    }
})();

async function logoutAdminForm() {
    try {
        await fetch("/api/logout", { method: "POST" });
        window.location.href = "login.html";
    } catch (e) {
        window.location.href = "login.html";
    }
}