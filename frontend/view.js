// ============================================================
// STUDENT RECORDS - VIEW.JS
// ============================================================

// Global array of students loaded from Flask REST API
let students = [];

// ============================================================
// HTML ESCAPE HELPER
// ============================================================

function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// ============================================================
// DOM ELEMENTS
// ============================================================

const tbody = document.getElementById("studentTableBody");
const searchInput = document.getElementById("searchInput");

const viewModal = document.getElementById("viewModal");
const modalDetails = document.getElementById("modalDetails");
const closeModal = document.getElementById("closeModal");
const closeModalFooter = document.getElementById("closeModalFooter");

const statusFilter = document.getElementById("statusFilter");
const deptFilter = document.getElementById("deptFilter");
const admissionTypeFilter = document.getElementById("admissionTypeFilter");
const genderFilter = document.getElementById("genderFilter");


// ============================================================
// FETCH ALL STUDENTS
// ============================================================

function fetchStudents() {

    fetch("/api/students")
        .then(response => {

            if (!response.ok) {
                throw new Error("Failed to fetch records from server");
            }

            return response.json();
        })

        .then(data => {

            console.log("Students API response:", data);

            /*
             * Backend supports two response formats:
             *
             * 1. Array:
             *    [student1, student2, ...]
             *
             * 2. Object:
             *    {
             *       students: [...],
             *       total: ...
             *    }
             *
             * Handle both safely.
             */

            if (Array.isArray(data)) {
                students = data;
            }
            else if (data && Array.isArray(data.students)) {
                students = data.students;
            }
            else {
                students = [];
            }

            console.log("Students loaded:", students.length);

            renderStudents();
            updateDashboard();
        })

        .catch(err => {

            console.error("API Fetch Error:", err);

            students = [];

            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="8" class="empty-state">
                            <div class="empty-icon">⚠️</div>
                            <p>Unable to load student records.</p>
                        </td>
                    </tr>
                `;
            }
        });
}


// ============================================================
// RENDER STUDENTS
// ============================================================

function renderStudents() {

    if (!tbody) {
        console.error("studentTableBody element not found.");
        return;
    }

    tbody.innerHTML = "";

    const nameQuery =
        searchInput
            ? searchInput.value.toLowerCase().trim()
            : "";

    const statusVal =
        statusFilter
            ? statusFilter.value.trim()
            : "";

    const deptVal =
        deptFilter
            ? deptFilter.value.trim()
            : "";

    const typeVal =
        admissionTypeFilter
            ? admissionTypeFilter.value.trim()
            : "";

    const genderVal =
        genderFilter
            ? genderFilter.value.trim()
            : "";


    // ========================================================
    // FILTER STUDENTS
    // ========================================================

    const filteredStudents = students.filter(student => {

        const matchesName =
            (student.fullName || "")
                .toLowerCase()
                .includes(nameQuery);

        const matchesStatus =
            !statusVal ||
            (student.status === statusVal) ||
            (!student.status && statusVal === "Pending Verification");

        const matchesDept =
            !deptVal ||
            student.department === deptVal;

        const matchesType =
            !typeVal ||
            student.admissionType === typeVal;

        const matchesGender =
            !genderVal ||
            student.gender === genderVal;

        return (
            matchesName &&
            matchesStatus &&
            matchesDept &&
            matchesType &&
            matchesGender
        );
    });


    // ========================================================
    // EMPTY STATE
    // ========================================================

    if (filteredStudents.length === 0) {

        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="empty-state">

                    <div class="empty-icon">
                        📂
                    </div>

                    <p>
                        No matching student records found.
                    </p>

                </td>
            </tr>
        `;

        return;
    }


    // ========================================================
    // RENDER TABLE ROWS
    // ========================================================

    filteredStudents.forEach((student, index) => {

        const studentId = Number(student.id);

        let statusBadgeClass = "badge-status-pending";
        let statusIcon = "⌛";
        const currentStatus = student.status || "Pending Verification";

        if (currentStatus === "Verified") {
            statusBadgeClass = "badge-status-verified";
            statusIcon = "✅";
        } else if (currentStatus === "Under Review") {
            statusBadgeClass = "badge-status-review";
            statusIcon = "🔍";
        } else if (currentStatus === "Rejected") {
            statusBadgeClass = "badge-status-rejected";
            statusIcon = "❌";
        }

        const tr = document.createElement("tr");

        tr.innerHTML = `

            <td>
                ${index + 1}
            </td>

            <td>
                <strong>
                    ${escapeHtml(student.fullName)}
                </strong>
            </td>

            <td>
                ${escapeHtml(student.department)}
            </td>

            <td>
                ${escapeHtml(student.mobile)}
            </td>

            <td>
                ${escapeHtml(student.email)}
            </td>

            <td>
                <span class="badge badge-academic">
                    ${escapeHtml(student.percentage12)}%
                </span>
            </td>

            <td>
                <span class="badge badge-score">
                    ${escapeHtml(student.entranceScore)}
                </span>
            </td>

            <td>
                <span class="badge-status ${statusBadgeClass}">
                    <span>${statusIcon}</span>
                    <span>${escapeHtml(currentStatus)}</span>
                </span>
            </td>

            <td class="action-cell">

                <button
                    class="btn btn-view"
                    onclick="openViewModal(${studentId})"
                    title="View Details">
                    👁 View
                </button>

                <button
                    class="btn btn-edit"
                    onclick="editStudent(${studentId})"
                    title="Edit Record">
                    ✏ Edit
                </button>

                <button
                    class="btn btn-download"
                    onclick="downloadPDF(${studentId})"
                    title="Download Admission Form PDF">
                    📥 Download PDF
                </button>

                <button
                    class="btn btn-delete"
                    onclick="deleteStudent(${studentId})"
                    title="Delete Record">
                    🗑 Delete
                </button>

            </td>
        `;

        tbody.appendChild(tr);
    });
}


// ============================================================
// FILTER EVENTS
// ============================================================

[
    searchInput,
    statusFilter,
    deptFilter,
    admissionTypeFilter,
    genderFilter
].forEach(element => {

    if (!element) {
        return;
    }

    element.addEventListener("input", renderStudents);
    element.addEventListener("change", renderStudents);

});


// ============================================================
// OPEN VIEW MODAL
// ============================================================

function openViewModal(studentId) {

    if (!viewModal || !modalDetails) {
        console.error("View modal elements not found.");
        return;
    }

    modalDetails.innerHTML = `

        <div style="
            text-align:center;
            padding:40px;
            color:#64748b;
        ">

            ⌛ Loading student details...

        </div>
    `;

    viewModal.style.display = "flex";


    fetch(`/api/students/${studentId}`)

        .then(response => {

            if (!response.ok) {
                throw new Error(
                    "Failed to fetch student details"
                );
            }

            return response.json();
        })

        .then(student => {

            console.log(
                "Student details:",
                student
            );

            populateViewModal(student);

        })

        .catch(err => {

            console.error(
                "Error fetching student details:",
                err
            );

            const cachedStudent =
                students.find(
                    s => Number(s.id) === Number(studentId)
                );

            if (cachedStudent) {

                populateViewModal(cachedStudent);

            }
            else {

                modalDetails.innerHTML = `

                    <div style="
                        color:#ef4444;
                        padding:20px;
                    ">

                        ⚠️ Error loading student record.

                    </div>

                `;
            }
        });
}


// ============================================================
// POPULATE VIEW MODAL
// ============================================================

function renderDocumentCard(label, filename, icon = "📄") {
    if (!filename) {
        return `
            <div class="document-item-card">
                <div class="document-item-header">
                    <span>${icon}</span>
                    <span>${escapeHtml(label)}</span>
                </div>
                <span class="doc-btn doc-btn-disabled">Document Not Uploaded</span>
            </div>
        `;
    }

    const fileUrl = `/uploads/${encodeURIComponent(filename)}`;
    return `
        <div class="document-item-card">
            <div class="document-item-header">
                <span>${icon}</span>
                <span>${escapeHtml(label)}</span>
            </div>
            <div class="doc-btn-group">
                <a href="${fileUrl}" target="_blank" class="doc-action-btn btn-doc-preview" title="Preview Document">
                    👁 Preview
                </a>
                <a href="${fileUrl}" target="_blank" class="doc-action-btn btn-doc-open" title="Open in New Tab">
                    ↗ Open
                </a>
                <a href="${fileUrl}" download="${escapeHtml(filename)}" class="doc-action-btn btn-doc-download" title="Download File">
                    📥 Download
                </a>
            </div>
        </div>
    `;
}

function handleModalStatusChange() {
    const statusSelect = document.getElementById("modalVerificationStatus");
    const requiredTag = document.getElementById("remarksRequiredTag");
    if (statusSelect && requiredTag) {
        requiredTag.style.display = (statusSelect.value === "Rejected") ? "inline" : "none";
    }
}

async function saveVerificationDecision(studentId) {
    const statusSelect = document.getElementById("modalVerificationStatus");
    const remarksTextarea = document.getElementById("modalVerificationRemarks");
    const saveBtn = document.getElementById("saveVerificationBtn");

    if (!statusSelect) return;

    const newStatus = statusSelect.value;
    const remarks = remarksTextarea ? remarksTextarea.value.trim() : "";

    if (newStatus === "Rejected" && !remarks) {
        showToast("Please provide verification remarks explaining the reason for rejection.", "error");
        if (remarksTextarea) remarksTextarea.focus();
        return;
    }

    try {
        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.textContent = "Saving Decision...";
        }

        const endpoint = `/api/students/${studentId}/verification`;
        const response = await fetch(endpoint, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            credentials: "same-origin",
            body: JSON.stringify({
                status: newStatus,
                admissionStatus: newStatus,
                remarks: remarks,
                verificationRemarks: remarks
            })
        });

        const contentType = response.headers.get("content-type") || "";
        let data = {};

        if (contentType.includes("application/json")) {
            data = await response.json();
        } else {
            const text = await response.text();
            throw new Error(
                `Server returned non-JSON response (${response.status}): ${text.substring(0, 150)}`
            );
        }

        if (!response.ok) {
            if (response.status === 401) {
                showToast("Session expired. Redirecting to admin login...", "error");
                setTimeout(() => { window.location.href = "login.html"; }, 1500);
                return;
            }
            throw new Error(
                data.error ||
                data.message ||
                `Request failed with status ${response.status}`
            );
        }

        let toastMsg = data.message || `Admission status updated to '${newStatus}' successfully.`;
        if (data.email_status === "sent") {
            toastMsg += " Notification email sent to student.";
        } else if (data.email_status === "failed") {
            toastMsg += " (Note: Notification email could not be delivered)";
        }

        showToast(toastMsg, "success");

        // Update local student in students array
        const localStudent = students.find(s => Number(s.id) === Number(studentId));
        if (localStudent && data.student) {
            Object.assign(localStudent, data.student);
        }

        // Re-render table rows
        renderStudents();

        // Update dashboard metrics
        updateDashboard();

        // Refresh single student details in modal
        if (data.student) {
            populateViewModal(data.student);
        }

    } catch (err) {
        console.error("Verification save error:", err);
        let errorMsg = err.message || "Unknown error";
        if (err.name === "TypeError" && errorMsg.toLowerCase().includes("fetch")) {
            errorMsg = "Network connection error: Unable to reach backend server. Please verify Flask server is running.";
        }
        showToast("Failed to save verification decision: " + errorMsg, "error");
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = "💾 Save Verification Decision";
        }
    }
}

function populateViewModal(student) {
    const currentStatus = student.status || "Pending Verification";

    const photoHtml = student.photo
        ? `
            <div class="passport-photo-wrapper">
                <img
                    src="/uploads/${escapeHtml(student.photo)}"
                    alt="Passport Photo"
                    class="passport-photo-img"
                >
            </div>
          `
        : `
            <div class="passport-photo-wrapper">
                <span class="passport-photo-placeholder">
                    👤
                </span>
            </div>
          `;

    const photoCard = renderDocumentCard("Passport Photo", student.photo, "🖼️");
    const marksheet10Card = renderDocumentCard("10th Marksheet", student.marksheet10, "📄");
    const marksheet12Card = renderDocumentCard("12th Marksheet", student.marksheet12, "📄");
    const lcCard = renderDocumentCard("Leaving Certificate", student.leavingCertificate, "📜");

    modalDetails.innerHTML = `
        <!-- APPLICATION & VERIFICATION WORKFLOW CARD -->
        <div class="verification-decision-card">
            <div class="verification-decision-header">
                <h4>📋 Application Details & Verification Decision</h4>
                <div class="verification-meta">
                    <span>App ID: <strong>#${student.id}</strong></span> | 
                    <span>Date: ${escapeHtml(student.created_at || "N/A")}</span>
                    ${student.verified_by ? ` | <span>Verified By: <strong>${escapeHtml(student.verified_by)}</strong> (${escapeHtml(student.verified_at || '')})</span>` : ''}
                </div>
            </div>

            <div class="verification-form-grid">
                <div class="verification-input-group">
                    <label for="modalVerificationStatus">Admission Status:</label>
                    <select id="modalVerificationStatus" class="verification-status-select" onchange="handleModalStatusChange()">
                        <option value="Pending Verification" ${currentStatus === "Pending Verification" ? "selected" : ""}>⌛ Pending Verification</option>
                        <option value="Under Review" ${currentStatus === "Under Review" ? "selected" : ""}>🔍 Under Review</option>
                        <option value="Verified" ${currentStatus === "Verified" ? "selected" : ""}>✅ Verified / Approved</option>
                        <option value="Rejected" ${currentStatus === "Rejected" ? "selected" : ""}>❌ Rejected</option>
                    </select>
                </div>

                <div class="verification-input-group">
                    <label for="modalVerificationRemarks">
                        Verification Remarks:
                        <span id="remarksRequiredTag" style="display:${currentStatus === 'Rejected' ? 'inline' : 'none'}; color:#dc2626; font-size:12px;">(Required for Rejection)</span>
                    </label>
                    <textarea id="modalVerificationRemarks" class="verification-remarks-textarea" placeholder="Enter verification notes, document inspection remarks, or rejection reason...">${escapeHtml(student.verification_remarks || "")}</textarea>
                </div>
            </div>

            <div style="display: flex; justify-content: flex-end; margin-top: 12px;">
                <button id="saveVerificationBtn" class="verification-btn-save" onclick="saveVerificationDecision(${student.id})">
                    💾 Save Verification Decision
                </button>
            </div>
        </div>

        <div class="modal-profile-card">
            ${photoHtml}
            <div class="modal-profile-info">
                <h3>${escapeHtml(student.fullName)}</h3>
                <p>🎓 ${escapeHtml(student.department)} | ${escapeHtml(student.admissionType)} Admission</p>
                <p>📧 ${escapeHtml(student.email)} | 📱 ${escapeHtml(student.mobile)}</p>
            </div>
        </div>

        <div class="detail-section">
            <h4>👤 Personal Information</h4>
            <div class="detail-grid">
                <div><strong>Full Name:</strong> ${escapeHtml(student.fullName)}</div>
                <div><strong>Father's Name:</strong> ${escapeHtml(student.fatherName)}</div>
                <div><strong>Mother's Name:</strong> ${escapeHtml(student.motherName)}</div>
                <div><strong>Date of Birth:</strong> ${escapeHtml(student.dob)}</div>
                <div><strong>Gender:</strong> ${escapeHtml(student.gender)}</div>
                <div><strong>Blood Group:</strong> ${escapeHtml(student.bloodGroup)}</div>
            </div>
        </div>

        <div class="detail-section">
            <h4>📞 Contact Information</h4>
            <div class="detail-grid">
                <div><strong>Mobile:</strong> ${escapeHtml(student.mobile)}</div>
                <div><strong>Alt Mobile:</strong> ${escapeHtml(student.altMobile || "N/A")}</div>
                <div><strong>Email:</strong> ${escapeHtml(student.email)}</div>
                <div><strong>Aadhaar:</strong> ${escapeHtml(student.aadhaar)}</div>
                <div><strong>Address:</strong> ${escapeHtml(student.address)}</div>
                <div><strong>City:</strong> ${escapeHtml(student.city)}</div>
                <div><strong>State:</strong> ${escapeHtml(student.state)}</div>
                <div><strong>Pincode:</strong> ${escapeHtml(student.pincode)}</div>
                <div><strong>Nationality:</strong> ${escapeHtml(student.nationality)}</div>
            </div>
        </div>

        <div class="detail-section">
            <h4>🎓 Academic Information</h4>
            <div class="detail-grid">
                <div><strong>10th Board:</strong> ${escapeHtml(student.board10)}</div>
                <div><strong>10th Percentage:</strong> ${escapeHtml(student.percentage10)}%</div>
                <div><strong>12th Board:</strong> ${escapeHtml(student.board12)}</div>
                <div><strong>12th Percentage:</strong> ${escapeHtml(student.percentage12)}%</div>
                <div><strong>Entrance Exam:</strong> ${escapeHtml(student.entranceExam)}</div>
                <div><strong>Entrance Score:</strong> ${escapeHtml(student.entranceScore)}</div>
            </div>
        </div>

        <div class="detail-section">
            <h4>📚 Course & Admission Information</h4>
            <div class="detail-grid">
                <div><strong>Department:</strong> ${escapeHtml(student.department)}</div>
                <div><strong>Admission Type:</strong> ${escapeHtml(student.admissionType)}</div>
                <div><strong>Application Status:</strong> <strong>${escapeHtml(currentStatus)}</strong></div>
            </div>
        </div>

        <div class="detail-section">
            <h4>📁 Uploaded Documents</h4>
            <div class="document-grid">
                ${photoCard}
                ${marksheet10Card}
                ${marksheet12Card}
                ${lcCard}
            </div>
        </div>

        <!-- FEES & PAYMENT MANAGEMENT SECTION IN MODAL -->
        <div class="fee-management-card" style="margin-top: 20px;">
            <div class="fee-card-header">
                <h4>💳 Fees & Payment Management</h4>
                <span id="modalFeeStatusBadge" class="fee-badge fee-badge-pending">🔴 Pending</span>
            </div>

            <!-- KPI Tiles -->
            <div class="fee-kpi-grid">
                <div class="fee-kpi-tile kpi-total">
                    <div class="kpi-label">Total Fee</div>
                    <div class="kpi-value" id="mTotalFee">₹ 0</div>
                </div>
                <div class="fee-kpi-tile kpi-paid">
                    <div class="kpi-label">Amount Paid</div>
                    <div class="kpi-value" id="mPaidAmount">₹ 0</div>
                </div>
                <div class="fee-kpi-tile kpi-pending">
                    <div class="kpi-label">Pending Dues</div>
                    <div class="kpi-value" id="mPendingAmount">₹ 0</div>
                </div>
                <div class="fee-kpi-tile kpi-status">
                    <div class="kpi-label">Status</div>
                    <div class="kpi-value" id="mFeeStatusText" style="font-size: 15px; color: #8b5cf6;">Pending</div>
                </div>
            </div>

            <!-- Fee Breakdown Pills -->
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px; margin-bottom: 15px;">
                <strong style="color: #1e3a8a; font-size: 12px;">Fee Breakdown:</strong>
                <div id="mFeeBreakdownPills" style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">
                    <!-- Breakdown items -->
                </div>
            </div>

            <!-- Record Payment Form -->
            <div class="record-payment-card">
                <h5 style="margin: 0 0 12px 0; color: #1e3a8a; font-size: 14px;">➕ Record Student Fee Payment</h5>
                <form id="recordPaymentForm" onsubmit="event.preventDefault(); recordStudentPayment(${student.id});">
                    <div class="record-payment-grid">
                        <div class="pay-input-group">
                            <label for="adminPayAmount">Amount (₹) *</label>
                            <input type="number" id="adminPayAmount" placeholder="e.g. 25000" min="1" step="0.01" required>
                        </div>
                        <div class="pay-input-group">
                            <label for="adminPayFeeType">Fee Category *</label>
                            <select id="adminPayFeeType" required>
                                <option value="Tuition Fee">Tuition Fee</option>
                                <option value="Development Fee">Development Fee</option>
                                <option value="Examination Fee">Examination Fee</option>
                                <option value="Library Fee">Library Fee</option>
                                <option value="Laboratory Fee">Laboratory Fee</option>
                                <option value="Other Fee">Other Fee</option>
                            </select>
                        </div>
                        <div class="pay-input-group">
                            <label for="adminPayMethod">Payment Method *</label>
                            <select id="adminPayMethod" required>
                                <option value="UPI">UPI</option>
                                <option value="Cash">Cash</option>
                                <option value="Bank Transfer">Bank Transfer</option>
                                <option value="Online Payment">Online Payment</option>
                                <option value="Demand Draft">Demand Draft</option>
                            </select>
                        </div>
                        <div class="pay-input-group">
                            <label for="adminPayTxnId">Transaction / Ref ID (Optional)</label>
                            <input type="text" id="adminPayTxnId" placeholder="Auto-generated if empty">
                        </div>
                    </div>
                    <div class="pay-input-group" style="margin-top: 10px;">
                        <label for="adminPayRemarks">Remarks / Notes</label>
                        <input type="text" id="adminPayRemarks" placeholder="Optional payment remarks, receipt notes...">
                    </div>
                    <div style="display: flex; justify-content: flex-end; margin-top: 12px;">
                        <button type="submit" id="adminPaySubmitBtn" class="btn-record-payment">
                            💳 Record Payment
                        </button>
                    </div>
                </form>
            </div>

            <!-- Payment History in Modal -->
            <h5 style="color: #1e3a8a; font-size: 14px; margin: 18px 0 10px 0;">📜 Payment Transactions History</h5>
            <div class="fee-table-wrapper">
                <table class="fee-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Fee Category</th>
                            <th>Amount</th>
                            <th>Method</th>
                            <th>Txn ID</th>
                            <th>Status</th>
                            <th>Recorded By</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody id="mPaymentHistoryBody">
                        <tr>
                            <td colspan="8" style="text-align: center; color: #64748b; padding: 14px;">Loading payment history...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `;

    viewModal.style.display = "flex";
    loadStudentModalFees(student.id, student.fullName);
}


// ============================================================
// EDIT STUDENT
// ============================================================

function editStudent(studentId) {

    window.location.href =
        `index.html?edit=${studentId}`;
}


// ============================================================
// GET IMAGE DATA URL
// ============================================================

function getImageDataUrl(url) {

    return new Promise(resolve => {

        const img = new Image();

        img.crossOrigin = "Anonymous";

        img.onload = function () {

            try {

                const canvas =
                    document.createElement("canvas");

                canvas.width = img.width;
                canvas.height = img.height;

                const ctx =
                    canvas.getContext("2d");

                ctx.drawImage(img, 0, 0);

                const dataURL =
                    canvas.toDataURL("image/jpeg");

                resolve(dataURL);

            }
            catch (error) {

                console.error(
                    "Image conversion error:",
                    error
                );

                resolve(null);
            }
        };


        img.onerror = function () {

            resolve(null);

        };


        img.src = url;
    });
}


// ============================================================
// DOWNLOAD PDF
// ============================================================

async function downloadPDF(studentId) {

    const student =
        students.find(
            s => Number(s.id) === Number(studentId)
        );

    if (!student) {

        showToast(
            "Student record not found.",
            "error"
        );

        return;
    }


    if (
        !window.jspdf ||
        !window.jspdf.jsPDF
    ) {

        showToast(
            "jsPDF library failed to load. Please check internet connection.",
            "error"
        );

        return;
    }


    const { jsPDF } =
        window.jspdf;


    const doc = new jsPDF({

        orientation: "p",
        unit: "mm",
        format: "a4"

    });


    // ========================================================
    // PAGE BORDER
    // ========================================================

    doc.setDrawColor(
        30,
        58,
        138
    );

    doc.setLineWidth(0.8);

    doc.rect(
        6,
        6,
        198,
        285
    );


    doc.setDrawColor(
        203,
        213,
        225
    );

    doc.setLineWidth(0.3);

    doc.rect(
        7.5,
        7.5,
        195,
        282
    );


    // ========================================================
    // HEADER
    // ========================================================

    doc.setFillColor(
        30,
        58,
        138
    );

    doc.rect(
        8,
        8,
        194,
        28,
        "F"
    );


    doc.setFillColor(
        255,
        255,
        255
    );

    doc.circle(
        20,
        22,
        9,
        "F"
    );


    doc.setFontSize(14);

    doc.setTextColor(
        30,
        58,
        138
    );

    doc.setFont(
        "helvetica",
        "bold"
    );

    doc.text(
        "Z",
        18.5,
        26.5
    );


    doc.setTextColor(
        255,
        255,
        255
    );

    doc.setFontSize(16);

    doc.setFont(
        "helvetica",
        "bold"
    );

    doc.text(
        "ZEAL COLLEGE OF ENGINEERING",
        34,
        19
    );


    doc.setFontSize(10);

    doc.setFont(
        "helvetica",
        "normal"
    );

    doc.text(
        "Online Admission System & Student Record",
        34,
        26
    );


    // ========================================================
    // APPLICATION INFO
    // ========================================================

    doc.setFillColor(
        241,
        245,
        249
    );

    doc.rect(
        8,
        36,
        194,
        10,
        "F"
    );


    doc.setFontSize(9);

    doc.setFont(
        "helvetica",
        "bold"
    );

    doc.setTextColor(
        30,
        58,
        138
    );

    doc.text(
        `Application ID: #${student.id}`,
        12,
        42.5
    );


    doc.setFont(
        "helvetica",
        "normal"
    );

    doc.setTextColor(
        71,
        85,
        105
    );

    doc.text(
        `Date of Application: ${student.created_at ||
        new Date().toISOString().slice(0, 10)
        }`,
        130,
        42.5
    );


    // ========================================================
    // PASSPORT PHOTO
    // ========================================================

    let photoLoaded = false;

    if (student.photo) {

        const photoUrl =
            `/uploads/${student.photo}`;

        const photoDataUrl =
            await getImageDataUrl(photoUrl);

        if (photoDataUrl) {

            try {

                doc.setDrawColor(
                    30,
                    58,
                    138
                );

                doc.setLineWidth(0.5);

                doc.rect(
                    162,
                    50,
                    30,
                    36
                );

                doc.addImage(
                    photoDataUrl,
                    "JPEG",
                    162.5,
                    50.5,
                    29,
                    35
                );

                photoLoaded = true;

            }
            catch (error) {

                photoLoaded = false;

            }
        }
    }


    if (!photoLoaded) {

        doc.setDrawColor(
            148,
            163,
            184
        );

        doc.setLineWidth(0.4);

        doc.rect(
            162,
            50,
            30,
            36
        );

        doc.setFillColor(
            248,
            250,
            252
        );

        doc.rect(
            162.5,
            50.5,
            29,
            35,
            "F"
        );

        doc.setFontSize(8);

        doc.setTextColor(
            148,
            163,
            184
        );

        doc.setFont(
            "helvetica",
            "normal"
        );

        doc.text(
            "PASSPORT",
            170,
            66
        );

        doc.text(
            "PHOTO",
            173,
            71
        );
    }


    // ========================================================
    // SECTION RENDERER
    // ========================================================

    let y = 50;

    function renderSection(
        title,
        data,
        customWidth = 148
    ) {

        doc.setFillColor(
            30,
            58,
            138
        );

        doc.rect(
            10,
            y,
            customWidth,
            6.5,
            "F"
        );


        doc.setFontSize(9);

        doc.setFont(
            "helvetica",
            "bold"
        );

        doc.setTextColor(
            255,
            255,
            255
        );

        doc.text(
            title,
            13,
            y + 4.5
        );


        y += 9.5;


        doc.setFontSize(8.5);

        doc.setTextColor(
            51,
            65,
            85
        );


        for (
            let i = 0;
            i < data.length;
            i += 2
        ) {

            const item1 = data[i];
            const item2 = data[i + 1];


            if (item1 && item1[0]) {

                doc.setFont(
                    "helvetica",
                    "bold"
                );

                doc.text(
                    `${item1[0]}:`,
                    12,
                    y
                );

                doc.setFont(
                    "helvetica",
                    "normal"
                );

                const val1 =
                    String(
                        item1[1] || "-"
                    );

                doc.text(
                    val1,
                    44,
                    y
                );
            }


            if (item2 && item2[0]) {

                doc.setFont(
                    "helvetica",
                    "bold"
                );

                doc.text(
                    `${item2[0]}:`,
                    82,
                    y
                );

                doc.setFont(
                    "helvetica",
                    "normal"
                );

                const val2 =
                    String(
                        item2[1] || "-"
                    );

                doc.text(
                    val2,
                    114,
                    y
                );
            }


            y += 5.5;
        }


        y += 3;
    }


    // ========================================================
    // PERSONAL
    // ========================================================

    renderSection(
        "1. PERSONAL INFORMATION",
        [
            ["Full Name", student.fullName],
            ["Father's Name", student.fatherName],
            ["Mother's Name", student.motherName],
            ["Date of Birth", student.dob],
            ["Gender", student.gender],
            ["Blood Group", student.bloodGroup]
        ],
        148
    );


    y = Math.max(y, 90);


    // ========================================================
    // CONTACT
    // ========================================================

    renderSection(
        "2. CONTACT INFORMATION",
        [
            ["Mobile Number", student.mobile],
            ["Alt Mobile", student.altMobile || "N/A"],
            ["Email Address", student.email],
            ["Aadhaar Number", student.aadhaar],
            ["City", student.city],
            ["State", student.state],
            ["Pincode", student.pincode],
            ["Nationality", student.nationality],
            ["Address", student.address],
            ["", ""]
        ],
        190
    );


    // ========================================================
    // ACADEMIC
    // ========================================================

    renderSection(
        "3. ACADEMIC INFORMATION",
        [
            ["10th Board", student.board10],
            ["10th Percentage", `${student.percentage10}%`],
            ["12th Board", student.board12],
            ["12th Percentage", `${student.percentage12}%`],
            ["Entrance Exam", student.entranceExam],
            ["Entrance Score", student.entranceScore]
        ],
        190
    );


    // ========================================================
    // COURSE
    // ========================================================

    renderSection(
        "4. COURSE INFORMATION",
        [
            ["Department", student.department],
            ["Admission Type", student.admissionType]
        ],
        190
    );


    // ========================================================
    // DOCUMENT CHECKLIST
    // ========================================================

    doc.setFillColor(
        30,
        58,
        138
    );

    doc.rect(
        10,
        y,
        190,
        6.5,
        "F"
    );


    doc.setFontSize(9);

    doc.setFont(
        "helvetica",
        "bold"
    );

    doc.setTextColor(
        255,
        255,
        255
    );

    doc.text(
        "5. UPLOADED DOCUMENTS CHECKLIST",
        13,
        y + 4.5
    );


    y += 9.5;

    doc.setFontSize(8.5);


    const docItems = [

        ["Passport Photo", student.photo],

        ["10th Marksheet", student.marksheet10],

        ["12th Marksheet", student.marksheet12],

        ["Leaving Certificate", student.leavingCertificate]

    ];


    for (
        let i = 0;
        i < docItems.length;
        i += 2
    ) {

        const item1 =
            docItems[i];

        const item2 =
            docItems[i + 1];


        if (item1) {

            const status1 =
                item1[1]
                    ? "[ YES ] Uploaded"
                    : "[ NO ] Not Uploaded";


            doc.setFont(
                "helvetica",
                "bold"
            );

            doc.setTextColor(
                item1[1] ? 5 : 220,
                item1[1] ? 150 : 38,
                item1[1] ? 105 : 38
            );


            doc.text(
                `${item1[0]}:`,
                12,
                y
            );


            doc.setFont(
                "helvetica",
                "normal"
            );


            doc.text(
                status1,
                48,
                y
            );
        }


        if (item2) {

            const status2 =
                item2[1]
                    ? "[ YES ] Uploaded"
                    : "[ NO ] Not Uploaded";


            doc.setFont(
                "helvetica",
                "bold"
            );


            doc.setTextColor(
                item2[1] ? 5 : 220,
                item2[1] ? 150 : 38,
                item2[1] ? 38 : 38
            );


            doc.text(
                `${item2[0]}:`,
                104,
                y
            );


            doc.setFont(
                "helvetica",
                "normal"
            );


            doc.text(
                status2,
                140,
                y
            );
        }


        y += 5.5;
    }


    y += 4;


    // ========================================================
    // DECLARATION
    // ========================================================

    doc.setDrawColor(
        203,
        213,
        225
    );

    doc.setFillColor(
        248,
        250,
        252
    );


    doc.rect(
        10,
        y,
        190,
        15,
        "F"
    );


    doc.setFontSize(8);

    doc.setFont(
        "helvetica",
        "bold"
    );

    doc.setTextColor(
        30,
        58,
        138
    );


    doc.text(
        "DECLARATION:",
        13,
        y + 4.5
    );


    doc.setFont(
        "helvetica",
        "normal"
    );

    doc.setTextColor(
        71,
        85,
        105
    );


    doc.text(
        "I hereby declare that all information provided in this admission form is true, correct, and complete to the best of my knowledge.",
        13,
        y + 8.5
    );


    doc.text(
        "This official document is generated automatically by the Zeal College Admission Management Portal.",
        13,
        y + 12.5
    );


    y += 26;


    // ========================================================
    // SIGNATURE
    // ========================================================

    doc.setDrawColor(
        71,
        85,
        105
    );

    doc.setLineWidth(0.4);


    doc.line(
        20,
        y,
        75,
        y
    );


    doc.line(
        135,
        y,
        190,
        y
    );


    doc.setFontSize(9);

    doc.setFont(
        "helvetica",
        "bold"
    );

    doc.setTextColor(
        30,
        58,
        138
    );


    doc.text(
        "Student Signature",
        32,
        y + 5
    );


    doc.text(
        "Admission Officer",
        148,
        y + 5
    );


    // ========================================================
    // FOOTER
    // ========================================================

    doc.setFontSize(8);

    doc.setFont(
        "helvetica",
        "italic"
    );

    doc.setTextColor(
        148,
        163,
        184
    );


    doc.text(
        "Page 1 of 1",
        12,
        286
    );


    doc.text(
        "Zeal College Admission System - Official Record",
        105,
        286,
        {
            align: "center"
        }
    );


    // ========================================================
    // SAVE PDF
    // ========================================================

    const safeName =
        (student.fullName || "Student")
            .trim()
            .replace(/\s+/g, "_");


    const fileName =
        `Admission_${safeName}.pdf`;


    doc.save(fileName);


    showToast(
        `Downloaded ${fileName}`,
        "success"
    );
}


// Global Chart.js Instances
let deptChartInstance = null;
let genderChartInstance = null;
let monthlyChartInstance = null;
let admissionTypeChartInstance = null;

// ============================================================
// UPDATE DASHBOARD (ENTERPRISE ERP ANALYTICS)
// ============================================================

function updateDashboard() {
    // 1. Dynamic Greeting & Current Date
    updateDashboardHeaderTime();

    fetch("/api/dashboard")
        .then(res => {
            if (!res.ok) {
                throw new Error("Dashboard API returned status " + res.status);
            }
            return res.json();
        })
        .then(stats => {
            console.log("Dashboard stats received:", stats);

            // ==================================================
            // 1. PRIMARY KPI TILES (TOP 6 CARDS)
            // ==================================================
            const totalCount = document.getElementById("totalCount");
            const monthCount = document.getElementById("monthCount");
            const dashTodayAttRate = document.getElementById("dashTodayAttRate");
            const dashTodayAttBar = document.getElementById("dashTodayAttBar");
            const dashPendingFees = document.getElementById("dashPendingFees");
            const dashPendingFeesBar = document.getElementById("dashPendingFeesBar");
            const dashPendingApps = document.getElementById("dashPendingApps");
            const dashPendingAppsBar = document.getElementById("dashPendingAppsBar");
            const totalDeptsCount = document.getElementById("totalDeptsCount");

            if (totalCount) totalCount.textContent = stats.total || 0;
            if (monthCount) monthCount.textContent = stats.month_admissions || stats.total || 0;

            const attRate = stats.attendance_summary ? stats.attendance_summary.attendance_rate : 100.0;
            if (dashTodayAttRate) dashTodayAttRate.textContent = `${attRate}%`;
            if (dashTodayAttBar) dashTodayAttBar.style.width = `${Math.min(100, Math.max(0, attRate))}%`;

            const pendingFeesNum = Number(stats.total_pending_fees || 0);
            if (dashPendingFees) dashPendingFees.textContent = `₹ ${pendingFeesNum.toLocaleString("en-IN")}`;
            if (dashPendingFeesBar) {
                const totalExp = Number(stats.total_fees_expected || 1);
                const pendPct = Math.min(100, Math.round((pendingFeesNum / totalExp) * 100));
                dashPendingFeesBar.style.width = `${pendPct}%`;
            }

            const pendingAppsCount = (stats.pending_count || 0) + (stats.review_count || 0);
            if (dashPendingApps) dashPendingApps.textContent = pendingAppsCount;
            if (dashPendingAppsBar) {
                const totalApps = Number(stats.total || 1);
                const appPct = Math.min(100, Math.round((pendingAppsCount / totalApps) * 100));
                dashPendingAppsBar.style.width = `${appPct}%`;
            }

            if (totalDeptsCount) totalDeptsCount.textContent = stats.total_departments || 7;

            // Department Counters
            const compCount = document.getElementById("compCount");
            const itCount = document.getElementById("itCount");
            const aidsCount = document.getElementById("aidsCount");
            if (compCount) compCount.textContent = stats.comp || 0;
            if (itCount) itCount.textContent = stats.it || 0;
            if (aidsCount) aidsCount.textContent = stats.aids || 0;

            // ==================================================
            // 2. OPERATIONS & RECONCILIATIONS
            // ==================================================
            // Fee Collection
            const expFees = document.getElementById("dashTotalFeesExpected");
            const collFees = document.getElementById("dashTotalFeesCollected");
            const pendFees = document.getElementById("dashTotalFeesPending");
            const feeRateTxt = document.getElementById("dashFeeRateText");
            const feeRateBar = document.getElementById("dashFeeRateBar");

            const totalExpected = Number(stats.total_fees_expected || 0);
            const totalCollected = Number(stats.total_fees_collected || 0);
            const feeRate = stats.fee_collection_rate !== undefined ? stats.fee_collection_rate : (totalExpected > 0 ? Math.round((totalCollected / totalExpected) * 100) : 0);

            if (expFees) expFees.textContent = `₹ ${totalExpected.toLocaleString("en-IN")}`;
            if (collFees) collFees.textContent = `₹ ${totalCollected.toLocaleString("en-IN")}`;
            if (pendFees) pendFees.textContent = `₹ ${pendingFeesNum.toLocaleString("en-IN")}`;
            if (feeRateTxt) feeRateTxt.textContent = `${feeRate}%`;
            if (feeRateBar) feeRateBar.style.width = `${Math.min(100, feeRate)}%`;

            // Attendance Overview
            const attPres = document.getElementById("dashAttPresentCount");
            const attAbs = document.getElementById("dashAttAbsentCount");
            const attMarked = document.getElementById("dashAttMarkedCount");
            const attRatePct = document.getElementById("dashAttRatePct");
            const attProgBar = document.getElementById("dashAttProgressBar");

            if (attPres) attPres.textContent = stats.attendance_summary ? stats.attendance_summary.present_today : 0;
            if (attAbs) attAbs.textContent = stats.attendance_summary ? stats.attendance_summary.absent_today : 0;
            if (attMarked) attMarked.textContent = stats.attendance_summary ? (stats.attendance_summary.marked_today || stats.total || 0) : (stats.total || 0);
            if (attRatePct) attRatePct.textContent = `${attRate}%`;
            if (attProgBar) attProgBar.style.width = `${Math.min(100, attRate)}%`;

            // Department Overview List
            renderDashboardDeptOverview(stats.department_overview || []);

            // ==================================================
            // 3. RECENT DATA TABLES
            // ==================================================
            renderDashboardRecentAdmissions(stats.recent_admissions || []);
            renderDashboardRecentPayments(stats.recent_payments || []);

            // ==================================================
            // 4. ATTENTION REQUIRED & ACTIVITY STREAM
            // ==================================================
            renderDashboardAlerts(stats.alerts || []);
            renderDashboardActivity(stats.activity || []);
            updateHeaderNotifications(stats.alerts || []);

            // ==================================================
            // 5. CHARTS (4 BALANCED MATRICES)
            // ==================================================
            if (window.Chart) {
                renderAnalyticsCharts(stats);
            }
        })
        .catch(err => {
            console.error("Error fetching dashboard analytics:", err);
            const alertBox = document.getElementById("dashAlertsList");
            if (alertBox) {
                alertBox.innerHTML = `
                    <div class="dash-alert-item danger">
                        <div class="alert-icon">⚠️</div>
                        <div class="alert-content">
                            <strong>Unable to load live dashboard analytics</strong>
                            <p>${escapeHtml(err.message || 'Please check server connection.')}</p>
                        </div>
                        <button type="button" class="btn-alert-action" onclick="updateDashboard()">Retry</button>
                    </div>
                `;
            }
        });
}

// Update Dynamic Greeting and Live Formatted Date
function updateDashboardHeaderTime() {
    const greetingEl = document.getElementById("dashGreetingText");
    const dateEl = document.getElementById("dashCurrentDate");
    const now = new Date();

    if (greetingEl) {
        const hour = now.getHours();
        if (hour < 12) {
            greetingEl.textContent = "Good morning";
        } else if (hour < 17) {
            greetingEl.textContent = "Good afternoon";
        } else {
            greetingEl.textContent = "Good evening";
        }
    }

    if (dateEl) {
        const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
        dateEl.textContent = now.toLocaleDateString('en-IN', options);
    }
}

// Render Department Overview Widget
function renderDashboardDeptOverview(deptList) {
    const container = document.getElementById("dashDeptOverviewList");
    if (!container) return;

    if (!deptList || deptList.length === 0) {
        container.innerHTML = `
            <div class="dash-dept-row-item">
                <span class="dash-d-name">Computer Engineering</span>
                <span class="dash-d-meta"><strong>0</strong> students</span>
            </div>
            <div class="dash-dept-row-item">
                <span class="dash-d-name">Information Technology</span>
                <span class="dash-d-meta"><strong>0</strong> students</span>
            </div>
            <div class="dash-dept-row-item">
                <span class="dash-d-name">AI & Data Science</span>
                <span class="dash-d-meta"><strong>0</strong> students</span>
            </div>
        `;
        return;
    }

    container.innerHTML = deptList.slice(0, 5).map(d => `
        <div class="dash-dept-row-item">
            <span class="dash-d-name">${escapeHtml(d.name)}</span>
            <span class="dash-d-meta"><strong>${d.students_count || 0}</strong> students (${d.attendance_rate || 100}% att)</span>
        </div>
    `).join("");
}

// Render Recent Admissions Mini Table
function renderDashboardRecentAdmissions(admissions) {
    const tbody = document.getElementById("dashRecentAdmissionsBody");
    if (!tbody) return;

    if (!admissions || admissions.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="table-empty-cell">No recent student admissions recorded.</td></tr>`;
        return;
    }

    tbody.innerHTML = admissions.slice(0, 6).map(s => {
        const status = s.status || "Pending Verification";
        let statusBadge = `<span class="att-status-pill pill-amber">⌛ Pending</span>`;
        if (status === "Verified") {
            statusBadge = `<span class="att-status-pill pill-green">✓ Verified</span>`;
        } else if (status === "Under Review") {
            statusBadge = `<span class="att-status-pill pill-blue">🔍 Review</span>`;
        } else if (status === "Rejected") {
            statusBadge = `<span class="att-status-pill pill-red">✕ Rejected</span>`;
        }

        const initials = (s.fullName || "Student").split(" ").map(w => w[0]).slice(0, 2).join("").toUpperCase();

        return `
            <tr>
                <td>
                    <div class="dash-student-cell">
                        <div class="dash-avatar-circle" style="background: linear-gradient(135deg, #2563EB, #4F46E5);">${initials}</div>
                        <strong>${escapeHtml(s.fullName)}</strong>
                    </div>
                </td>
                <td><code class="dash-id-code">#${s.id}</code></td>
                <td><span class="dash-dept-pill">${escapeHtml(s.department || '-')}</span></td>
                <td><small style="color: #64748b;">${escapeHtml(s.created_at || 'Today')}</small></td>
                <td>${statusBadge}</td>
            </tr>
        `;
    }).join("");
}

// Render Recent Payments Mini Table
function renderDashboardRecentPayments(payments) {
    const tbody = document.getElementById("dashRecentPaymentsBody");
    if (!tbody) return;

    if (!payments || payments.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="table-empty-cell">No fee payment receipts recorded yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = payments.slice(0, 6).map(p => {
        const amount = Number(p.amount || 0);
        return `
            <tr>
                <td><strong>${escapeHtml(p.student_name || 'Student')}</strong></td>
                <td><code class="dash-id-code">${escapeHtml(p.transaction_id || `PAY-${p.id}`)}</code></td>
                <td><strong style="color: #059669;">₹ ${amount.toLocaleString("en-IN")}</strong></td>
                <td><span class="dash-dept-pill">${escapeHtml(p.payment_method || 'UPI')}</span></td>
                <td><span class="att-status-pill pill-green">✓ Paid</span></td>
            </tr>
        `;
    }).join("");
}

// Render Attention Required Alerts
function renderDashboardAlerts(alerts) {
    const container = document.getElementById("dashAlertsList");
    if (!container) return;

    if (!alerts || alerts.length === 0) {
        container.innerHTML = `
            <div class="dash-empty-alert-state">
                <span class="empty-check">✓</span> Everything is up to date and in academic compliance.
            </div>
        `;
        return;
    }

    container.innerHTML = alerts.map(a => {
        const typeClass = a.type || "warning";
        const icon = typeClass === "danger" ? "🚨" : (typeClass === "info" ? "💳" : "⚠️");
        return `
            <div class="dash-alert-item ${typeClass}">
                <div class="alert-icon">${icon}</div>
                <div class="alert-content">
                    <strong>${escapeHtml(a.title)} (${a.count || 0})</strong>
                    <p>${escapeHtml(a.description)}</p>
                </div>
                <button type="button" class="btn-alert-action" onclick="switchAdminSection('${a.action_target || 'pane-dashboard'}', null, '${a.title}')">
                    ${escapeHtml(a.action_text || 'Review')}
                </button>
            </div>
        `;
    }).join("");
}

// Render Recent Administrative Activity Timeline
function renderDashboardActivity(activity) {
    const container = document.getElementById("dashActivityTimeline");
    if (!container) return;

    if (!activity || activity.length === 0) {
        container.innerHTML = `<div class="dash-activity-empty">No institutional activity logged yet.</div>`;
        return;
    }

    container.innerHTML = activity.map(item => `
        <div class="activity-timeline-item">
            <div class="activity-icon-bullet" style="background: ${item.color || '#2563EB'};">
                ${item.icon || '📌'}
            </div>
            <div class="activity-details">
                <strong>${escapeHtml(item.title)}</strong>
                <p>${escapeHtml(item.description)}</p>
                <small>${escapeHtml(item.timestamp || 'Recently')}</small>
            </div>
        </div>
    `).join("");
}

// Header Notification Menu Handling
function toggleNotificationMenu(force) {
    const menu = document.getElementById("headerNotifDropdown");
    if (!menu) return;

    if (force === true) {
        menu.style.display = "block";
    } else if (force === false) {
        menu.style.display = "none";
    } else {
        menu.style.display = menu.style.display === "none" ? "block" : "none";
    }
}

function updateHeaderNotifications(alerts) {
    const badge = document.getElementById("headerNotifCount");
    const container = document.getElementById("notifDropdownBody");
    if (!badge) return;

    const count = (alerts || []).length;
    badge.textContent = count;
    badge.style.display = count > 0 ? "inline-flex" : "none";

    if (container) {
        if (!alerts || alerts.length === 0) {
            container.innerHTML = `<div class="notif-empty-state">No unread notifications</div>`;
        } else {
            container.innerHTML = alerts.map(a => `
                <div class="notif-item" onclick="toggleNotificationMenu(false); switchAdminSection('${a.action_target || 'pane-dashboard'}', null, '${a.title}')">
                    <span class="notif-item-icon">🔔</span>
                    <div class="notif-item-text">
                        <strong>${escapeHtml(a.title)}</strong>
                        <small>${escapeHtml(a.description)}</small>
                    </div>
                </div>
            `).join("");
        }
    }
}

function markAllNotificationsRead() {
    const badge = document.getElementById("headerNotifCount");
    const container = document.getElementById("notifDropdownBody");
    if (badge) {
        badge.textContent = "0";
        badge.style.display = "none";
    }
    if (container) {
        container.innerHTML = `<div class="notif-empty-state">All notifications marked as read ✓</div>`;
    }
    showToast("All notifications marked as read.", "success");
}

// Executive PDF Report Export
function exportDashboardExecutiveReport() {
    window.print();
}

// ============================================================
// RENDER ANALYTICS CHARTS (PROFESSIONAL RESPONSIVE PALETTE)
// ============================================================

function renderAnalyticsCharts(stats) {
    // 1. MONTHLY ADMISSIONS TREND (SMOOTH GRADIENT LINE)
    const monthlyCtx = document.getElementById("monthlyChart");
    if (monthlyCtx) {
        const trends = stats.monthly_trends || [];
        const monthLabels = trends.map(t => t.month);
        const monthData = trends.map(t => t.count);

        if (monthlyChartInstance) {
            monthlyChartInstance.destroy();
        }

        monthlyChartInstance = new Chart(monthlyCtx, {
            type: "line",
            data: {
                labels: monthLabels.length ? monthLabels : ["Mar 2026", "Apr 2026", "May 2026", "Jun 2026", "Jul 2026", "Aug 2026"],
                datasets: [{
                    label: "Admissions",
                    data: monthData.length ? monthData : [0, 0, 0, 0, 0, stats.total || 0],
                    borderColor: "#2563EB",
                    backgroundColor: "rgba(37, 99, 235, 0.08)",
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: "#2563EB",
                    pointBorderColor: "#FFFFFF",
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: "#172033",
                        titleFont: { family: "'Plus Jakarta Sans', sans-serif", weight: "700" },
                        bodyFont: { family: "'Inter', sans-serif" },
                        padding: 10,
                        cornerRadius: 6
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: "#F1F5F9" },
                        ticks: { font: { family: "'Inter', sans-serif", size: 11 }, precision: 0 }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { font: { family: "'Inter', sans-serif", size: 11 } }
                    }
                }
            }
        });
    }

    // 2. DEPARTMENT DISTRIBUTION (ENTERPRISE BAR CHART)
    const deptCtx = document.getElementById("deptChart");
    if (deptCtx) {
        const deptLabels = Object.keys(stats.dept_stats || {});
        const deptData = Object.values(stats.dept_stats || {});

        if (deptChartInstance) {
            deptChartInstance.destroy();
        }

        deptChartInstance = new Chart(deptCtx, {
            type: "bar",
            data: {
                labels: deptLabels.length ? deptLabels.map(l => l.replace(" Engineering", "").replace("Artificial Intelligence & Data Science", "AI & DS")) : ["Computer", "IT", "AI & DS", "E&TC", "Mechanical", "Civil", "Electrical"],
                datasets: [{
                    label: "Enrolled Students",
                    data: deptData.length ? deptData : [0, 0, 0, 0, 0, 0, 0],
                    backgroundColor: [
                        "#2563EB", // Computer
                        "#0891B2", // IT
                        "#7C3AED", // AI&DS
                        "#059669", // ENTC
                        "#EA580C", // Mech
                        "#DC2626", // Civil
                        "#D97706"  // Elec
                    ],
                    borderRadius: 6,
                    barThickness: 22
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: "#172033",
                        padding: 10,
                        cornerRadius: 6
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: "#F1F5F9" },
                        ticks: { font: { family: "'Inter', sans-serif", size: 11 }, precision: 0 }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { font: { family: "'Inter', sans-serif", size: 11 } }
                    }
                }
            }
        });
    }

    // 3. ADMISSION VERIFICATION STATUS DOUGHNUT
    const typeCtx = document.getElementById("admissionTypeChart");
    if (typeCtx) {
        const sStats = stats.status_stats || {
            "Verified": 0,
            "Pending Verification": 0,
            "Under Review": 0,
            "Rejected": 0
        };

        if (admissionTypeChartInstance) {
            admissionTypeChartInstance.destroy();
        }

        admissionTypeChartInstance = new Chart(typeCtx, {
            type: "doughnut",
            data: {
                labels: ["Verified", "Pending Verification", "Under Review", "Rejected"],
                datasets: [{
                    data: [
                        sStats["Verified"] || 0,
                        sStats["Pending Verification"] || 0,
                        sStats["Under Review"] || 0,
                        sStats["Rejected"] || 0
                    ],
                    backgroundColor: [
                        "#059669", // Verified (Green)
                        "#D97706", // Pending (Amber)
                        "#2563EB", // Under Review (Blue)
                        "#DC2626"  // Rejected (Red)
                    ],
                    borderWidth: 2,
                    borderColor: "#FFFFFF"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "68%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            font: { family: "'Inter', sans-serif", size: 11, weight: "600" },
                            padding: 10,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    // 4. GENDER RATIO DOUGHNUT
    const genderCtx = document.getElementById("genderChart");
    if (genderCtx) {
        const gStats = stats.gender_stats || { Male: 0, Female: 0, Other: 0 };

        if (genderChartInstance) {
            genderChartInstance.destroy();
        }

        genderChartInstance = new Chart(genderCtx, {
            type: "doughnut",
            data: {
                labels: ["Male", "Female", "Other"],
                datasets: [{
                    data: [
                        gStats.Male || 0,
                        gStats.Female || 0,
                        gStats.Other || 0
                    ],
                    backgroundColor: [
                        "#2563EB", // Male
                        "#EC4899", // Female
                        "#64748B"  // Other
                    ],
                    borderWidth: 2,
                    borderColor: "#FFFFFF"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "68%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            font: { family: "'Inter', sans-serif", size: 11, weight: "600" },
                            padding: 10,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }
}


// ============================================================
// TOAST NOTIFICATIONS
// ============================================================

const toastContainer = document.getElementById("toastContainer");

function showToast(message, type = "success") {
    const container = toastContainer || document.getElementById("toastContainer");
    if (!container) {
        console.log(`[Toast ${type}]:`, message);
        return;
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    const icon = type === "success" ? "✅" : "⚠️";

    toast.innerHTML = `
        <span>${icon}</span>
        <span>${escapeHtml(message)}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("toast-fade-out");
        setTimeout(() => {
            if (toast.parentElement) {
                toast.parentElement.removeChild(toast);
            }
        }, 300);
    }, 3500);
}


// ============================================================
// DELETE STUDENT SYSTEM
// ============================================================

let pendingDeleteStudentId = null;

function getDeleteElements() {
    return {
        modal: document.getElementById("deleteModal"),
        message: document.getElementById("deleteModalMessage"),
        cancelButton: document.getElementById("cancelDeleteBtn"),
        confirmButton: document.getElementById("confirmDeleteBtn")
    };
}

function deleteStudent(studentId) {
    const id = Number(studentId);
    console.log("Delete button clicked. Student ID:", id);

    if (!Number.isInteger(id) || id <= 0) {
        showToast("Invalid student ID.", "error");
        return;
    }

    // Find student from currently loaded students
    const student = Array.isArray(students)
        ? students.find(s => Number(s.id) === id)
        : null;

    const {
        modal,
        message,
        confirmButton
    } = getDeleteElements();

    if (!modal) {
        alert("Delete confirmation modal was not found.");
        console.error("Element #deleteModal not found.");
        return;
    }

    // Store selected student ID
    pendingDeleteStudentId = id;

    // Show student name
    if (message) {
        const studentName = student && student.fullName ? `"${student.fullName}"` : `record #${id}`;
        message.textContent = `Are you sure you want to delete the admission record for ${studentName}? This action cannot be undone.`;
    }

    // Show modal
    modal.style.display = "flex";
    modal.classList.add("show");

    // Reset confirm button
    if (confirmButton) {
        confirmButton.disabled = false;
        confirmButton.textContent = "Delete";
    }

    console.log("Delete confirmation opened for student:", id);
}

function hideDeleteModal() {
    const { modal } = getDeleteElements();
    pendingDeleteStudentId = null;

    if (modal) {
        modal.style.display = "none";
        modal.classList.remove("show");
    }

    console.log("Delete modal closed.");
}

function cancelStudentDelete() {
    console.log("Delete cancelled.");
    hideDeleteModal();
}

async function confirmStudentDelete() {
    const id = pendingDeleteStudentId;
    console.log("Confirm delete clicked. Student ID:", id);

    if (!id) {
        showToast("No student selected for deletion.", "error");
        return;
    }

    const { confirmButton } = getDeleteElements();

    try {
        if (confirmButton) {
            confirmButton.disabled = true;
            confirmButton.textContent = "Deleting...";
        }

        console.log(`Sending DELETE request to /api/students/${id}`);

        const response = await fetch(`/api/students/${id}`, {
            method: "DELETE",
            headers: {
                "Accept": "application/json"
            }
        });

        console.log("DELETE response status:", response.status);

        let data = {};
        try {
            data = await response.json();
        } catch (jsonError) {
            console.warn("Server did not return JSON.");
        }

        console.log("DELETE response data:", data);

        if (!response.ok) {
            throw new Error(data.error || data.message || `Delete failed. HTTP ${response.status}`);
        }

        // Close modal
        hideDeleteModal();

        // Show toast feedback
        showToast(data.message || "Student deleted successfully.", "success");

        // Remove student from local array
        if (Array.isArray(students)) {
            students = students.filter(student => Number(student.id) !== Number(id));
        }

        // Refresh student table
        if (typeof renderStudents === "function") {
            renderStudents();
        }

        // Refresh dashboard
        if (typeof updateDashboard === "function") {
            updateDashboard();
        }

        // Reload data from backend
        if (typeof fetchStudents === "function") {
            await fetchStudents();
        }

        console.log("Student deleted successfully:", id);

    } catch (error) {
        console.error("DELETE STUDENT ERROR:", error);
        showToast("Unable to delete student: " + error.message, "error");
    } finally {
        if (confirmButton) {
            confirmButton.disabled = false;
            confirmButton.textContent = "Delete";
        }
    }
}

function initializeDeleteSystem() {
    const {
        modal,
        cancelButton,
        confirmButton
    } = getDeleteElements();

    if (!modal) {
        console.warn("Delete modal not found.");
        return;
    }

    if (cancelButton) {
        cancelButton.onclick = function (event) {
            event.preventDefault();
            event.stopPropagation();
            cancelStudentDelete();
        };
    }

    if (confirmButton) {
        confirmButton.onclick = function (event) {
            event.preventDefault();
            event.stopPropagation();
            confirmStudentDelete();
        };
    }

    modal.onclick = function (event) {
        if (event.target === modal) {
            hideDeleteModal();
        }
    };

    console.log("Delete system initialized successfully.");
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeDeleteSystem);
} else {
    initializeDeleteSystem();
}


// ============================================================
// VIEW MODAL CLOSE & GLOBAL EVENT HANDLERS
// ============================================================

function hideModal() {
    if (viewModal) {
        viewModal.style.display = "none";
    }
}

if (closeModal) {
    closeModal.addEventListener("click", hideModal);
}

if (closeModalFooter) {
    closeModalFooter.addEventListener("click", hideModal);
}

window.addEventListener("click", function (event) {
    if (viewModal && event.target === viewModal) {
        hideModal();
    }
    const delModal = document.getElementById("deleteModal");
    if (delModal && event.target === delModal) {
        hideDeleteModal();
    }
});

window.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") {
        return;
    }
    if (viewModal && viewModal.style.display === "flex") {
        hideModal();
    }
    const delModal = document.getElementById("deleteModal");
    if (delModal && delModal.style.display === "flex") {
        hideDeleteModal();
    }
});


// ============================================================
// EXPORT TO EXCEL / CSV
// ============================================================

function exportToExcel() {

    if (students.length === 0) {

        alert(
            "No student records available to export!"
        );

        return;
    }


    const headers = [

        "Sr No",
        "Full Name",
        "Father's Name",
        "Mother's Name",
        "DOB",
        "Gender",
        "Blood Group",
        "Mobile",
        "Alt Mobile",
        "Email",
        "Aadhaar No",
        "Address",
        "City",
        "State",
        "Pincode",
        "Nationality",
        "10th Board",
        "10th %",
        "12th Board",
        "12th %",
        "Entrance Exam",
        "Entrance Score",
        "Department",
        "Admission Type"

    ];


    let csvContent =
        "\uFEFF";


    csvContent +=
        headers
            .map(
                h =>
                    `"${h.replace(
                        /"/g,
                        '""'
                    )}"`
            )
            .join(",") +
        "\r\n";


    students.forEach(
        (student, index) => {

            const row = [

                index + 1,

                student.fullName || "",

                student.fatherName || "",

                student.motherName || "",

                student.dob || "",

                student.gender || "",

                student.bloodGroup || "",

                student.mobile || "",

                student.altMobile || "",

                student.email || "",

                student.aadhaar || "",

                student.address || "",

                student.city || "",

                student.state || "",

                student.pincode || "",

                student.nationality || "",

                student.board10 || "",

                student.percentage10 || "",

                student.board12 || "",

                student.percentage12 || "",

                student.entranceExam || "",

                student.entranceScore || "",

                student.department || "",

                student.admissionType || ""

            ];


            csvContent +=

                row
                    .map(
                        val =>
                            `"${String(val)
                                .replace(
                                    /"/g,
                                    '""'
                                )}"`
                    )
                    .join(",") +
                "\r\n";

        }
    );


    const blob =
        new Blob(
            [csvContent],
            {
                type:
                    "text/csv;charset=utf-8;"
            }
        );


    const url =
        URL.createObjectURL(
            blob
        );


    const link =
        document.createElement(
            "a"
        );


    link.setAttribute(
        "href",
        url
    );


    link.setAttribute(
        "download",
        `Student_Admission_Records_${new Date()
            .toISOString()
            .slice(0, 10)
        }.csv`
    );


    document.body.appendChild(
        link
    );


    link.click();


    document.body.removeChild(
        link
    );


    URL.revokeObjectURL(
        url
    );
}


// ============================================================
// INITIAL API LOAD
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {
        checkAdminAuth();
        fetchStudents();
        initAttendanceModule();
    }
);


// ============================================================
// ADMIN LOGOUT
// ============================================================

function logoutAdmin() {

    fetch(
        "/api/logout",
        {
            method: "POST"
        }
    )

        .then(res =>
            res.json()
        )

        .then(() => {

            window.location.href =
                "login.html";

        })

        .catch(err => {

            console.error(
                "Logout error:",
                err
            );


            window.location.href =
                "login.html";

        });
}

// ============================================================
// MODAL FEE MANAGEMENT FUNCTIONS
// ============================================================

let currentModalStudentName = "Student";

function loadStudentModalFees(studentId, studentName = "Student") {
    currentModalStudentName = studentName;
    fetch(`/api/students/${studentId}/fees`)
        .then(res => {
            if (!res.ok) throw new Error("Failed to load student fee summary");
            return res.json();
        })
        .then(feeData => {
            renderModalFeeDetails(feeData);
        })
        .catch(err => {
            console.error("Error loading modal fees:", err);
            const historyBody = document.getElementById("mPaymentHistoryBody");
            if (historyBody) {
                historyBody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: #ef4444; padding: 14px;">Unable to load fee summary.</td></tr>`;
            }
        });
}

function renderModalFeeDetails(feeData) {
    const totalEl = document.getElementById("mTotalFee");
    const paidEl = document.getElementById("mPaidAmount");
    const pendEl = document.getElementById("mPendingAmount");
    const statusTextEl = document.getElementById("mFeeStatusText");
    const statusBadgeEl = document.getElementById("modalFeeStatusBadge");
    const pillsContainer = document.getElementById("mFeeBreakdownPills");
    const historyBody = document.getElementById("mPaymentHistoryBody");

    const total = Number(feeData.total_fee || 0);
    const paid = Number(feeData.paid_amount || 0);
    const pending = Number(feeData.pending_amount || 0);
    const status = feeData.payment_status || "Pending";

    if (totalEl) totalEl.textContent = `₹ ${total.toLocaleString("en-IN")}`;
    if (paidEl) paidEl.textContent = `₹ ${paid.toLocaleString("en-IN")}`;
    if (pendEl) pendEl.textContent = `₹ ${pending.toLocaleString("en-IN")}`;
    if (statusTextEl) statusTextEl.textContent = status;

    if (statusBadgeEl) {
        if (status === "Paid") {
            statusBadgeEl.className = "fee-badge fee-badge-paid";
            statusBadgeEl.innerHTML = "🟢 Paid";
        } else if (status === "Partially Paid") {
            statusBadgeEl.className = "fee-badge fee-badge-partial";
            statusBadgeEl.innerHTML = "🟡 Partially Paid";
        } else {
            statusBadgeEl.className = "fee-badge fee-badge-pending";
            statusBadgeEl.innerHTML = "🔴 Pending";
        }
    }

    if (pillsContainer && feeData.fee_breakdown) {
        pillsContainer.innerHTML = Object.entries(feeData.fee_breakdown).map(([k, v]) => `
            <span style="background: white; border: 1px solid #cbd5e1; border-radius: 6px; padding: 4px 8px; font-size: 11px;">
                <span style="color: #64748b;">${k}:</span> <strong style="color: #0f172a;">₹ ${Number(v).toLocaleString("en-IN")}</strong>
            </span>
        `).join("");
    }

    if (historyBody) {
        const payments = feeData.payments || [];
        if (payments.length === 0) {
            historyBody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: #64748b; padding: 16px;">No fee payments recorded yet.</td></tr>`;
        } else {
            historyBody.innerHTML = payments.map(p => `
                <tr>
                    <td><strong>${p.payment_date || p.created_at || '-'}</strong></td>
                    <td>${p.fee_type || 'Tuition Fee'}</td>
                    <td style="font-weight: 700; color: #059669;">₹ ${Number(p.amount).toLocaleString('en-IN')}</td>
                    <td><span style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 11px;">${p.payment_method || 'UPI'}</span></td>
                    <td><code style="font-size: 11px;">${p.transaction_id || '-'}</code></td>
                    <td><span style="color: #15803d; font-weight: 600;">✓ ${p.status || 'SUCCESS'}</span></td>
                    <td><small style="color: #64748b;">${p.recorded_by || 'admin'}</small></td>
                    <td>
                        <button type="button" class="doc-action-btn btn-doc-download" onclick="downloadAdminPaymentReceipt(${JSON.stringify(p).replace(/"/g, '&quot;')}, '${escapeHtml(currentModalStudentName)}')">
                            📥 Receipt
                        </button>
                    </td>
                </tr>
            `).join("");
        }
    }
}

async function recordStudentPayment(studentId) {
    const amountInput = document.getElementById("adminPayAmount");
    const feeTypeSelect = document.getElementById("adminPayFeeType");
    const methodSelect = document.getElementById("adminPayMethod");
    const txnIdInput = document.getElementById("adminPayTxnId");
    const remarksInput = document.getElementById("adminPayRemarks");
    const submitBtn = document.getElementById("adminPaySubmitBtn");

    const amountVal = parseFloat(amountInput.value);
    if (isNaN(amountVal) || amountVal <= 0) {
        showToast("Please enter a valid payment amount greater than zero.", "error");
        amountInput.focus();
        return;
    }

    try {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = "Processing...";
        }

        const payload = {
            amount: amountVal,
            fee_type: feeTypeSelect.value,
            payment_method: methodSelect.value,
            transaction_id: txnIdInput ? txnIdInput.value.trim() : "",
            remarks: remarksInput ? remarksInput.value.trim() : ""
        };

        const response = await fetch(`/api/students/${studentId}/payments`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            credentials: "same-origin",
            body: JSON.stringify(payload)
        });

        const contentType = response.headers.get("content-type") || "";
        let data = {};
        if (contentType.includes("application/json")) {
            data = await response.json();
        } else {
            const text = await response.text();
            throw new Error(`Server returned non-JSON response: ${text.substring(0, 100)}`);
        }

        if (!response.ok) {
            throw new Error(data.error || data.message || `HTTP Error ${response.status}`);
        }

        showToast(data.message || "Payment recorded successfully!", "success");

        // Clear input form
        amountInput.value = "";
        if (txnIdInput) txnIdInput.value = "";
        if (remarksInput) remarksInput.value = "";

        // Reload modal fee card
        if (data.summary) {
            renderModalFeeDetails(data.summary);
        } else {
            loadStudentModalFees(studentId, currentModalStudentName);
        }

        // Refresh global dashboard analytics
        updateDashboard();

    } catch (err) {
        console.error("Record payment error:", err);
        showToast("Failed to record payment: " + err.message, "error");
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = "💳 Record Payment";
        }
    }
}

function downloadAdminPaymentReceipt(payment, studentName) {
    if (!payment || !payment.id) {
        showToast("Invalid payment record selected.", "error");
        return;
    }

    showToast("Downloading official fee receipt PDF...", "success");
    const link = document.createElement("a");
    link.href = `/api/payments/${payment.id}/receipt`;
    link.target = "_blank";
    link.download = `${payment.receipt_number || 'Receipt_' + payment.id}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ============================================================
// ATTENDANCE MANAGEMENT MODULE (ADMIN / FACULTY)
// ============================================================

let currentAttendanceRoster = [];

const DEPARTMENT_ICONS = {
    "Computer Engineering": "💻",
    "Information Technology": "🌐",
    "Artificial Intelligence & Data Science": "🤖",
    "Electronics & Telecommunication": "📡",
    "Mechanical Engineering": "⚙️",
    "Civil Engineering": "🏗️",
    "Electrical Engineering": "⚡"
};

function initAttendanceModule() {
    const dateInput = document.getElementById("attDateFilter");
    if (dateInput && !dateInput.value) {
        const today = new Date().toISOString().slice(0, 10);
        dateInput.value = today;
    }

    const todayDisplay = document.getElementById("attTodayDisplay");
    if (todayDisplay) {
        const now = new Date();
        const options = { day: 'numeric', month: 'short', year: 'numeric' };
        todayDisplay.textContent = now.toLocaleDateString('en-GB', options);
    }
    
    const deptSelect = document.getElementById("attDeptFilter");
    if (deptSelect && deptSelect.value) {
        selectAttendanceDepartment(deptSelect.value);
    } else {
        resetAttendanceDepartmentSelection();
    }
}

function exportAttendanceReport() {
    const deptSelect = document.getElementById("attDeptFilter");
    const department = deptSelect ? deptSelect.value : "";
    const dateInput = document.getElementById("attDateFilter");
    const dateVal = dateInput && dateInput.value ? dateInput.value : new Date().toISOString().slice(0, 10);

    if (!department) {
        showToast("Please select a department first to export attendance.", "warning");
        return;
    }

    if (!currentAttendanceRoster || currentAttendanceRoster.length === 0) {
        showToast("No student attendance data loaded to export.", "error");
        return;
    }

    // Generate CSV data for enterprise export
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += `Zeal College ERP - Daily Attendance Sheet\n`;
    csvContent += `Department: ${department}\n`;
    csvContent += `Date: ${dateVal}\n\n`;
    csvContent += `Sr,Student ID,Student Name,Department,Quota,Status,Remarks\n`;

    currentAttendanceRoster.forEach((s, idx) => {
        const statusEl = document.getElementById(`attStatus_${s.student_id}`);
        const remarksEl = document.getElementById(`attRemarks_${s.student_id}`);
        const status = statusEl ? statusEl.value : (s.status || "Present");
        const remarks = remarksEl ? remarksEl.value.replace(/,/g, ";") : (s.remarks || "");

        csvContent += `${idx + 1},${s.student_id},"${s.fullName || ''}","${s.department || ''}","${s.admissionType || 'CAP'}",${status},"${remarks}"\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Attendance_${department.replace(/\s+/g, '_')}_${dateVal}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast(`Attendance report exported as CSV!`, "success");
}

function selectAttendanceDepartment(deptName) {
    if (!deptName) {
        resetAttendanceDepartmentSelection();
        return;
    }

    const deptSelect = document.getElementById("attDeptFilter");
    if (deptSelect) deptSelect.value = deptName;

    const activeDeptTitle = document.getElementById("attActiveDeptTitle");
    if (activeDeptTitle) activeDeptTitle.textContent = deptName;

    const activeDeptIcon = document.getElementById("attActiveDeptIcon");
    if (activeDeptIcon) activeDeptIcon.textContent = DEPARTMENT_ICONS[deptName] || "🎓";

    const selectionView = document.getElementById("attDeptSelectionView");
    const activeView = document.getElementById("attDeptActiveView");

    if (selectionView) selectionView.style.display = "none";
    if (activeView) activeView.style.display = "block";

    loadAttendanceSheet();
}

function resetAttendanceDepartmentSelection() {
    const deptSelect = document.getElementById("attDeptFilter");
    if (deptSelect) deptSelect.value = "";

    const searchInput = document.getElementById("attSearchInput");
    if (searchInput) searchInput.value = "";

    currentAttendanceRoster = [];

    const selectionView = document.getElementById("attDeptSelectionView");
    const activeView = document.getElementById("attDeptActiveView");

    if (selectionView) selectionView.style.display = "block";
    if (activeView) activeView.style.display = "none";
}

function onDeptDropdownChange() {
    const deptSelect = document.getElementById("attDeptFilter");
    const deptName = deptSelect ? deptSelect.value : "";
    if (!deptName) {
        resetAttendanceDepartmentSelection();
    } else {
        selectAttendanceDepartment(deptName);
    }
}

async function loadAttendanceSheet() {
    const deptSelect = document.getElementById("attDeptFilter");
    const dateInput = document.getElementById("attDateFilter");
    const tableBody = document.getElementById("attendanceTableBody");

    if (!tableBody) return;

    const department = deptSelect ? deptSelect.value : "";
    if (!department) {
        resetAttendanceDepartmentSelection();
        return;
    }

    const dateVal = dateInput && dateInput.value ? dateInput.value : new Date().toISOString().slice(0, 10);

    tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: #64748b; padding: 16px;">Loading attendance roster for ${escapeHtml(department)}...</td></tr>`;

    try {
        const url = `/api/attendance?department=${encodeURIComponent(department)}&date=${encodeURIComponent(dateVal)}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(`Failed to load attendance (HTTP ${res.status})`);

        const data = await res.json();
        currentAttendanceRoster = data.students || [];

        renderAttendanceSheet(currentAttendanceRoster);
        updateAttendanceKpis(data);
        loadAttendanceReport(department, dateVal);

    } catch (err) {
        console.error("Error loading attendance sheet:", err);
        tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: #ef4444; padding: 16px;">Failed to load attendance sheet: ${escapeHtml(err.message)}</td></tr>`;
    }
}

function renderAttendanceSheet(students) {
    const tableBody = document.getElementById("attendanceTableBody");
    if (!tableBody) return;

    const deptSelect = document.getElementById("attDeptFilter");
    const currentDeptName = deptSelect && deptSelect.value ? deptSelect.value : "this department";

    if (!students || students.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; color: #64748b; padding: 36px 16px;">
                    <div style="font-size: 38px; margin-bottom: 10px;">📋</div>
                    <strong style="color: #1e293b; font-size: 15px; display: block;">No students enrolled in ${escapeHtml(currentDeptName)} yet.</strong>
                    <div style="font-size: 13px; color: #94a3b8; margin: 4px 0 16px 0;">Admitted students for this branch will appear here automatically.</div>
                    <button type="button" class="att-back-btn" onclick="resetAttendanceDepartmentSelection()">← Select Another Department</button>
                </td>
            </tr>
        `;
        return;
    }

    function getInitials(name) {
        if (!name) return "ST";
        const parts = name.trim().split(" ");
        if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }

    const avatarGradients = [
        "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
        "linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)",
        "linear-gradient(135deg, #059669 0%, #047857 100%)",
        "linear-gradient(135deg, #d97706 0%, #b45309 100%)",
        "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
        "linear-gradient(135deg, #ea580c 0%, #c2410c 100%)"
    ];

    tableBody.innerHTML = students.map((s, index) => {
        const isPresent = s.status === "Present";
        const statusClass = isPresent ? "att-status-present" : "att-status-absent";
        const avatarBg = avatarGradients[index % avatarGradients.length];
        const initials = getInitials(s.fullName);
        const quotaKey = (s.admissionType || 'cap').toLowerCase().replace(/[^a-z]/g, '');

        return `
            <tr id="attRow_${s.student_id}">
                <td style="font-weight: 700; color: #64748b; text-align: center;">${index + 1}</td>
                <td><code class="att-id-badge">#${s.student_id}</code></td>
                <td>
                    <div class="att-student-cell">
                        <div class="att-avatar" style="background: ${avatarBg};">${initials}</div>
                        <div class="att-student-meta">
                            <strong class="att-student-name">${escapeHtml(s.fullName)}</strong>
                            <span class="att-student-sub">${escapeHtml(s.email || s.mobile || 'Roll #' + s.student_id)}</span>
                        </div>
                    </div>
                </td>
                <td><span class="att-dept-badge">${escapeHtml(s.department || '-')}</span></td>
                <td><span class="att-quota-badge quota-${quotaKey}">${escapeHtml(s.admissionType || 'CAP')}</span></td>
                <td>
                    <select id="attStatus_${s.student_id}" class="att-status-select ${statusClass}" onchange="onStatusSelectChange(${s.student_id})" aria-label="Attendance status for ${escapeHtml(s.fullName)}">
                        <option value="Present" ${isPresent ? "selected" : ""}>✓ Present</option>
                        <option value="Absent" ${!isPresent ? "selected" : ""}>✕ Absent</option>
                    </select>
                </td>
                <td>
                    <input type="text" id="attRemarks_${s.student_id}" class="att-remarks-input" placeholder="Optional notes (e.g. Medical, On Duty)..." value="${escapeHtml(s.remarks || '')}" aria-label="Remarks for ${escapeHtml(s.fullName)}">
                </td>
            </tr>
        `;
    }).join("");
}

function onStatusSelectChange(studentId) {
    const sel = document.getElementById(`attStatus_${studentId}`);
    if (!sel) return;
    if (sel.value === "Present") {
        sel.className = "att-status-select att-status-present";
    } else {
        sel.className = "att-status-select att-status-absent";
    }
    recalcAttendanceSheetKpis();
}

function markAllAttendance(targetStatus) {
    const selects = document.querySelectorAll(".att-status-select");
    selects.forEach(sel => {
        sel.value = targetStatus;
        if (targetStatus === "Present") {
            sel.className = "att-status-select att-status-present";
        } else {
            sel.className = "att-status-select att-status-absent";
        }
    });
    recalcAttendanceSheetKpis();
    showToast(`Marked all displayed students as ${targetStatus}`, "success");
}

function applyAttendanceVisualStats(total, present, absent, rate) {
    const kpiTotal = document.getElementById("attKpiTotal");
    const kpiPresent = document.getElementById("attKpiPresent");
    const kpiAbsent = document.getElementById("attKpiAbsent");
    const kpiRate = document.getElementById("attKpiRate");
    const heroRate = document.getElementById("heroAttRate");
    const kpiPresentBar = document.getElementById("kpiPresentBar");
    const kpiAbsentBar = document.getElementById("kpiAbsentBar");
    const kpiRateBar = document.getElementById("kpiRateBar");
    const ratioPresentPct = document.getElementById("ratioPresentPct");
    const ratioAbsentPct = document.getElementById("ratioAbsentPct");
    const stackedPresentBar = document.getElementById("stackedPresentBar");
    const stackedAbsentBar = document.getElementById("stackedAbsentBar");

    if (kpiTotal) kpiTotal.textContent = total;
    if (kpiPresent) kpiPresent.textContent = present;
    if (kpiAbsent) kpiAbsent.textContent = absent;
    if (kpiRate) kpiRate.textContent = `${rate}%`;
    if (heroRate) heroRate.textContent = `${rate}%`;

    const presentPct = total > 0 ? Math.round((present / total) * 100) : 0;
    const absentPct = total > 0 ? (100 - presentPct) : 0;

    if (kpiPresentBar) kpiPresentBar.style.width = `${presentPct}%`;
    if (kpiAbsentBar) kpiAbsentBar.style.width = `${absentPct}%`;
    if (kpiRateBar) kpiRateBar.style.width = `${rate}%`;

    if (ratioPresentPct) ratioPresentPct.textContent = `${presentPct}%`;
    if (ratioAbsentPct) ratioAbsentPct.textContent = `${absentPct}%`;
    if (stackedPresentBar) stackedPresentBar.style.width = `${presentPct}%`;
    if (stackedAbsentBar) stackedAbsentBar.style.width = `${absentPct}%`;
}

function recalcAttendanceSheetKpis() {
    const selects = Array.from(document.querySelectorAll(".att-status-select"));
    const total = selects.length;
    const present = selects.filter(s => s.value === "Present").length;
    const absent = total - present;
    const rate = total > 0 ? Math.round((present / total) * 100) : 0;

    applyAttendanceVisualStats(total, present, absent, rate);
}

function updateAttendanceKpis(data) {
    const total = data.total_students || 0;
    const present = data.present_count || 0;
    const absent = data.absent_count || 0;
    const rate = data.marked_count > 0 ? Math.round((present / data.marked_count) * 100) : (total > 0 ? 100 : 0);

    applyAttendanceVisualStats(total, present, absent, rate);
}

async function loadAttendanceReport(department, dateVal) {
    const alertBox = document.getElementById("attLowAlertBox");
    const studentsList = document.getElementById("attLowStudentsList");
    if (!alertBox || !studentsList) return;

    try {
        const res = await fetch(`/api/attendance/report?department=${encodeURIComponent(department)}&date=${encodeURIComponent(dateVal)}`);
        if (!res.ok) return;

        const rep = await res.json();
        const lowStudents = rep.low_attendance_students || [];

        if (lowStudents.length > 0) {
            alertBox.style.display = "block";
            studentsList.innerHTML = lowStudents.map(s => `
                <span style="background: white; border: 1px solid #fca5a5; padding: 3px 8px; border-radius: 6px; font-weight: 600;">
                    ${escapeHtml(s.fullName)} (${s.attendance_percentage}% attendance)
                </span>
            `).join("");
        } else {
            alertBox.style.display = "none";
        }
    } catch (e) {
        console.error("Error loading attendance report:", e);
    }
}

function filterAttendanceTable() {
    const input = document.getElementById("attSearchInput");
    const filter = input ? input.value.toLowerCase().trim() : "";
    const rows = document.querySelectorAll("#attendanceTableBody tr");

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(filter)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}

async function saveBulkAttendance() {
    const dateInput = document.getElementById("attDateFilter");
    const saveBtn = document.getElementById("saveAttendanceBtn");

    if (!dateInput || !dateInput.value) {
        showToast("Please choose a valid attendance date.", "error");
        return;
    }

    const attendance_date = dateInput.value;
    const records = [];

    currentAttendanceRoster.forEach(s => {
        const statusEl = document.getElementById(`attStatus_${s.student_id}`);
        const remarksEl = document.getElementById(`attRemarks_${s.student_id}`);

        if (statusEl) {
            records.push({
                student_id: s.student_id,
                status: statusEl.value,
                remarks: remarksEl ? remarksEl.value.trim() : ""
            });
        }
    });

    if (records.length === 0) {
        showToast("No students to submit attendance for.", "error");
        return;
    }

    try {
        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.textContent = "Saving...";
        }

        const res = await fetch("/api/attendance", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({
                attendance_date: attendance_date,
                records: records
            })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Failed to save attendance");

        showToast(data.message || "Attendance saved successfully!", "success");
        loadAttendanceSheet();

    } catch (err) {
        console.error("Save attendance error:", err);
        showToast("Failed to save attendance: " + err.message, "error");
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.innerHTML = "💾 Save Attendance";
        }
    }
}

// ============================================================
// ADMIN ERP SHELL NAVIGATION & SECTION SWITCHING
// ============================================================

function switchAdminSection(paneId, btnEl, pageTitle = "Dashboard Overview") {
    // 1. Update navigation items
    document.querySelectorAll(".sidebar-nav .nav-link").forEach(link => {
        link.classList.remove("active");
    });

    if (btnEl) {
        btnEl.classList.add("active");
    } else {
        // Find matching link by paneId
        const matchLink = document.querySelector(`[onclick*="${paneId}"]`);
        if (matchLink) matchLink.classList.add("active");
    }

    // 2. Update visible pane
    document.querySelectorAll(".erp-section-pane").forEach(pane => {
        pane.classList.remove("active");
    });

    const targetPane = document.getElementById(paneId);
    if (targetPane) {
        targetPane.classList.add("active");
    }

    // 3. Update breadcrumb and header title
    const headerTitleEl = document.getElementById("headerPageTitle");
    if (headerTitleEl) {
        headerTitleEl.textContent = pageTitle;
    }

    // 4. Close mobile sidebar if open
    toggleMobileSidebar(false);

    // 5. Trigger lazy loaders based on selected section
    if (paneId === "pane-fees") {
        loadFeeLedger();
    } else if (paneId === "pane-attendance") {
        const deptSelect = document.getElementById("attDeptFilter");
        if (deptSelect && deptSelect.value) {
            loadAttendanceSheet();
        } else {
            resetAttendanceDepartmentSelection();
        }
    } else if (paneId === "pane-dashboard" || paneId === "pane-admissions" || paneId === "pane-students") {
        if (!students || students.length === 0) {
            fetchStudents();
        } else {
            renderStudents();
        }
    }

    // Scroll to top of content
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Backwards-compatible alias for any existing switchAdminTab calls
function switchAdminTab(tabId, btnEl) {
    const paneMap = {
        "sec-admissions": { id: "pane-admissions", title: "Student Admissions & Verification" },
        "sec-fees": { id: "pane-fees", title: "Fee & Payment Management" },
        "sec-attendance": { id: "pane-attendance", title: "Attendance Management" },
        "pane-dashboard": { id: "pane-dashboard", title: "Dashboard Overview" },
        "pane-admissions": { id: "pane-admissions", title: "Student Admissions & Verification" },
        "pane-fees": { id: "pane-fees", title: "Fee & Payment Management" },
        "pane-attendance": { id: "pane-attendance", title: "Attendance Management" }
    };

    const target = paneMap[tabId] || { id: tabId, title: "Admin Portal" };
    switchAdminSection(target.id, btnEl, target.title);
}

// Mobile sidebar drawer toggle
function toggleMobileSidebar(force) {
    const sidebar = document.getElementById("adminSidebar");
    const backdrop = document.getElementById("sidebarBackdrop");
    if (!sidebar || !backdrop) return;

    if (force === true) {
        sidebar.classList.add("mobile-open");
        backdrop.classList.add("active");
    } else if (force === false) {
        sidebar.classList.remove("mobile-open");
        backdrop.classList.remove("active");
    } else {
        const isOpen = sidebar.classList.toggle("mobile-open");
        if (isOpen) {
            backdrop.classList.add("active");
        } else {
            backdrop.classList.remove("active");
        }
    }
}

// Administrator Profile Dropdown Menu Toggle
function toggleAdminProfileMenu(force) {
    const menu = document.getElementById("headerUserMenu");
    if (!menu) return;

    if (force === true) {
        menu.style.display = "block";
    } else if (force === false) {
        menu.style.display = "none";
    } else {
        menu.style.display = menu.style.display === "none" ? "block" : "none";
    }
}

// Close user dropdown and notifications dropdown when clicking outside
document.addEventListener("click", function(e) {
    const userDropdown = document.getElementById("headerUserDropdownContainer");
    const userMenu = document.getElementById("headerUserMenu");
    if (userDropdown && userMenu && !userDropdown.contains(e.target)) {
        userMenu.style.display = "none";
    }

    const notifDropdown = document.getElementById("headerNotificationWrapper");
    const notifMenu = document.getElementById("headerNotifDropdown");
    if (notifDropdown && notifMenu && !notifDropdown.contains(e.target)) {
        notifMenu.style.display = "none";
    }
});

// Check Admin Authentication and sync Admin Profile info
async function checkAdminAuth() {
    try {
        const res = await fetch("/api/check-auth");
        if (!res.ok) {
            window.location.href = "login.html";
            return;
        }
        const data = await res.json();
        if (data.authenticated && data.user_type === "admin") {
            const adminName = data.username || "Administrator";
            
            const headerName = document.getElementById("headerAdminName");
            const sidebarName = document.getElementById("sidebarAdminName");
            const menuName = document.getElementById("menuAdminName");

            if (headerName) headerName.textContent = adminName;
            if (sidebarName) sidebarName.textContent = adminName;
            if (menuName) menuName.textContent = adminName;

            const initials = adminName.slice(0, 2).toUpperCase();
            const headerPill = document.getElementById("headerAvatarPill");
            const sidebarAvatar = document.getElementById("sidebarProfileAvatar");

            if (headerPill) headerPill.textContent = initials || "🛡️";
            if (sidebarAvatar) sidebarAvatar.textContent = initials || "🛡️";
        } else {
            window.location.href = "login.html";
        }
    } catch (err) {
        console.warn("Auth check warning:", err);
    }
}

// Global Quick Search Handler
function handleGlobalSearch(query) {
    const q = (query || "").toLowerCase().trim();
    const activePane = document.querySelector(".erp-section-pane.active");

    if (!activePane || activePane.id === "pane-dashboard" || activePane.id === "pane-admissions" || activePane.id === "pane-students") {
        const searchInput = document.getElementById("searchInput");
        if (searchInput) {
            searchInput.value = q;
            renderStudents();
        }
    } else if (activePane.id === "pane-fees") {
        const feeInput = document.getElementById("feeSearchInput");
        if (feeInput) {
            feeInput.value = q;
            filterFeeLedgerTable();
        }
    } else if (activePane.id === "pane-attendance") {
        const attInput = document.getElementById("attSearchInput");
        if (attInput) {
            attInput.value = q;
            filterAttendanceTable();
        }
    }
}

async function loadFeeLedger() {
    const tableBody = document.getElementById("feeLedgerTableBody");
    if (!tableBody) return;

    tableBody.innerHTML = `<tr><td colspan="10" style="text-align: center; color: #64748b; padding: 16px;">Loading student fee ledger...</td></tr>`;

    try {
        const res = await fetch("/api/students");
        if (!res.ok) throw new Error("Failed to load students");
        const students = await res.json();

        if (students.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="10" style="text-align: center; color: #64748b; padding: 16px;">No students found.</td></tr>`;
            return;
        }

        const feePromises = students.map(s => 
            fetch(`/api/students/${s.id}/fees`)
                .then(r => r.ok ? r.json() : null)
                .catch(() => null)
        );

        const feeResults = await Promise.all(feePromises);

        tableBody.innerHTML = students.map((s, index) => {
            const feeData = feeResults[index] || {};
            const total = Number(feeData.total_fee || 110000);
            const paid = Number(feeData.paid_amount || 0);
            const pending = Number(feeData.pending_amount !== undefined ? feeData.pending_amount : (total - paid));
            const status = feeData.payment_status || (paid >= total ? "Paid" : (paid > 0 ? "Partially Paid" : "Pending"));

            let badgeHtml = `<span style="background: #fee2e2; color: #991b1b; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px;">🔴 Pending</span>`;
            if (status === "Paid") {
                badgeHtml = `<span style="background: #dcfce7; color: #15803d; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px;">🟢 Paid</span>`;
            } else if (status === "Partially Paid") {
                badgeHtml = `<span style="background: #fef3c7; color: #b45309; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px;">🟡 Partial</span>`;
            }

            return `
                <tr>
                    <td style="font-weight: 600; color: #64748b;">${index + 1}</td>
                    <td><code style="font-size: 11px; background: #f1f5f9; padding: 2px 6px; border-radius: 4px;">#${s.id}</code></td>
                    <td><strong style="color: #0f172a;">${escapeHtml(s.fullName)}</strong></td>
                    <td><span style="font-size: 12px; color: #475569;">${escapeHtml(s.department || '-')}</span></td>
                    <td><span style="font-size: 11px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 2px 6px; border-radius: 4px;">${escapeHtml(s.admissionType || '-')}</span></td>
                    <td style="font-weight: 600; color: #334155;">₹ ${total.toLocaleString("en-IN")}</td>
                    <td style="font-weight: 700; color: #059669;">₹ ${paid.toLocaleString("en-IN")}</td>
                    <td style="font-weight: 700; color: ${pending > 0 ? '#dc2626' : '#15803d'};">₹ ${pending.toLocaleString("en-IN")}</td>
                    <td>${badgeHtml}</td>
                    <td>
                        <button type="button" class="btn-fee-manage" onclick="viewStudentDetails(${s.id})" title="Manage Student Fee & Record Payment">
                            <span>💳</span> Manage Fee
                        </button>
                    </td>
                </tr>
            `;
        }).join("");

    } catch (err) {
        console.error("Error loading fee ledger:", err);
        tableBody.innerHTML = `<tr><td colspan="10" style="text-align: center; color: #ef4444; padding: 16px;">Failed to load fee ledger: ${escapeHtml(err.message)}</td></tr>`;
    }
}

function filterFeeLedgerTable() {
    const input = document.getElementById("feeSearchInput");
    const filter = input ? input.value.toLowerCase().trim() : "";
    const rows = document.querySelectorAll("#feeLedgerTableBody tr");

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(filter)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}