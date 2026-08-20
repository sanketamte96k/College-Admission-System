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
    } else if (paneId === "pane-admissions") {
        loadAdmissionsPortal();
    } else if (paneId === "pane-dashboard") {
        if (!students || students.length === 0) {
            fetchStudents();
        } else {
            renderStudents();
        }
    } else if (paneId === "pane-students") {
        fetchStudentsModule(1);
        fetchStudentKpiStats();
    } else if (paneId === "pane-departments") {
        loadDepartments();
    } else if (paneId === "pane-courses") {
        loadCourses();
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

// ============================================================
// ADMISSIONS MODULE CONTROLLERS & LOGIC
// ============================================================
let admCurrentPage = 1;
let admTotalPages = 1;
let admTotalCount = 0;
let admLimit = 20;
let admActivePipelineStage = "";
let admChartDeptInstance = null;
let admChartStatusInstance = null;

function loadAdmissionsPortal(page = 1) {
    admCurrentPage = page;
    fetchAdmissions(page);
    fetchAdmissionsAnalytics();
}

function fetchAdmissions(page = 1) {
    admCurrentPage = page;
    const searchVal = document.getElementById("admSearchInput") ? document.getElementById("admSearchInput").value.trim() : "";
    const deptVal = document.getElementById("admDeptFilter") ? document.getElementById("admDeptFilter").value.trim() : "";
    const courseVal = document.getElementById("admCourseFilter") ? document.getElementById("admCourseFilter").value.trim() : "";
    const statusVal = admActivePipelineStage || (document.getElementById("admStatusFilter") ? document.getElementById("admStatusFilter").value.trim() : "");
    const yearVal = document.getElementById("admYearFilter") ? document.getElementById("admYearFilter").value.trim() : "";
    const fromDate = document.getElementById("admFromDate") ? document.getElementById("admFromDate").value : "";
    const toDate = document.getElementById("admToDate") ? document.getElementById("admToDate").value : "";

    const params = new URLSearchParams({
        page: admCurrentPage,
        limit: admLimit,
        search: searchVal,
        dept: deptVal,
        course: courseVal,
        status: statusVal,
        academic_year: yearVal,
        from_date: fromDate,
        to_date: toDate
    });

    const tbody = document.getElementById("studentTableBody");
    if (tbody) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:30px; color:#64748B;">⌛ Loading admissions records...</td></tr>`;
    }

    fetch(`/api/students?${params.toString()}`)
        .then(res => {
            if (!res.ok) throw new Error("Failed to load admissions from server");
            return res.json();
        })
        .then(data => {
            if (Array.isArray(data)) {
                students = data;
                admTotalCount = data.length;
                admTotalPages = 1;
            } else if (data && Array.isArray(data.students)) {
                students = data.students;
                admTotalCount = data.total || data.students.length;
                admTotalPages = data.pages || 1;
            } else {
                students = [];
                admTotalCount = 0;
                admTotalPages = 1;
            }
            renderAdmissionsTable();
            renderAdmissionsPagination();
        })
        .catch(err => {
            console.error("Fetch admissions error:", err);
            if (tbody) {
                tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:24px; color:#EF4444;">⚠️ Unable to load applications. <button class="btn-sm btn-primary" onclick="fetchAdmissions(1)" style="margin-left:8px;">Retry</button></td></tr>`;
            }
        });
}

function renderAdmissionsTable() {
    const tbody = document.getElementById("studentTableBody");
    if (!tbody) return;

    if (!students || students.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 48px 20px; color: #64748B;">
                    <div style="font-size: 40px; margin-bottom: 8px;">📂</div>
                    <strong style="font-size: 16px; color: #1E293B; display:block;">No applications found.</strong>
                    <p style="margin: 4px 0 16px 0; font-size: 13px;">Try changing your filter settings or submit a new candidate application.</p>
                    <button class="btn-adm-primary" onclick="openNewAdmissionModal()">+ New Application</button>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = students.map(s => {
        const appId = s.application_id || `ADM-2026-${String(s.id).padStart(4, '0')}`;
        const fullName = escapeHtml(s.fullName || 'N/A');
        const email = escapeHtml(s.email || 'N/A');
        const mobile = escapeHtml(s.mobile || 'N/A');
        const dept = escapeHtml(s.department || 'N/A');
        const course = escapeHtml(s.course || `B.Tech in ${dept}`);
        const dateStr = escapeHtml(s.created_at ? s.created_at.split(' ')[0] : 'N/A');
        const status = s.status || 'Pending Verification';

        let statusClass = 'badge-pending';
        let statusIcon = '⌛';
        if (status === 'Approved' || status === 'Verified') {
            statusClass = 'badge-approved';
            statusIcon = '✅';
        } else if (status === 'Under Review') {
            statusClass = 'badge-review';
            statusIcon = '🔍';
        } else if (status === 'Rejected') {
            statusClass = 'badge-rejected';
            statusIcon = '❌';
        } else if (status === 'Enrolled') {
            statusClass = 'badge-enrolled';
            statusIcon = '🎓';
        } else if (status === 'Documents Verified') {
            statusClass = 'badge-doc';
            statusIcon = '📄';
        }

        const photoChip = s.doc_status_photo === 'Verified'
            ? '<span class="doc-chip doc-chip-verified">✓ Photo</span>'
            : (s.doc_status_photo === 'Rejected' ? '<span class="doc-chip doc-chip-rejected">❌ Photo</span>' : '<span class="doc-chip doc-chip-pending">⌛ Photo</span>');

        const doc10Chip = s.doc_status_10th === 'Verified'
            ? '<span class="doc-chip doc-chip-verified">✓ 10th</span>'
            : (s.doc_status_10th === 'Rejected' ? '<span class="doc-chip doc-chip-rejected">❌ 10th</span>' : '<span class="doc-chip doc-chip-pending">⌛ 10th</span>');

        const doc12Chip = s.doc_status_12th === 'Verified'
            ? '<span class="doc-chip doc-chip-verified">✓ 12th</span>'
            : (s.doc_status_12th === 'Rejected' ? '<span class="doc-chip doc-chip-rejected">❌ 12th</span>' : '<span class="doc-chip doc-chip-pending">⌛ 12th</span>');

        const isApproved = (status === 'Approved' || status === 'Verified' || status === 'Documents Verified');
        const isEnrolled = s.is_enrolled || status === 'Enrolled';

        return `
            <tr>
                <td><span class="adm-id-badge">${appId}</span></td>
                <td>
                    <div class="adm-user-cell">
                        <div class="adm-avatar">${fullName.charAt(0).toUpperCase()}</div>
                        <div>
                            <strong class="adm-user-name">${fullName}</strong>
                            ${s.enrollment_number ? `<small style="color:#059669; font-weight:700; display:block;">ENR: ${escapeHtml(s.enrollment_number)}</small>` : ''}
                        </div>
                    </div>
                </td>
                <td>
                    <div><a href="mailto:${email}" class="adm-link">${email}</a></div>
                    <small class="adm-subtext">📞 ${mobile}</small>
                </td>
                <td>
                    <strong class="adm-dept-title">${dept}</strong>
                    <div class="adm-subtext">${course}</div>
                </td>
                <td><span class="adm-date-badge">📅 ${dateStr}</span></td>
                <td>
                    <div class="adm-doc-chips">
                        ${photoChip}
                        ${doc10Chip}
                        ${doc12Chip}
                    </div>
                </td>
                <td>
                    <span class="adm-status-badge ${statusClass}">
                        <span>${statusIcon}</span> ${escapeHtml(status)}
                    </span>
                </td>
                <td style="text-align: right;">
                    <div class="adm-action-group">
                        <button class="btn-adm-table btn-table-view" onclick="openViewModal(${s.id})" title="View Complete Details">👁 View</button>
                        ${!isEnrolled && (status === 'Pending Verification' || status === 'Under Review') ? `
                            <button class="btn-adm-table btn-table-approve" onclick="quickApproveApplication(${s.id})" title="Verify &amp; Approve Candidate">✓ Verify</button>
                        ` : ''}
                        ${!isEnrolled && isApproved ? `
                            <button class="btn-adm-table btn-table-convert" onclick="openConvertModal(${s.id})" title="Convert to Enrolled Student">🎓 Convert</button>
                        ` : ''}
                        ${!isEnrolled && status !== 'Rejected' ? `
                            <button class="btn-adm-table btn-table-reject" onclick="openRejectionModal(${s.id})" title="Reject Candidate Application">❌ Reject</button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function renderAdmissionsPagination() {
    const infoEl = document.getElementById("admPaginationInfo");
    const controlsEl = document.getElementById("admPaginationControls");
    const toolbarCountEl = document.getElementById("admToolbarCount");
    if (!infoEl || !controlsEl) return;

    const start = admTotalCount === 0 ? 0 : (admCurrentPage - 1) * admLimit + 1;
    const end = Math.min(admCurrentPage * admLimit, admTotalCount);

    const infoText = `Showing ${start}–${end} of ${admTotalCount} applications`;
    infoEl.textContent = infoText;
    if (toolbarCountEl) toolbarCountEl.textContent = infoText;

    let btnsHtml = `
        <button class="page-btn" ${admCurrentPage <= 1 ? 'disabled' : ''} onclick="fetchAdmissions(${admCurrentPage - 1})">◀ Previous</button>
    `;

    for (let p = 1; p <= admTotalPages; p++) {
        if (p === 1 || p === admTotalPages || (p >= admCurrentPage - 1 && p <= admCurrentPage + 1)) {
            btnsHtml += `<button class="page-btn ${p === admCurrentPage ? 'active' : ''}" onclick="fetchAdmissions(${p})">${p}</button>`;
        } else if (p === admCurrentPage - 2 || p === admCurrentPage + 2) {
            btnsHtml += `<span style="padding:4px 8px; color:#64748B;">...</span>`;
        }
    }

    btnsHtml += `
        <button class="page-btn" ${admCurrentPage >= admTotalPages ? 'disabled' : ''} onclick="fetchAdmissions(${admCurrentPage + 1})">Next ▶</button>
    `;

    controlsEl.innerHTML = btnsHtml;
}

function fetchAdmissionsAnalytics() {
    fetch('/api/admissions/analytics')
        .then(res => {
            if (!res.ok) throw new Error("Analytics API error");
            return res.json();
        })
        .then(data => {
            if (document.getElementById("admKpiTotal")) document.getElementById("admKpiTotal").textContent = data.total_applications || 0;
            if (document.getElementById("admKpiPending")) document.getElementById("admKpiPending").textContent = data.pending_review || 0;
            if (document.getElementById("admKpiReview")) document.getElementById("admKpiReview").textContent = data.under_review || 0;
            if (document.getElementById("admKpiApproved")) document.getElementById("admKpiApproved").textContent = data.approved || 0;
            if (document.getElementById("admKpiRejected")) document.getElementById("admKpiRejected").textContent = data.rejected || 0;
            if (document.getElementById("admKpiRate")) document.getElementById("admKpiRate").textContent = `${data.admission_rate || 0}%`;

            if (data.pipeline) {
                const p = data.pipeline;
                if (document.getElementById("pipeCountAll")) document.getElementById("pipeCountAll").textContent = data.total_applications || 0;
                if (document.getElementById("pipeCountNew")) document.getElementById("pipeCountNew").textContent = p.new || 0;
                if (document.getElementById("pipeCountReview")) document.getElementById("pipeCountReview").textContent = p.under_review || 0;
                if (document.getElementById("pipeCountDoc")) document.getElementById("pipeCountDoc").textContent = p.documents_verification || 0;
                if (document.getElementById("pipeCountApproved")) document.getElementById("pipeCountApproved").textContent = p.approved || 0;
                if (document.getElementById("pipeCountEnrolled")) document.getElementById("pipeCountEnrolled").textContent = p.enrolled || 0;
            }

            const attContent = document.getElementById("admAttentionContent");
            if (attContent && data.attention_required) {
                const att = data.attention_required;
                let attHtml = '';
                if (att.pending_documents > 0) {
                    attHtml += `<div class="att-chip att-chip-amber"><span class="att-chip-icon">📁</span> <span><strong>${att.pending_documents}</strong> candidate document verifications pending</span></div>`;
                }
                if (att.awaiting_review > 0) {
                    attHtml += `<div class="att-chip att-chip-amber"><span class="att-chip-icon">⌛</span> <span><strong>${att.awaiting_review}</strong> applications awaiting review</span></div>`;
                }
                if (att.approved_awaiting_enrollment > 0) {
                    attHtml += `<div class="att-chip att-chip-purple"><span class="att-chip-icon">🎓</span> <span><strong>${att.approved_awaiting_enrollment}</strong> approved candidates awaiting enrollment conversion</span></div>`;
                }
                if (!attHtml) {
                    attHtml = `<div class="att-chip" style="color:#059669; border-color:#A7F3D0; background:#ECFDF5;"><span class="att-chip-icon">✅</span> <span>No admission issues require attention. System running clean.</span></div>`;
                }
                attContent.innerHTML = attHtml;
            }

            renderAdmissionsCharts(data);
        })
        .catch(err => {
            console.error("Fetch analytics error:", err);
        });
}

function renderAdmissionsCharts(data) {
    if (typeof Chart === 'undefined') return;

    const deptCtx = document.getElementById("admDeptChart");
    if (deptCtx && data.by_department) {
        const labels = Object.keys(data.by_department);
        const totals = labels.map(k => data.by_department[k].total);
        const approveds = labels.map(k => data.by_department[k].approved);

        if (admChartDeptInstance) admChartDeptInstance.destroy();
        admChartDeptInstance = new Chart(deptCtx, {
            type: 'bar',
            data: {
                labels: labels.map(l => l.replace(' Engineering', '')),
                datasets: [
                    { label: 'Total Applications', data: totals, backgroundColor: '#2563EB', borderRadius: 4 },
                    { label: 'Approved', data: approveds, backgroundColor: '#059669', borderRadius: 4 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } },
                scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
            }
        });
    }

    const statusCtx = document.getElementById("admStatusChart");
    if (statusCtx && data.pipeline) {
        const p = data.pipeline;
        if (admChartStatusInstance) admChartStatusInstance.destroy();
        admChartStatusInstance = new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: ['New', 'Under Review', 'Doc Verified', 'Approved', 'Rejected', 'Enrolled'],
                datasets: [{
                    data: [p.new, p.under_review, p.documents_verification, p.approved, p.rejected, p.enrolled],
                    backgroundColor: ['#F59E0B', '#3B82F6', '#8B5CF6', '#10B981', '#EF4444', '#14B8A6']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'right' } }
            }
        });
    }
}

function filterPipelineStage(stage) {
    admActivePipelineStage = stage;

    document.querySelectorAll(".adm-pipe-card").forEach(el => el.classList.remove("active"));
    if (stage === "") {
        if (document.getElementById("pipeStageAll")) document.getElementById("pipeStageAll").classList.add("active");
    } else if (stage === "Pending Verification") {
        if (document.getElementById("pipeStageNew")) document.getElementById("pipeStageNew").classList.add("active");
    } else if (stage === "Under Review") {
        if (document.getElementById("pipeStageReview")) document.getElementById("pipeStageReview").classList.add("active");
    } else if (stage === "Documents Verified") {
        if (document.getElementById("pipeStageDoc")) document.getElementById("pipeStageDoc").classList.add("active");
    } else if (stage === "Approved") {
        if (document.getElementById("pipeStageApproved")) document.getElementById("pipeStageApproved").classList.add("active");
    } else if (stage === "Enrolled") {
        if (document.getElementById("pipeStageEnrolled")) document.getElementById("pipeStageEnrolled").classList.add("active");
    }

    const statusFilter = document.getElementById("admStatusFilter");
    if (statusFilter) statusFilter.value = stage;

    fetchAdmissions(1);
}

function applyAdmissionsFilters() {
    fetchAdmissions(1);
}

function resetAdmissionsFilters() {
    if (document.getElementById("admSearchInput")) document.getElementById("admSearchInput").value = "";
    if (document.getElementById("admDeptFilter")) document.getElementById("admDeptFilter").value = "";
    if (document.getElementById("admCourseFilter")) document.getElementById("admCourseFilter").value = "";
    if (document.getElementById("admStatusFilter")) document.getElementById("admStatusFilter").value = "";
    if (document.getElementById("admYearFilter")) document.getElementById("admYearFilter").value = "2026-27";
    if (document.getElementById("admFromDate")) document.getElementById("admFromDate").value = "";
    if (document.getElementById("admToDate")) document.getElementById("admToDate").value = "";
    admActivePipelineStage = "";
    document.querySelectorAll(".pipeline-stage").forEach(el => el.classList.remove("active"));
    document.getElementById("pipeStageAll").classList.add("active");
    fetchAdmissions(1);
}

function openNewAdmissionModal() {
    const modal = document.getElementById("newAdmissionModal");
    if (modal) modal.style.display = "flex";
}

function closeNewAdmissionModal() {
    const modal = document.getElementById("newAdmissionModal");
    if (modal) modal.style.display = "none";
}

function autoFillCourseOptions(dept) {
    const courseInput = document.getElementById("newCourse");
    if (courseInput && dept) {
        courseInput.value = `B.Tech in ${dept}`;
    }
}

function handleNewAdmissionSubmit(e) {
    e.preventDefault();

    const formData = new FormData();
    formData.append("fullName", document.getElementById("newFullName").value.trim());
    formData.append("fatherName", document.getElementById("newFatherName").value.trim());
    formData.append("motherName", document.getElementById("newMotherName").value.trim());
    formData.append("dob", document.getElementById("newDob").value);
    formData.append("gender", document.getElementById("newGender").value);
    formData.append("bloodGroup", document.getElementById("newBloodGroup").value);
    formData.append("email", document.getElementById("newEmail").value.trim());
    formData.append("mobile", document.getElementById("newMobile").value.trim());
    formData.append("altMobile", document.getElementById("newAltMobile").value.trim());
    formData.append("aadhaar", document.getElementById("newAadhaar").value.trim());
    formData.append("nationality", document.getElementById("newNationality").value.trim());
    formData.append("address", document.getElementById("newAddress").value.trim());
    formData.append("city", document.getElementById("newCity").value.trim());
    formData.append("state", document.getElementById("newState").value.trim());
    formData.append("pincode", document.getElementById("newPincode").value.trim());

    formData.append("board10", document.getElementById("newBoard10").value.trim());
    formData.append("percentage10", document.getElementById("newPercentage10").value);
    formData.append("board12", document.getElementById("newBoard12").value.trim());
    formData.append("percentage12", document.getElementById("newPercentage12").value);
    formData.append("entranceExam", document.getElementById("newEntranceExam").value);
    formData.append("entranceScore", document.getElementById("newEntranceScore").value);

    formData.append("department", document.getElementById("newDepartment").value);
    formData.append("course", document.getElementById("newCourse").value.trim());
    formData.append("admissionType", document.getElementById("newAdmissionType").value);
    formData.append("academic_year", document.getElementById("newAcademicYear").value);

    const photoFile = document.getElementById("newPhoto").files[0];
    const doc10File = document.getElementById("newMarksheet10").files[0];
    const doc12File = document.getElementById("newMarksheet12").files[0];
    const lcFile = document.getElementById("newLeavingCert").files[0];

    if (photoFile) formData.append("photo", photoFile);
    if (doc10File) formData.append("marksheet10", doc10File);
    if (doc12File) formData.append("marksheet12", doc12File);
    if (lcFile) formData.append("leavingCertificate", lcFile);

    fetch('/api/students', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json().then(data => ({ ok: res.ok, status: res.status, data })))
    .then(({ ok, data }) => {
        if (!ok) throw new Error(data.error || "Failed to submit application");
        showToast("New admission application submitted successfully! Application ID: #" + (data.student ? data.student.id : ""), "success");
        closeNewAdmissionModal();
        document.getElementById("newAdmissionForm").reset();
        loadAdmissionsPortal();
    })
    .catch(err => {
        console.error("New admission submit error:", err);
        showToast(err.message, "error");
    });
}

function quickApproveApplication(id) {
    if (!confirm("Are you sure you want to approve this candidate application?")) return;

    fetch(`/api/admissions/${id}/approve`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (!data.success) throw new Error(data.error || "Approval failed");
            showToast(data.message || "Application approved successfully!", "success");
            loadAdmissionsPortal(admCurrentPage);
        })
        .catch(err => {
            console.error("Approval error:", err);
            showToast(err.message, "error");
        });
}

let activeRejectionId = null;
function openRejectionModal(id) {
    activeRejectionId = id;
    document.getElementById("rejectionReasonInput").value = "";
    document.getElementById("rejectionModal").style.display = "flex";
}

function closeRejectionModal() {
    activeRejectionId = null;
    document.getElementById("rejectionModal").style.display = "none";
}

function submitApplicationRejection() {
    if (!activeRejectionId) return;
    const reason = document.getElementById("rejectionReasonInput").value.trim();
    if (!reason) {
        alert("Please provide a reason for rejecting the application.");
        return;
    }

    fetch(`/api/admissions/${activeRejectionId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason })
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) throw new Error(data.error || "Rejection failed");
        showToast("Application rejected successfully.", "success");
        closeRejectionModal();
        loadAdmissionsPortal(admCurrentPage);
    })
    .catch(err => {
        console.error("Rejection error:", err);
        showToast(err.message, "error");
    });
}

let activeConvertId = null;
function openConvertModal(id) {
    activeConvertId = id;
    const student = students.find(s => Number(s.id) === Number(id));
    const bodyEl = document.getElementById("convertModalBody");
    if (student && bodyEl) {
        bodyEl.innerHTML = `
            <div style="background:#F8FAFC; border-radius:8px; padding:12px; margin-bottom:16px;">
                <strong style="color:#0F172A; font-size:16px;">${escapeHtml(student.fullName)}</strong>
                <div style="font-size:13px; color:#64748B; margin-top:4px;">
                    Department: <strong>${escapeHtml(student.department)}</strong> | App ID: <strong>${student.application_id || '#'+student.id}</strong>
                </div>
            </div>
            <p style="font-size:13.5px; color:#334155;">This action will convert this approved candidate into an officially enrolled student, generate their unique Enrollment Number, and update the department seat matrix.</p>
            <div style="margin-top:16px; display:flex; justify-content:flex-end; gap:10px;">
                <button type="button" class="btn-secondary" onclick="closeConvertModal()">Cancel</button>
                <button type="button" class="btn-success" onclick="confirmConvertToStudent(${student.id})" style="background:#059669; color:white; border:none; padding:8px 16px; border-radius:6px; font-weight:600; cursor:pointer;">Confirm Enrollment</button>
            </div>
        `;
    }
    document.getElementById("convertModal").style.display = "flex";
}

function closeConvertModal() {
    activeConvertId = null;
    document.getElementById("convertModal").style.display = "none";
}

function confirmConvertToStudent(id) {
    fetch(`/api/admissions/${id}/convert-to-student`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (!data.success) throw new Error(data.error || "Conversion failed");
            showToast(`Candidate converted to enrolled student! Enrollment No: ${data.enrollment_number}`, "success");
            closeConvertModal();
            loadAdmissionsPortal(admCurrentPage);
        })
        .catch(err => {
            console.error("Convert error:", err);
            showToast(err.message, "error");
        });
}

function exportAdmissionsReport() {
    const searchVal = document.getElementById("admSearchInput") ? document.getElementById("admSearchInput").value.trim() : "";
    const deptVal = document.getElementById("admDeptFilter") ? document.getElementById("admDeptFilter").value.trim() : "";
    const courseVal = document.getElementById("admCourseFilter") ? document.getElementById("admCourseFilter").value.trim() : "";
    const statusVal = document.getElementById("admStatusFilter") ? document.getElementById("admStatusFilter").value.trim() : "";

    const params = new URLSearchParams({ search: searchVal, dept: deptVal, course: courseVal, status: statusVal });
    window.location.href = `/api/admissions/export?${params.toString()}`;
}

// ============================================================
// STUDENTS MODULE MANAGEMENT LOGIC
// ============================================================

let stuCurrentPage = 1;
let stuLimit = 20;
let stuTotalCount = 0;

async function fetchStudentsModule(page = 1) {
    stuCurrentPage = page;
    const searchVal = document.getElementById("stuSearchInput") ? document.getElementById("stuSearchInput").value.trim() : "";
    const deptVal = document.getElementById("stuDeptFilter") ? document.getElementById("stuDeptFilter").value.trim() : "";
    const courseVal = document.getElementById("stuCourseFilter") ? document.getElementById("stuCourseFilter").value.trim() : "";
    const yearVal = document.getElementById("stuYearFilter") ? document.getElementById("stuYearFilter").value.trim() : "";
    const genderVal = document.getElementById("stuGenderFilter") ? document.getElementById("stuGenderFilter").value.trim() : "";
    const statusVal = document.getElementById("stuStatusFilter") ? document.getElementById("stuStatusFilter").value.trim() : "";

    const params = new URLSearchParams({
        page: stuCurrentPage,
        limit: stuLimit,
        search: searchVal,
        dept: deptVal,
        course: courseVal,
        academic_year: yearVal,
        gender: genderVal,
        status: statusVal
    });

    const tbodyEl = document.getElementById("studentTableBody");
    if (tbodyEl) {
        tbodyEl.innerHTML = `
            <tr>
                <td colspan="9" style="text-align: center; padding: 40px; color: #64748B;">
                    <div style="font-size: 24px; margin-bottom: 8px;">⌛</div>
                    <div>Loading student directory from database...</div>
                </td>
            </tr>
        `;
    }

    try {
        const response = await fetch(`/api/students?${params.toString()}`);
        if (!response.ok) throw new Error("Failed to fetch students data");
        const data = await response.json();

        let studentsList = [];
        if (Array.isArray(data)) {
            studentsList = data;
            stuTotalCount = data.length;
        } else if (data && Array.isArray(data.students)) {
            studentsList = data.students;
            stuTotalCount = data.total || data.students.length;
        }

        renderStudentsTableFromData(studentsList);
        renderStudentsPagination();

    } catch (err) {
        console.error("fetchStudentsModule error:", err);
        if (tbodyEl) {
            tbodyEl.innerHTML = `
                <tr>
                    <td colspan="9" style="text-align: center; padding: 30px; color: #EF4444;">
                        ⚠️ Unable to load student records. Please ensure backend server is running.
                    </td>
                </tr>
            `;
        }
    }
}

async function fetchStudentKpiStats() {
    try {
        const response = await fetch("/api/students/stats");
        if (!response.ok) return;
        const stats = await response.json();

        const totalEl = document.getElementById("stuKpiTotal");
        const activeEl = document.getElementById("stuKpiActive");
        const maleEl = document.getElementById("stuKpiMale");
        const femaleEl = document.getElementById("stuKpiFemale");
        const newEl = document.getElementById("stuKpiNew");

        if (totalEl) totalEl.textContent = stats.total_students || 0;
        if (activeEl) activeEl.textContent = stats.active_students || 0;
        if (maleEl) maleEl.textContent = stats.male_students || 0;
        if (femaleEl) femaleEl.textContent = stats.female_students || 0;
        if (newEl) newEl.textContent = stats.new_students || 0;

    } catch (err) {
        console.error("fetchStudentKpiStats error:", err);
    }
}

function renderStudentsTableFromData(list) {
    const tbodyEl = document.getElementById("studentTableBody");
    const countEl = document.getElementById("stuToolbarCount");
    if (!tbodyEl) return;

    if (countEl) {
        countEl.textContent = `Showing ${list.length} of ${stuTotalCount} records`;
    }

    if (!list || list.length === 0) {
        tbodyEl.innerHTML = `
            <tr>
                <td colspan="9" style="text-align: center; padding: 40px; color: #64748B;">
                    <div style="font-size: 28px; margin-bottom: 8px;">📂</div>
                    <div style="font-weight: 600; color: #1E293B;">No matching student records found</div>
                    <small>Try clearing search filters or selecting a different department/academic year.</small>
                </td>
            </tr>
        `;
        return;
    }

    tbodyEl.innerHTML = list.map((s, idx) => {
        const fullName = escapeHtml(s.fullName || 'Unknown Student');
        const email = escapeHtml(s.email || 'N/A');
        const mobile = escapeHtml(s.mobile || 'N/A');
        const dept = escapeHtml(s.department || 'General');
        const course = escapeHtml(s.course || `B.Tech in ${dept}`);
        const year = escapeHtml(s.academic_year || '2026-27');
        const gender = escapeHtml(s.gender || 'Not Specified');
        const status = s.status || 'Pending Verification';
        const dateStr = s.created_at ? s.created_at.split(' ')[0] : 'N/A';

        const displayId = s.enrollment_number ? s.enrollment_number : `ADM-2026-${String(s.id).padStart(4, '0')}`;

        const nameParts = fullName.split(' ').filter(Boolean);
        const initials = nameParts.length >= 2
            ? (nameParts[0][0] + nameParts[1][0]).toUpperCase()
            : fullName.substring(0, 2).toUpperCase();

        const avatarHtml = s.photo
            ? `<img src="/uploads/${escapeHtml(s.photo)}" class="stu-avatar-img" alt="${fullName}">`
            : `<div class="stu-avatar-initials">${initials}</div>`;

        let statusClass = 'badge-pending';
        let statusIcon = '⌛';
        if (status === 'Enrolled') {
            statusClass = 'badge-enrolled';
            statusIcon = '🎓';
        } else if (status === 'Approved' || status === 'Verified' || status === 'Documents Verified') {
            statusClass = 'badge-approved';
            statusIcon = '✅';
        } else if (status === 'Under Review') {
            statusClass = 'badge-review';
            statusIcon = '🔍';
        } else if (status === 'Rejected') {
            statusClass = 'badge-rejected';
            statusIcon = '❌';
        }

        const genderClass = gender === 'Male' ? 'stu-gender-male' : (gender === 'Female' ? 'stu-gender-female' : 'stu-gender-other');

        return `
            <tr>
                <td><span class="stu-id-badge">${displayId}</span></td>
                <td>
                    <div class="stu-user-cell">
                        ${avatarHtml}
                        <div>
                            <strong class="stu-user-name">${fullName}</strong>
                            ${s.enrollment_number ? `<small class="stu-enr-tag">ENR: ${escapeHtml(s.enrollment_number)}</small>` : ''}
                        </div>
                    </div>
                </td>
                <td>
                    <div><a href="mailto:${email}" class="stu-link">${email}</a></div>
                    <small class="stu-subtext">📞 ${mobile}</small>
                </td>
                <td>
                    <strong class="stu-dept-title">${dept}</strong>
                    <div class="stu-subtext">${course}</div>
                </td>
                <td><span class="stu-year-badge">${year}</span></td>
                <td><span class="stu-gender-badge ${genderClass}">${gender}</span></td>
                <td><span class="stu-date-badge">📅 ${dateStr}</span></td>
                <td>
                    <span class="adm-status-badge ${statusClass}">
                        <span>${statusIcon}</span> ${escapeHtml(status)}
                    </span>
                </td>
                <td style="text-align: right;">
                    <div class="stu-action-group">
                        <button type="button" class="btn-stu-tbl btn-tbl-view" onclick="openViewModal(${s.id})" title="View Complete Profile">👁 View</button>
                        <button type="button" class="btn-stu-tbl btn-tbl-edit" onclick="openStudentEditModal(${s.id})" title="Edit Student Record">✏️ Edit</button>
                        <button type="button" class="btn-stu-tbl btn-tbl-delete" onclick="deleteStudent(${s.id})" title="Delete Record">🗑 Delete</button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function renderStudentsPagination() {
    const infoEl = document.getElementById("stuPaginationInfo");
    const controlsEl = document.getElementById("stuPaginationControls");
    if (!infoEl || !controlsEl) return;

    const start = stuTotalCount === 0 ? 0 : (stuCurrentPage - 1) * stuLimit + 1;
    const end = Math.min(stuCurrentPage * stuLimit, stuTotalCount);
    const totalPages = Math.ceil(stuTotalCount / stuLimit) || 1;

    infoEl.textContent = `Showing ${start}–${end} of ${stuTotalCount} students`;

    controlsEl.innerHTML = `
        <button type="button" class="stu-page-btn" ${stuCurrentPage <= 1 ? 'disabled' : ''} onclick="fetchStudentsModule(${stuCurrentPage - 1})">
            ◀ Prev
        </button>
        <span class="stu-page-active">Page ${stuCurrentPage} of ${totalPages}</span>
        <button type="button" class="stu-page-btn" ${stuCurrentPage >= totalPages ? 'disabled' : ''} onclick="fetchStudentsModule(${stuCurrentPage + 1})">
            Next ▶
        </button>
    `;
}

function applyStudentFilters() {
    fetchStudentsModule(1);
    fetchStudentKpiStats();
}

function resetStudentFilters() {
    if (document.getElementById("stuSearchInput")) document.getElementById("stuSearchInput").value = "";
    if (document.getElementById("stuDeptFilter")) document.getElementById("stuDeptFilter").value = "";
    if (document.getElementById("stuCourseFilter")) document.getElementById("stuCourseFilter").value = "";
    if (document.getElementById("stuYearFilter")) document.getElementById("stuYearFilter").value = "";
    if (document.getElementById("stuGenderFilter")) document.getElementById("stuGenderFilter").value = "";
    if (document.getElementById("stuStatusFilter")) document.getElementById("stuStatusFilter").value = "";

    fetchStudentsModule(1);
    fetchStudentKpiStats();
}

function openStudentEditModal(studentId) {
    fetch(`/api/students/${studentId}`)
        .then(res => {
            if (!res.ok) throw new Error("Student not found");
            return res.json();
        })
        .then(s => {
            document.getElementById("editStudentId").value = s.id;
            document.getElementById("editFullName").value = s.fullName || "";
            document.getElementById("editEmail").value = s.email || "";
            document.getElementById("editMobile").value = s.mobile || "";
            document.getElementById("editGender").value = s.gender || "Male";
            document.getElementById("editDepartment").value = s.department || "Computer Engineering";
            document.getElementById("editCourse").value = s.course || `B.Tech in ${s.department || 'Computer Engineering'}`;
            document.getElementById("editAcademicYear").value = s.academic_year || "2026-27";
            document.getElementById("editStatus").value = s.status || "Enrolled";

            document.getElementById("stuEditModal").style.display = "flex";
        })
        .catch(err => {
            console.error("openStudentEditModal error:", err);
            showToast("Failed to load student details for editing", "error");
        });
}

function closeStudentEditModal() {
    document.getElementById("stuEditModal").style.display = "none";
}

async function saveStudentEdits(event) {
    event.preventDefault();
    const studentId = document.getElementById("editStudentId").value;
    const saveBtn = document.getElementById("saveEditStudentBtn");

    const payload = {
        fullName: document.getElementById("editFullName").value.trim(),
        email: document.getElementById("editEmail").value.trim(),
        mobile: document.getElementById("editMobile").value.trim(),
        gender: document.getElementById("editGender").value.trim(),
        department: document.getElementById("editDepartment").value.trim(),
        course: document.getElementById("editCourse").value.trim(),
        academic_year: document.getElementById("editAcademicYear").value.trim(),
        status: document.getElementById("editStatus").value.trim()
    };

    try {
        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.textContent = "Saving...";
        }

        const res = await fetch(`/api/students/${studentId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Failed to update student");

        showToast("Student record updated successfully!", "success");
        closeStudentEditModal();
        fetchStudentsModule(stuCurrentPage);
        fetchStudentKpiStats();

    } catch (err) {
        console.error("saveStudentEdits error:", err);
        showToast(err.message, "error");
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = "Save Changes";
        }
    }
}

function exportStudentsReport() {
    exportAdmissionsReport();
}

// ============================================================
// DEPARTMENT MANAGEMENT MODULE LOGIC
// ============================================================

let cachedDepartments = [];

async function loadDepartments() {
    const searchVal = document.getElementById("dptSearchInput") ? document.getElementById("dptSearchInput").value.trim() : "";
    const statusVal = document.getElementById("dptStatusFilter") ? document.getElementById("dptStatusFilter").value.trim() : "";

    const params = new URLSearchParams({ search: searchVal, status: statusVal });
    const gridContainer = document.getElementById("departmentsGridContainer");

    if (gridContainer) {
        gridContainer.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 50px; color: #64748B;">
                <div style="font-size: 28px; margin-bottom: 8px;">⌛</div>
                <div>Loading department directory from database...</div>
            </div>
        `;
    }

    try {
        const response = await fetch(`/api/departments?${params.toString()}`);
        if (!response.ok) throw new Error("Failed to fetch department data");
        const data = await response.json();

        cachedDepartments = data.departments || [];

        // Update KPI metrics
        if (data.summary) {
            if (document.getElementById("dptKpiTotal")) document.getElementById("dptKpiTotal").textContent = data.summary.total_departments || 0;
            if (document.getElementById("dptKpiActive")) document.getElementById("dptKpiActive").textContent = data.summary.active_departments || 0;
            if (document.getElementById("dptKpiStudents")) document.getElementById("dptKpiStudents").textContent = data.summary.total_students || 0;
            if (document.getElementById("dptKpiCourses")) document.getElementById("dptKpiCourses").textContent = data.summary.total_courses || 0;
        }

        renderDepartmentsGrid(cachedDepartments);

    } catch (err) {
        console.error("loadDepartments error:", err);
        if (gridContainer) {
            gridContainer.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #EF4444;">
                    ⚠️ Unable to load departments. Please ensure backend server is running.
                </div>
            `;
        }
    }
}

// Backwards-compatible alias
function fetchDepartmentsModule() {
    return loadDepartments();
}

function renderDepartmentsGrid(list) {
    const container = document.getElementById("departmentsGridContainer");
    if (!container) return;

    if (!list || list.length === 0) {
        container.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 50px; background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0;">
                <div style="font-size: 32px; margin-bottom: 8px;">🏢</div>
                <h4 style="margin: 0 0 4px 0; color: #0F172A;">No matching departments found</h4>
                <p style="margin: 0; font-size: 13px; color: #64748B;">Try clearing search filters or adding a new academic department.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = list.map(d => {
        const id = d.id;
        const name = escapeHtml(d.name);
        const code = escapeHtml(d.code);
        const hod = escapeHtml(d.hod_name || 'To Be Appointed');
        const hodEmail = escapeHtml(d.hod_email || '');
        const desc = escapeHtml(d.description || 'Standard Engineering Degree Program');
        const totalSeats = d.total_seats || 60;
        const studentCount = d.student_count || 0;
        const courseCount = d.course_count || 1;
        const occupancy = d.occupancy_rate || 0;
        const status = d.status || 'Active';
        const isInactive = status === 'Inactive';

        const barColor = isInactive ? '#94A3B8' : (occupancy >= 90 ? '#DC2626' : (occupancy >= 70 ? '#D97706' : '#2563EB'));

        return `
            <div class="dept-card dpt-card ${isInactive ? 'dpt-card-inactive' : ''}">
                <div class="dept-card-header dpt-card-top">
                    <div class="dpt-code-badge">${code}</div>
                    <span class="dpt-status-badge ${isInactive ? 'status-inactive' : 'status-active'}">
                        <span>${isInactive ? '⏸' : '✓'}</span> ${status}
                    </span>
                </div>

                <h3 class="dpt-card-title">${name}</h3>
                <p class="dpt-card-desc">${desc}</p>

                <div class="dpt-hod-box">
                    <div class="dpt-hod-avatar">👤</div>
                    <div class="dpt-hod-info">
                        <small>HEAD OF DEPARTMENT (HOD)</small>
                        <strong>${hod}</strong>
                        ${hodEmail ? `<a href="mailto:${hodEmail}" class="dpt-hod-email">${hodEmail}</a>` : ''}
                    </div>
                </div>

                <div class="dpt-stats-row">
                    <div class="dpt-stat-item">
                        <small>ENROLLED STUDENTS</small>
                        <strong>👥 ${studentCount}</strong>
                    </div>
                    <div class="dpt-stat-item">
                        <small>COURSES</small>
                        <strong>🎓 ${courseCount} B.Tech</strong>
                    </div>
                    <div class="dpt-stat-item">
                        <small>INTAKE SEATS</small>
                        <strong>🪑 ${totalSeats}</strong>
                    </div>
                </div>

                <div class="dpt-occupancy-wrap">
                    <div class="dpt-occupancy-header">
                        <span>Seat Capacity Utilization</span>
                        <strong>${occupancy}% (${studentCount}/${totalSeats})</strong>
                    </div>
                    <div class="dpt-occupancy-bar">
                        <div class="dpt-occupancy-fill" style="width: ${Math.min(occupancy, 100)}%; background: ${barColor};"></div>
                    </div>
                </div>

                <div class="dept-actions dpt-card-actions">
                    <button type="button" class="btn-dpt-card btn-card-view" onclick="openViewDepartmentModal(${id})" title="View Department Details">👁 View</button>
                    <button type="button" class="btn-dpt-card btn-card-edit" onclick="openEditDepartmentModal(${id})" title="Edit Department Info">✏️ Edit</button>
                    <button type="button" class="btn-dpt-card btn-card-delete" onclick="confirmDeleteDepartment(${id})" title="Delete Department">🗑 Delete</button>
                </div>
            </div>
        `;
    }).join('');
}

function resetDepartmentFilters() {
    if (document.getElementById("dptSearchInput")) document.getElementById("dptSearchInput").value = "";
    if (document.getElementById("dptStatusFilter")) document.getElementById("dptStatusFilter").value = "";
    fetchDepartmentsModule();
}

function openAddDepartmentModal() {
    if (document.getElementById("dptAddForm")) document.getElementById("dptAddForm").reset();
    document.getElementById("dptAddModal").style.display = "flex";
}

function closeAddDepartmentModal() {
    document.getElementById("dptAddModal").style.display = "none";
}

async function submitNewDepartment(event) {
    event.preventDefault();
    const saveBtn = document.getElementById("saveNewDptBtn");

    const payload = {
        name: document.getElementById("addDptName").value.trim(),
        code: document.getElementById("addDptCode").value.trim().toUpperCase(),
        hod_name: document.getElementById("addDptHodName").value.trim(),
        hod_email: document.getElementById("addDptHodEmail").value.trim(),
        total_seats: parseInt(document.getElementById("addDptSeats").value) || 60,
        status: document.getElementById("addDptStatus").value,
        description: document.getElementById("addDptDesc").value.trim()
    };

    try {
        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.textContent = "Creating...";
        }

        const res = await fetch("/api/departments", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Failed to create department");

        showToast(data.message || "Department created successfully!", "success");
        closeAddDepartmentModal();
        fetchDepartmentsModule();

    } catch (err) {
        console.error("submitNewDepartment error:", err);
        showToast(err.message, "error");
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = "Create Department";
        }
    }
}

function openEditDepartmentModal(deptId) {
    fetch(`/api/departments/${deptId}`)
        .then(res => {
            if (!res.ok) throw new Error("Department not found");
            return res.json();
        })
        .then(d => {
            document.getElementById("editDptId").value = d.id;
            document.getElementById("editDptName").value = d.name || "";
            document.getElementById("editDptCode").value = d.code || "";
            document.getElementById("editDptHodName").value = d.hod_name || "";
            document.getElementById("editDptHodEmail").value = d.hod_email || "";
            document.getElementById("editDptSeats").value = d.total_seats || 60;
            document.getElementById("editDptStatus").value = d.status || "Active";
            document.getElementById("editDptDesc").value = d.description || "";

            document.getElementById("dptEditModal").style.display = "flex";
        })
        .catch(err => {
            console.error("openEditDepartmentModal error:", err);
            showToast("Failed to load department details for editing", "error");
        });
}

function closeEditDepartmentModal() {
    document.getElementById("dptEditModal").style.display = "none";
}

async function submitEditDepartment(event) {
    event.preventDefault();
    const deptId = document.getElementById("editDptId").value;
    const saveBtn = document.getElementById("saveEditDptBtn");

    const payload = {
        name: document.getElementById("editDptName").value.trim(),
        code: document.getElementById("editDptCode").value.trim().toUpperCase(),
        hod_name: document.getElementById("editDptHodName").value.trim(),
        hod_email: document.getElementById("editDptHodEmail").value.trim(),
        total_seats: parseInt(document.getElementById("editDptSeats").value) || 60,
        status: document.getElementById("editDptStatus").value,
        description: document.getElementById("editDptDesc").value.trim()
    };

    try {
        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.textContent = "Saving...";
        }

        const res = await fetch(`/api/departments/${deptId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Failed to update department");

        showToast(data.message || "Department updated successfully!", "success");
        closeEditDepartmentModal();
        fetchDepartmentsModule();

    } catch (err) {
        console.error("submitEditDepartment error:", err);
        showToast(err.message, "error");
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = "Save Changes";
        }
    }
}

function openViewDepartmentModal(deptId) {
    const modalBody = document.getElementById("dptViewModalBody");
    if (!modalBody) return;

    modalBody.innerHTML = `
        <div style="text-align: center; padding: 40px; color: #64748B;">
            <div style="font-size: 24px; margin-bottom: 8px;">⌛</div>
            <div>Loading department metrics...</div>
        </div>
    `;

    document.getElementById("dptViewModal").style.display = "flex";

    fetch(`/api/departments/${deptId}`)
        .then(res => {
            if (!res.ok) throw new Error("Department details not available");
            return res.json();
        })
        .then(d => {
            const isInactive = d.status === 'Inactive';
            modalBody.innerHTML = `
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-family: monospace; font-size: 13px; font-weight: 800; background: #2563EB; color: white; padding: 3px 10px; border-radius: 4px;">${escapeHtml(d.code)}</span>
                        <span style="font-size: 12px; font-weight: 700; color: ${isInactive ? '#64748B' : '#059669'}; background: ${isInactive ? '#F1F5F9' : '#ECFDF5'}; padding: 3px 10px; border-radius: 12px; border: 1px solid ${isInactive ? '#CBD5E1' : '#A7F3D0'};">
                            ${isInactive ? '⏸ Inactive' : '✓ Active Branch'}
                        </span>
                    </div>
                    <h3 style="margin: 0 0 6px 0; color: #0F172A; font-size: 20px;">${escapeHtml(d.name)}</h3>
                    <p style="margin: 0; color: #475569; font-size: 13.5px; line-height: 1.5;">${escapeHtml(d.description || 'Standard Engineering Degree Program')}</p>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
                    <div style="border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; background: white;">
                        <small style="font-size: 10.5px; font-weight: 700; color: #64748B; display: block; margin-bottom: 4px;">HEAD OF DEPARTMENT (HOD)</small>
                        <strong style="font-size: 14px; color: #0F172A; display: block;">👤 ${escapeHtml(d.hod_name)}</strong>
                        ${d.hod_email ? `<small style="color: #2563EB; font-weight: 600;">📧 ${escapeHtml(d.hod_email)}</small>` : ''}
                    </div>

                    <div style="border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; background: white;">
                        <small style="font-size: 10.5px; font-weight: 700; color: #64748B; display: block; margin-bottom: 4px;">SEATING CAPACITY & ENROLLMENT</small>
                        <strong style="font-size: 14px; color: #0F172A; display: block;">👥 ${d.student_count || 0} Enrolled / ${d.total_seats || 60} Seats</strong>
                        <small style="color: #059669; font-weight: 600;">📊 ${d.occupancy_rate || 0}% Capacity Utilization</small>
                    </div>
                </div>

                <div style="border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; background: white;">
                    <small style="font-size: 10.5px; font-weight: 700; color: #64748B; display: block; margin-bottom: 8px;">DEGREE PROGRAMS OFFERED</small>
                    <div style="display: flex; align-items: center; gap: 10px; background: #F1F5F9; padding: 10px 14px; border-radius: 6px;">
                        <span style="font-size: 20px;">🎓</span>
                        <div>
                            <strong style="font-size: 13px; color: #1E293B; display: block;">Bachelor of Technology (B.Tech in ${escapeHtml(d.name)})</strong>
                            <small style="color: #64748B;">4 Years Full-Time Undergraduate Degree Program</small>
                        </div>
                    </div>
                </div>

                <div style="margin-top: 20px; display: flex; justify-content: flex-end;">
                    <button type="button" class="btn-secondary" onclick="closeViewDepartmentModal()">Close</button>
                </div>
            `;
        })
        .catch(err => {
            console.error("openViewDepartmentModal error:", err);
            modalBody.innerHTML = `<div style="color: #DC2626; padding: 20px;">⚠️ Failed to load department details.</div>`;
        });
}

function closeViewDepartmentModal() {
    document.getElementById("dptViewModal").style.display = "none";
}

async function confirmDeleteDepartment(deptId) {
    const dept = cachedDepartments.find(d => Number(d.id) === Number(deptId));
    const deptName = dept ? dept.name : "this department";

    if (!confirm(`Are you sure you want to delete the department "${deptName}"?\n\nNote: Safe deletion checks will prevent deleting departments that currently have active student records.`)) {
        return;
    }

    try {
        const res = await fetch(`/api/departments/${deptId}`, {
            method: "DELETE",
            headers: {
                "Accept": "application/json"
            }
        });

        const data = await res.json();
        if (!res.ok) {
            showToast(data.error || "Failed to delete department", "error");
            return;
        }

        showToast(data.message || "Department deleted successfully!", "success");
        fetchDepartmentsModule();

    } catch (err) {
        console.error("confirmDeleteDepartment error:", err);
        showToast("Error deleting department: " + err.message, "error");
    }
}

/* ============================================================ */
/* COURSES & CURRICULUM MODULE JAVASCRIPT                       */
/* ============================================================ */

let currentCurriculumData = null;

async function loadCourses() {
    const container = document.getElementById("coursesCurriculumContainer");
    if (container) {
        container.innerHTML = `
            <div style="text-align:center; padding:60px 20px;">
                <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem; border: 4px solid #E2E8F0; border-top-color: #2563EB; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px;"></div>
                <h4 style="color:#1E293B; font-weight:700;">Loading Curriculum & Academic Programs...</h4>
                <p style="color:#64748B; font-size:13px;">Fetching year-wise and semester-wise subject rosters from database.</p>
            </div>
        `;
    }

    const dept = document.getElementById("courseDeptFilter")?.value || "";
    const program = document.getElementById("courseProgramFilter")?.value || "";
    const year = document.getElementById("courseYearFilter")?.value || "";
    const sem = document.getElementById("courseSemFilter")?.value || "";
    const search = document.getElementById("courseSearchInput")?.value || "";

    const params = new URLSearchParams();
    if (dept) params.append("department", dept);
    if (program) params.append("program", program);
    if (year) params.append("academic_year", year);
    if (sem) params.append("semester", sem);
    if (search) params.append("search", search);

    try {
        const response = await fetch(`/api/courses?${params.toString()}`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        currentCurriculumData = data;
        renderCurriculumView(data);
    } catch (err) {
        console.error("Failed to load curriculum:", err);
        if (container) {
            container.innerHTML = `
                <div style="background:#FEF2F2; border:1px solid #FCA5A5; border-radius:10px; padding:30px; text-align:center; color:#991B1B;">
                    <div style="font-size:32px; margin-bottom:8px;">⚠️</div>
                    <h3 style="margin:0 0 6px 0; font-weight:700;">Unable to Load Curriculum</h3>
                    <p style="margin:0 0 16px 0; font-size:13px; color:#B91C1C;">${err.message || "Network error fetching data."}</p>
                    <button type="button" onclick="loadCourses()" style="background:#DC2626; color:white; border:none; padding:8px 18px; border-radius:6px; font-weight:700; cursor:pointer;">Retry</button>
                </div>
            `;
        }
    }
}

function renderCurriculumView(data) {
    const summary = data.summary || {};
    const curriculum = data.curriculum || [];

    // 1. Update KPI Metrics
    const programsEl = document.getElementById("crsKpiPrograms");
    if (programsEl) programsEl.textContent = summary.total_programs || 0;

    const subjectsEl = document.getElementById("crsKpiSubjects");
    if (subjectsEl) subjectsEl.textContent = summary.total_subjects || 0;

    const creditsEl = document.getElementById("crsKpiCredits");
    if (creditsEl) creditsEl.textContent = summary.total_credits || 0;

    const typesEl = document.getElementById("crsKpiTypes");
    if (typesEl) typesEl.textContent = `${summary.core_subjects || 0} Core / ${summary.elective_subjects || 0} Elec`;

    const container = document.getElementById("coursesCurriculumContainer");
    if (!container) return;

    if (!curriculum || curriculum.length === 0) {
        container.innerHTML = `
            <div style="background:#FFFFFF; border:1px dashed #CBD5E1; border-radius:12px; padding:50px 20px; text-align:center; color:#64748B;">
                <div style="font-size:40px; margin-bottom:10px;">🎓</div>
                <h3 style="color:#1E293B; font-weight:700; margin:0 0 8px 0;">No Curriculum Records Found</h3>
                <p style="font-size:13px; margin:0 0 20px 0;">No subjects match the selected filters or search parameters.</p>
                <button type="button" onclick="openAddCourseModal()" style="background:#2563EB; color:white; border:none; padding:10px 20px; border-radius:6px; font-weight:700; cursor:pointer;">+ Add New Course Program</button>
            </div>
        `;
        return;
    }

    let html = '';

    curriculum.forEach(yearGroup => {
        const yearNum = yearGroup.academic_year;
        const yearName = yearGroup.year_name;
        const sems = yearGroup.semesters || [];

        html += `
            <div class="course-year crs-year-section" style="margin-bottom: 28px;">
                <div class="crs-year-header" style="display:flex; align-items:center; gap:12px; margin-bottom:14px; padding-bottom:8px; border-bottom:2px solid #E2E8F0;">
                    <div style="background:#2563EB; color:white; font-weight:800; font-size:12px; padding:4px 12px; border-radius:6px; text-transform:uppercase; letter-spacing:0.5px;">
                        YEAR ${yearNum}
                    </div>
                    <h3 style="margin:0; font-size:17px; font-weight:800; color:#0F172A;">${yearName} Curriculum</h3>
                </div>

                <div class="crs-semesters-grid" style="display:grid; grid-template-columns: repeat(2, 1fr); gap:16px;">
        `;

        sems.forEach(sem => {
            const semNum = sem.semester_number;
            const subCount = sem.subject_count;
            const credits = sem.total_credits;
            const coreCount = sem.core_count;
            const elecCount = sem.elective_count;
            const subjects = sem.subjects || [];

            html += `
                <div class="course-semester course-semester-card crs-sem-card" style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:20px; box-shadow:0 2px 6px rgba(0,0,0,0.02); display:flex; flex-direction:column; justify-content:space-between; transition:all 0.2s ease;">
                    <div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                            <span style="font-size:13px; font-weight:800; color:#2563EB; background:#EFF6FF; padding:4px 10px; border-radius:6px; border:1px solid #BFDBFE;">
                                Semester ${semNum}
                            </span>
                            <span style="font-size:11.5px; font-weight:700; color:#64748B;">
                                🏅 ${credits} Credits
                            </span>
                        </div>

                        <h4 style="margin:0 0 6px 0; font-size:15px; font-weight:800; color:#1E293B;">
                            ${sem.semester_name}
                        </h4>

                        <div style="display:flex; gap:12px; font-size:12px; color:#475569; margin-bottom:14px;">
                            <span>📘 <strong>${subCount}</strong> Subjects</span>
                            <span>✓ <strong>${coreCount}</strong> Core</span>
                            <span>⭐ <strong>${elecCount}</strong> Elective</span>
                        </div>

                        <div style="background:#F8FAFC; border-radius:8px; padding:10px; margin-bottom:16px;">
                            <small style="font-size:10px; font-weight:700; color:#94A3B8; text-transform:uppercase; display:block; margin-bottom:6px;">Sample Subjects:</small>
                            ${subjects.length > 0 ? `
                                <ul style="margin:0; padding-left:16px; font-size:12px; color:#334155;">
                                    ${subjects.slice(0, 3).map(s => `<li><strong>${s.code}</strong> — ${s.name} (${s.credits} cr)</li>`).join('')}
                                    ${subjects.length > 3 ? `<li style="color:#64748B; font-style:italic;">+ ${subjects.length - 3} more subjects...</li>` : ''}
                                </ul>
                            ` : '<span style="font-size:12px; color:#94A3B8; font-style:italic;">No subjects defined for this semester.</span>'}
                        </div>
                    </div>

                    <div class="course-actions crs-sem-actions" style="display:flex; gap:8px;">
                        <button type="button" onclick="viewSemesterSubjects(${yearNum}, ${semNum})" style="flex:1; height:34px; background:#F1F5F9; color:#1E293B; border:1px solid #CBD5E1; border-radius:6px; font-size:12px; font-weight:700; cursor:pointer; transition:all 0.15s ease;">
                            👁 View Subjects
                        </button>
                        <button type="button" onclick="openAddSubjectModal('', '', ${yearNum}, ${semNum})" style="height:34px; padding:0 12px; background:#2563EB; color:white; border:none; border-radius:6px; font-size:12px; font-weight:700; cursor:pointer;">
                            + Add Subject
                        </button>
                    </div>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function resetCourseFilters() {
    const dept = document.getElementById("courseDeptFilter");
    const prog = document.getElementById("courseProgramFilter");
    const yr = document.getElementById("courseYearFilter");
    const sem = document.getElementById("courseSemFilter");
    const search = document.getElementById("courseSearchInput");

    if (dept) dept.value = "";
    if (prog) prog.value = "";
    if (yr) yr.value = "";
    if (sem) sem.value = "";
    if (search) search.value = "";

    loadCourses();
}

// ============================================================
// SEMESTER SUBJECTS INSPECTOR MODAL
// ============================================================

function viewSemesterSubjects(yearNum, semNum) {
    const modal = document.getElementById("semesterSubjectsModal");
    const titleEl = document.getElementById("semModalTitle");
    const bodyEl = document.getElementById("semModalBody");

    if (!currentCurriculumData || !currentCurriculumData.curriculum) return;

    let targetSem = null;
    currentCurriculumData.curriculum.forEach(y => {
        if (y.academic_year === yearNum) {
            y.semesters.forEach(s => {
                if (s.semester_number === semNum) {
                    targetSem = s;
                }
            });
        }
    });

    if (!targetSem) return;

    if (titleEl) {
        titleEl.textContent = `📚 ${targetSem.semester_name} Subjects Roster (${yearNum}st/nd/rd/th Year)`;
    }

    const subs = targetSem.subjects || [];

    let html = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; padding-bottom:10px; border-bottom:1px solid #E2E8F0;">
            <div>
                <span style="font-size:13px; font-weight:700; color:#475569;">Total Subjects: <strong>${subs.length}</strong></span> |
                <span style="font-size:13px; font-weight:700; color:#475569;">Total Credits: <strong>${targetSem.total_credits}</strong></span>
            </div>
            <button type="button" onclick="openAddSubjectModal('', '', ${yearNum}, ${semNum})" style="background:#2563EB; color:white; border:none; padding:6px 14px; border-radius:6px; font-size:12px; font-weight:700; cursor:pointer;">
                + Add Subject to Sem ${semNum}
            </button>
        </div>
    `;

    if (subs.length === 0) {
        html += `
            <div style="text-align:center; padding:30px; color:#64748B;">
                <p>No subjects added for Semester ${semNum} yet.</p>
            </div>
        `;
    } else {
        html += `
            <div style="overflow-x:auto;">
                <table class="course-subject-table" style="width:100%; border-collapse:collapse; font-size:12.5px;">
                    <thead>
                        <tr style="background:#F8FAFC; border-bottom:2px solid #E2E8F0; text-align:left;">
                            <th style="padding:10px; color:#475569; font-weight:700;">CODE</th>
                            <th style="padding:10px; color:#475569; font-weight:700;">SUBJECT NAME</th>
                            <th style="padding:10px; color:#475569; font-weight:700;">CREDITS</th>
                            <th style="padding:10px; color:#475569; font-weight:700;">TYPE</th>
                            <th style="padding:10px; color:#475569; font-weight:700;">STATUS</th>
                            <th style="padding:10px; color:#475569; font-weight:700; text-align:right;">ACTIONS</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${subs.map(s => `
                            <tr style="border-bottom:1px solid #F1F5F9;">
                                <td style="padding:10px; font-weight:800; color:#2563EB;">${s.code}</td>
                                <td style="padding:10px;">
                                    <strong style="color:#0F172A;">${s.name}</strong>
                                    ${s.description ? `<br><small style="color:#64748B;">${s.description}</small>` : ''}
                                </td>
                                <td style="padding:10px; font-weight:700;">${s.credits}</td>
                                <td style="padding:10px;">
                                    <span style="font-size:11px; font-weight:700; padding:2px 8px; border-radius:10px; background:${s.subject_type === 'Core' ? '#EFF6FF' : '#FEF3C7'}; color:${s.subject_type === 'Core' ? '#2563EB' : '#D97706'};">
                                        ${s.subject_type}
                                    </span>
                                </td>
                                <td style="padding:10px;">
                                    <span style="font-size:11px; font-weight:700; color:${s.status === 'Active' ? '#16A34A' : '#94A3B8'};">
                                        ${s.status}
                                    </span>
                                </td>
                                <td style="padding:10px; text-align:right;">
                                    <button type="button" onclick="openEditSubjectModal(${s.id})" style="background:#EFF6FF; color:#2563EB; border:1px solid #BFDBFE; border-radius:4px; padding:4px 8px; font-size:11px; font-weight:700; cursor:pointer; margin-right:4px;">✏️ Edit</button>
                                    <button type="button" onclick="confirmDeleteSubject(${s.id})" style="background:#FEF2F2; color:#DC2626; border:1px solid #FECACA; border-radius:4px; padding:4px 8px; font-size:11px; font-weight:700; cursor:pointer;">🗑 Delete</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    if (bodyEl) bodyEl.innerHTML = html;
    if (modal) modal.style.display = "block";
}

function closeSemesterSubjectsModal() {
    const modal = document.getElementById("semesterSubjectsModal");
    if (modal) modal.style.display = "none";
}

// ============================================================
// COURSE PROGRAM MODAL
// ============================================================

function openAddCourseModal() {
    const modal = document.getElementById("courseAddEditModal");
    const form = document.getElementById("courseForm");
    const title = document.getElementById("courseModalTitle");

    if (form) form.reset();
    document.getElementById("courseModalId").value = "";
    if (title) title.textContent = "🎓 Add New Academic Program";

    if (modal) modal.style.display = "block";
}

function closeCourseModal() {
    const modal = document.getElementById("courseAddEditModal");
    if (modal) modal.style.display = "none";
}

async function submitCourseForm(e) {
    e.preventDefault();

    const id = document.getElementById("courseModalId").value;
    const name = document.getElementById("crsModalName").value;
    const code = document.getElementById("crsModalCode").value;
    const department = document.getElementById("crsModalDept").value;
    const degree_type = document.getElementById("crsModalDegree").value;
    const duration_years = document.getElementById("crsModalYears").value;
    const total_credits = document.getElementById("crsModalCredits").value;
    const description = document.getElementById("crsModalDesc").value;

    const payload = {
        name, code, department, degree_type,
        duration_years: parseInt(duration_years),
        total_credits: parseInt(total_credits),
        description
    };

    const url = id ? `/api/courses/${id}` : "/api/courses";
    const method = id ? "PUT" : "POST";

    try {
        const res = await fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) {
            alert(`Error: ${data.error || "Failed to save program."}`);
            return;
        }

        alert(data.message || "Program saved successfully!");
        closeCourseModal();
        loadCourses();
    } catch (err) {
        console.error("Save program error:", err);
        alert("Failed to submit program request.");
    }
}

// ============================================================
// SUBJECT MODAL
// ============================================================

function openAddSubjectModal(dept = "", program = "", year = 1, sem = 1) {
    const modal = document.getElementById("subjectAddEditModal");
    const form = document.getElementById("subjectForm");
    const title = document.getElementById("subjectModalTitle");

    if (form) form.reset();
    document.getElementById("subModalId").value = "";
    if (title) title.textContent = "📘 Add New Subject";

    if (dept) document.getElementById("subModalDept").value = dept;
    if (program) document.getElementById("subModalProgram").value = program;
    if (year) document.getElementById("subModalYear").value = year;
    if (sem) document.getElementById("subModalSem").value = sem;

    if (modal) modal.style.display = "block";
}

function closeSubjectModal() {
    const modal = document.getElementById("subjectAddEditModal");
    if (modal) modal.style.display = "none";
}

async function openEditSubjectModal(subId) {
    try {
        const res = await fetch(`/api/subjects/${subId}`);
        if (!res.ok) throw new Error("Subject not found");
        const sub = await res.json();

        document.getElementById("subModalId").value = sub.id;
        document.getElementById("subModalCode").value = sub.code;
        document.getElementById("subModalName").value = sub.name;
        document.getElementById("subModalDept").value = sub.department;
        document.getElementById("subModalProgram").value = sub.program;
        document.getElementById("subModalYear").value = sub.academic_year;
        document.getElementById("subModalSem").value = sub.semester;
        document.getElementById("subModalCredits").value = sub.credits;
        document.getElementById("subModalType").value = sub.subject_type;
        document.getElementById("subModalDesc").value = sub.description || "";

        document.getElementById("subjectModalTitle").textContent = `✏️ Edit Subject (${sub.code})`;
        document.getElementById("subjectAddEditModal").style.display = "block";
    } catch (err) {
        alert("Failed to fetch subject details: " + err.message);
    }
}

async function submitSubjectForm(e) {
    e.preventDefault();

    const id = document.getElementById("subModalId").value;
    const code = document.getElementById("subModalCode").value;
    const name = document.getElementById("subModalName").value;
    const department = document.getElementById("subModalDept").value;
    const program = document.getElementById("subModalProgram").value;
    const academic_year = parseInt(document.getElementById("subModalYear").value);
    const semester = parseInt(document.getElementById("subModalSem").value);
    const credits = parseInt(document.getElementById("subModalCredits").value);
    const subject_type = document.getElementById("subModalType").value;
    const description = document.getElementById("subModalDesc").value;

    const payload = {
        code, name, department, program,
        academic_year, semester, credits,
        subject_type, description
    };

    const url = id ? `/api/subjects/${id}` : "/api/subjects";
    const method = id ? "PUT" : "POST";

    try {
        const res = await fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) {
            alert(`Error: ${data.error || "Failed to save subject."}`);
            return;
        }

        alert(data.message || "Subject saved successfully!");
        closeSubjectModal();
        closeSemesterSubjectsModal();
        loadCourses();
    } catch (err) {
        console.error("Save subject error:", err);
        alert("Failed to save subject record.");
    }
}

async function confirmDeleteSubject(subId) {
    if (!confirm("Are you sure you want to delete this subject?")) return;

    try {
        const res = await fetch(`/api/subjects/${subId}`, { method: "DELETE" });
        const data = await res.json();

        if (!res.ok) {
            alert(`Delete Blocked: ${data.error || "Failed to delete subject."}`);
            return;
        }

        alert(data.message || "Subject deleted successfully.");
        closeSemesterSubjectsModal();
        loadCourses();
    } catch (err) {
        alert("Failed to delete subject: " + err.message);
    }
}