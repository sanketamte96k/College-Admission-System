document.addEventListener("DOMContentLoaded", function () {
    let currentStudent = null;

    const studentNameDisplay = document.getElementById("studentNameDisplay");
    const studentAppIdDisplay = document.getElementById("studentAppIdDisplay");
    const studentDeptDisplay = document.getElementById("studentDeptDisplay");
    const statusBadgeDisplay = document.getElementById("statusBadgeDisplay");

    const contactModal = document.getElementById("contactModal");
    const openContactEditBtn = document.getElementById("openContactEditBtn");
    const closeContactModalBtn = document.getElementById("closeContactModalBtn");
    const editContactForm = document.getElementById("editContactForm");

    const downloadPdfBtn = document.getElementById("downloadPdfBtn");
    const studentLogoutBtn = document.getElementById("studentLogoutBtn");
    const toastContainer = document.getElementById("toastContainer");

    // Fetch Logged In Student Profile
    function loadStudentProfile() {
        fetch("/api/student/profile")
            .then(res => {
                if (!res.ok) {
                    window.location.href = "student-login.html";
                    throw new Error("Unauthorized");
                }
                return res.json();
            })
            .then(student => {
                currentStudent = student;
                renderStudentPortal(student);
            })
            .catch(err => {
                console.error("Profile load error:", err);
            });
    }

    function renderStudentPortal(student) {
        // Top Header & Status
        if (studentNameDisplay) studentNameDisplay.textContent = student.fullName || "Student";
        if (studentAppIdDisplay) studentAppIdDisplay.textContent = `#${student.id}`;
        if (studentDeptDisplay) studentDeptDisplay.textContent = student.department || "-";

        // Status Badge & Colors
        const status = student.status || "Pending Verification";
        if (statusBadgeDisplay) {
            statusBadgeDisplay.className = "status-badge-lg";
            if (status === "Verified" || status === "Approved") {
                statusBadgeDisplay.classList.add("status-approved");
                statusBadgeDisplay.textContent = "✅ Verified & Approved";
            } else if (status === "Rejected") {
                statusBadgeDisplay.classList.add("status-rejected");
                statusBadgeDisplay.textContent = "❌ Rejected";
            } else if (status === "Under Review" || status === "Hold") {
                statusBadgeDisplay.classList.add("status-hold");
                statusBadgeDisplay.textContent = "🔍 Under Review";
            } else {
                statusBadgeDisplay.classList.add("status-pending");
                statusBadgeDisplay.textContent = "⌛ Pending Verification";
            }
        }

        // Timeline Progress Step Highlighting
        updateTimelineProgress(status);

        // Personal Info
        setText("pFullName", student.fullName);
        setText("pFatherName", student.fatherName);
        setText("pMotherName", student.motherName);
        setText("pDob", student.dob);
        setText("pGender", student.gender);
        setText("pBloodGroup", student.bloodGroup);

        // Contact Info
        setText("pMobile", student.mobile);
        setText("pAltMobile", student.altMobile || "-");
        setText("pEmail", student.email);
        setText("pAadhaar", student.aadhaar);
        setText("pAddress", student.address);
        setText("pCityState", `${student.city || '-'}, ${student.state || '-'}`);
        setText("pPincode", student.pincode);

        // Academic Info
        setText("pPerc10", (student.percentage10 || "-") + "%");
        setText("pPerc12", (student.percentage12 || "-") + "%");
        setText("pExam", student.entranceExam);
        setText("pScore", student.entranceScore);
        setText("pDepartment", student.department);
        setText("pAdmissionType", student.admissionType);

        // Verification Remarks if present
        const remarksContainer = document.getElementById("studentRemarksNotice");
        if (remarksContainer) {
            if (student.verification_remarks) {
                remarksContainer.style.display = "block";
                remarksContainer.innerHTML = `
                    <div style="background: ${status === 'Rejected' ? '#fef2f2' : '#f0fdf4'}; border: 1px solid ${status === 'Rejected' ? '#fca5a5' : '#86efac'}; border-radius: 8px; padding: 12px 16px; margin: 15px 0;">
                        <strong style="color: ${status === 'Rejected' ? '#991b1b' : '#166534'};">Verification Officer Remarks:</strong>
                        <p style="margin: 4px 0 0 0; color: #334155; font-size: 13px;">${student.verification_remarks}</p>
                    </div>
                `;
            } else {
                remarksContainer.style.display = "none";
            }
        }

        // Render Uploaded Document Action Buttons
        renderDocumentButtons(student);
    }

    function updateTimelineProgress(status) {
        const steps = [
            document.getElementById("step1"),
            document.getElementById("step2"),
            document.getElementById("step3"),
            document.getElementById("step4"),
            document.getElementById("step5")
        ];

        steps.forEach(s => { if (s) s.className = "timeline-step"; });

        if (status === "Verified" || status === "Approved") {
            steps.forEach(s => { if (s) s.className = "timeline-step completed"; });
        } else if (status === "Under Review" || status === "Hold") {
            if (steps[0]) steps[0].className = "timeline-step completed";
            if (steps[1]) steps[1].className = "timeline-step completed";
            if (steps[2]) steps[2].className = "timeline-step active";
        } else if (status === "Rejected") {
            if (steps[0]) steps[0].className = "timeline-step completed";
            if (steps[1]) steps[1].className = "timeline-step active";
        } else {
            // Default Pending Verification
            if (steps[0]) steps[0].className = "timeline-step completed";
            if (steps[1]) steps[1].className = "timeline-step active";
        }
    }

    function renderDocumentButtons(student) {
        const container = document.getElementById("studentDocButtons");
        if (!container) return;
        container.innerHTML = "";

        const docs = [
            { label: "Passport Photo", file: student.photo },
            { label: "10th Marksheet", file: student.marksheet10 },
            { label: "12th Marksheet", file: student.marksheet12 },
            { label: "Leaving Certificate", file: student.leavingCertificate }
        ];

        docs.forEach(doc => {
            const btn = document.createElement("a");
            btn.className = "doc-btn";
            btn.style.display = "flex";
            btn.style.justify = "space-between";
            btn.style.alignItems = "center";
            btn.style.padding = "8px 12px";
            btn.style.border = "1px solid #cbd5e1";
            btn.style.borderRadius = "6px";
            btn.style.fontSize = "13px";
            btn.style.color = "#1e3a8a";
            btn.style.textDecoration = "none";
            btn.style.background = "#f8fafc";

            if (doc.file) {
                btn.href = `/uploads/${doc.file}`;
                btn.target = "_blank";
                btn.innerHTML = `<span>📄 ${doc.label}</span><span style="color: #059669; font-weight: 600;">✓ View</span>`;
            } else {
                btn.href = "#";
                btn.style.opacity = "0.6";
                btn.style.cursor = "not-allowed";
                btn.innerHTML = `<span>📄 ${doc.label}</span><span style="color: #94a3b8;">Not Uploaded</span>`;
                btn.addEventListener("click", e => e.preventDefault());
            }
            container.appendChild(btn);
        });
    }

    function setText(id, val) {
        const el = document.getElementById(id);
        if (el) el.textContent = val || "-";
    }

    // Modal Control & Contact Info Edit
    if (openContactEditBtn) {
        openContactEditBtn.addEventListener("click", function () {
            if (!currentStudent) return;
            document.getElementById("editMobile").value = currentStudent.mobile || "";
            document.getElementById("editAltMobile").value = currentStudent.altMobile || "";
            document.getElementById("editEmail").value = currentStudent.email || "";
            document.getElementById("editAddress").value = currentStudent.address || "";
            document.getElementById("editCity").value = currentStudent.city || "";
            document.getElementById("editState").value = currentStudent.state || "";
            document.getElementById("editPincode").value = currentStudent.pincode || "";
            contactModal.style.display = "flex";
        });
    }

    if (closeContactModalBtn) {
        closeContactModalBtn.addEventListener("click", function () {
            contactModal.style.display = "none";
        });
    }

    if (editContactForm) {
        editContactForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const updatedData = {
                mobile: document.getElementById("editMobile").value.trim(),
                altMobile: document.getElementById("editAltMobile").value.trim(),
                email: document.getElementById("editEmail").value.trim(),
                address: document.getElementById("editAddress").value.trim(),
                city: document.getElementById("editCity").value.trim(),
                state: document.getElementById("editState").value.trim(),
                pincode: document.getElementById("editPincode").value.trim()
            };

            fetch("/api/student/profile", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(updatedData)
            })
            .then(res => {
                if (!res.ok) throw new Error("Failed to update profile");
                return res.json();
            })
            .then(data => {
                contactModal.style.display = "none";
                showToast("Contact details updated successfully!", "success");
                loadStudentProfile();
            })
            .catch(err => {
                showToast("Unable to update contact details.", "error");
            });
        });
    }

    // PDF Download Handler
    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener("click", function () {
            if (!currentStudent) return;
            generateStudentPDF(currentStudent);
        });
    }

    function generateStudentPDF(student) {
        if (!window.jspdf) {
            showToast("jsPDF library loading error", "error");
            return;
        }

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });

        doc.rect(6, 6, 198, 285);
        doc.setFillColor(30, 58, 138);
        doc.rect(10, 10, 190, 24, "F");

        doc.setTextColor(255, 255, 255);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(16);
        doc.text("ZEAL COLLEGE OF ENGINEERING", 15, 20);
        doc.setFontSize(10);
        doc.setFont("helvetica", "normal");
        doc.text("OFFICIAL ADMISSION APPLICATION FORM", 15, 27);

        doc.setTextColor(30, 58, 138);
        doc.setFontSize(12);
        doc.setFont("helvetica", "bold");
        doc.text("1. PERSONAL DETAILS", 15, 45);
        doc.setFontSize(10);
        doc.setFont("helvetica", "normal");
        doc.setTextColor(51, 65, 85);
        doc.text(`Full Name: ${student.fullName || '-'}`, 15, 52);
        doc.text(`Father's Name: ${student.fatherName || '-'}`, 15, 58);
        doc.text(`Mother's Name: ${student.motherName || '-'}`, 15, 64);
        doc.text(`Date of Birth: ${student.dob || '-'} | Gender: ${student.gender || '-'}`, 15, 70);

        doc.setTextColor(30, 58, 138);
        doc.setFontSize(12);
        doc.setFont("helvetica", "bold");
        doc.text("2. CONTACT DETAILS", 15, 85);
        doc.setFontSize(10);
        doc.setFont("helvetica", "normal");
        doc.setTextColor(51, 65, 85);
        doc.text(`Mobile: ${student.mobile || '-'} | Email: ${student.email || '-'}`, 15, 92);
        doc.text(`Address: ${student.address || '-'}, ${student.city || '-'}, ${student.state || '-'} - ${student.pincode || '-'}`, 15, 98);

        doc.setTextColor(30, 58, 138);
        doc.setFontSize(12);
        doc.setFont("helvetica", "bold");
        doc.text("3. ACADEMIC & COURSE DETAILS", 15, 113);
        doc.setFontSize(10);
        doc.setFont("helvetica", "normal");
        doc.setTextColor(51, 65, 85);
        doc.text(`10th %: ${student.percentage10 || '-'}% | 12th %: ${student.percentage12 || '-'}%`, 15, 120);
        doc.text(`Entrance Exam: ${student.entranceExam || '-'} | Score: ${student.entranceScore || '-'}`, 15, 126);
        doc.text(`Department: ${student.department || '-'}`, 15, 132);
        doc.text(`Admission Type: ${student.admissionType || '-'}`, 15, 138);

        const safeName = (student.fullName || "Student").trim().replace(/\s+/g, "_");
        const fileName = `Admission_${safeName}.pdf`;
        doc.save(fileName);
        showToast(`Downloaded ${fileName}`, "success");
    }

    // Student Logout Handler
    if (studentLogoutBtn) {
        studentLogoutBtn.addEventListener("click", function () {
            fetch("/api/student-logout", { method: "POST" })
                .then(() => { window.location.href = "student-login.html"; })
                .catch(() => { window.location.href = "student-login.html"; });
        });
    }

    function showToast(message, type = "success") {
        if (!toastContainer) return;
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        const icon = type === "success" ? "✅" : "⚠️";
        toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.classList.add("toast-fade-out");
            setTimeout(() => {
                if (toast.parentElement) toast.parentElement.removeChild(toast);
            }, 300);
        }, 3000);
    }

    // Initialize Student Profile Load
    loadStudentProfile();
});
