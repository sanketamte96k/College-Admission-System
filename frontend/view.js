// Global array of students loaded from Flask REST API
let students = [];

// DOM Elements
const tbody = document.getElementById("studentTableBody");
const searchInput = document.getElementById("searchInput");
const viewModal = document.getElementById("viewModal");
const modalDetails = document.getElementById("modalDetails");
const closeModal = document.getElementById("closeModal");
const closeModalFooter = document.getElementById("closeModalFooter");

/**
 * Fetch all students from Flask REST API
 */
function fetchStudents() {
    fetch("/api/students")
        .then(response => {
            if (!response.ok) throw new Error("Failed to fetch records from server");
            return response.json();
        })
        .then(data => {
            students = data;
            renderStudents(searchInput.value);
            updateDashboard();
        })
        .catch(err => {
            console.error("API Fetch Error:", err);
        });
}

/**
 * Render students into the table based on an optional search filter query
 * @param {string} filter - Name search query string
 */
// Filter Elements
const deptFilter = document.getElementById("deptFilter");
const admissionTypeFilter = document.getElementById("admissionTypeFilter");
const genderFilter = document.getElementById("genderFilter");

/**
 * Render students into the table based on search query and multi-filter controls
 */
function renderStudents() {
    tbody.innerHTML = "";
    const nameQuery = (searchInput ? searchInput.value : "").toLowerCase().trim();
    const deptVal = (deptFilter ? deptFilter.value : "").trim();
    const typeVal = (admissionTypeFilter ? admissionTypeFilter.value : "").trim();
    const genderVal = (genderFilter ? genderFilter.value : "").trim();

    // Multi-Filter student list
    const filteredStudents = students.filter(student => {
        const matchesName = (student.fullName || "").toLowerCase().includes(nameQuery);
        const matchesDept = !deptVal || student.department === deptVal;
        const matchesType = !typeVal || student.admissionType === typeVal;
        const matchesGender = !genderVal || student.gender === genderVal;
        return matchesName && matchesDept && matchesType && matchesGender;
    });

    // Empty state handling
    if (filteredStudents.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    <div class="empty-icon">📂</div>
                    <p>No matching student records found.</p>
                </td>
            </tr>
        `;
        return;
    }

    // Render table rows
    filteredStudents.forEach((student, index) => {
        const studentId = student.id;

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${index + 1}</td>
            <td><strong>${escapeHtml(student.fullName)}</strong></td>
            <td>${escapeHtml(student.department)}</td>
            <td>${escapeHtml(student.mobile)}</td>
            <td>${escapeHtml(student.email)}</td>
            <td><span class="badge badge-academic">${escapeHtml(student.percentage12)}%</span></td>
            <td><span class="badge badge-score">${escapeHtml(student.entranceScore)}</span></td>
            <td class="action-cell">
                <button class="btn btn-view" onclick="openViewModal(${studentId})" title="View Details">👁 View</button>
                <button class="btn btn-edit" onclick="editStudent(${studentId})" title="Edit Record">✏ Edit</button>
                <button class="btn btn-download" onclick="downloadPDF(${studentId})" title="Download Admission Form PDF">📥 Download PDF</button>
                <button class="btn btn-delete" onclick="deleteStudent(${studentId})" title="Delete Record">🗑 Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Add Filter Event Listeners
[searchInput, deptFilter, admissionTypeFilter, genderFilter].forEach(el => {
    if (el) el.addEventListener("input", renderStudents);
    if (el) el.addEventListener("change", renderStudents);
});

/**
 * Open View Modal with full student information fetched from REST API
 * @param {number} studentId - Unique database ID of student
 */
function openViewModal(studentId) {
    // Show temporary loading indicator in modal
    modalDetails.innerHTML = `<div style="text-align:center; padding: 40px; color: #64748b;">⌛ Loading student details...</div>`;
    viewModal.style.display = "flex";

    fetch(`/api/students/${studentId}`)
        .then(response => {
            if (!response.ok) throw new Error("Failed to fetch student details");
            return response.json();
        })
        .then(student => {
            populateViewModal(student);
        })
        .catch(err => {
            console.error("Error fetching student details:", err);
            const cachedStudent = students.find(s => s.id === studentId);
            if (cachedStudent) {
                populateViewModal(cachedStudent);
            } else {
                modalDetails.innerHTML = `<div style="color: #ef4444; padding: 20px;">⚠️ Error loading student record.</div>`;
            }
        });
}

/**
 * Populate View Modal details HTML with complete student information & document buttons
 * @param {Object} student - Student record object
 */
function populateViewModal(student) {
    const photoHtml = student.photo
        ? `<div class="passport-photo-wrapper"><img src="/uploads/${escapeHtml(student.photo)}" alt="Passport Photo" class="passport-photo-img"></div>`
        : `<div class="passport-photo-wrapper"><span class="passport-photo-placeholder">👤</span></div>`;

    const photoBtn = student.photo
        ? `<a href="/uploads/${escapeHtml(student.photo)}" target="_blank" class="doc-btn doc-btn-photo">🖼 View Passport Photo</a>`
        : `<span class="doc-btn doc-btn-disabled">Document Not Uploaded</span>`;

    const marksheet10Btn = student.marksheet10
        ? `<a href="/uploads/${escapeHtml(student.marksheet10)}" target="_blank" class="doc-btn doc-btn-pdf">📄 View 10th Marksheet</a>`
        : `<span class="doc-btn doc-btn-disabled">Document Not Uploaded</span>`;

    const marksheet12Btn = student.marksheet12
        ? `<a href="/uploads/${escapeHtml(student.marksheet12)}" target="_blank" class="doc-btn doc-btn-pdf">📄 View 12th Marksheet</a>`
        : `<span class="doc-btn doc-btn-disabled">Document Not Uploaded</span>`;

    const lcBtn = student.leavingCertificate
        ? `<a href="/uploads/${escapeHtml(student.leavingCertificate)}" target="_blank" class="doc-btn doc-btn-pdf">📄 View Leaving Certificate</a>`
        : `<span class="doc-btn doc-btn-disabled">Document Not Uploaded</span>`;

    modalDetails.innerHTML = `
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
            <h4>📚 Course Information</h4>
            <div class="detail-grid">
                <div><strong>Department:</strong> ${escapeHtml(student.department)}</div>
                <div><strong>Admission Type:</strong> ${escapeHtml(student.admissionType)}</div>
            </div>
        </div>

        <div class="detail-section">
            <h4>📁 Uploaded Documents</h4>
            <div class="document-grid">
                <div>${photoBtn}</div>
                <div>${marksheet10Btn}</div>
                <div>${marksheet12Btn}</div>
                <div>${lcBtn}</div>
            </div>
        </div>
    `;

    viewModal.style.display = "flex";
}

/**
 * Redirect to Admission Form with edit ID parameter
 * @param {number} studentId - Database ID of student to edit
 */
function editStudent(studentId) {
    window.location.href = `index.html?edit=${studentId}`;
}

/**
 * Helper to load an image URL into a base64 Data URL for jsPDF embedding
 * @param {string} url - Image URL
 * @returns {Promise<string|null>}
 */
function getImageDataUrl(url) {
    return new Promise((resolve) => {
        const img = new Image();
        img.crossOrigin = 'Anonymous';
        img.onload = function () {
            try {
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                const dataURL = canvas.toDataURL('image/jpeg');
                resolve(dataURL);
            } catch (e) {
                resolve(null);
            }
        };
        img.onerror = function () {
            resolve(null);
        };
        img.src = url;
    });
}

/**
 * Generate and download professional Admission Form PDF for selected student using jsPDF
 * @param {number} studentId - Database ID of student
 */
async function downloadPDF(studentId) {
    const student = students.find(s => s.id === studentId);
    if (!student) return;

    if (!window.jspdf || !window.jspdf.jsPDF) {
        showToast("jsPDF library failed to load. Please check internet connection.", "error");
        return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({
        orientation: 'p',
        unit: 'mm',
        format: 'a4'
    });

    // 1. Page Outer Border (A4 is 210mm x 297mm)
    doc.setDrawColor(30, 58, 138); // #1e3a8a Navy Blue
    doc.setLineWidth(0.8);
    doc.rect(6, 6, 198, 285);

    // Inner thin accent line
    doc.setDrawColor(203, 213, 225);
    doc.setLineWidth(0.3);
    doc.rect(7.5, 7.5, 195, 282);

    // 2. Primary Header Bar
    doc.setFillColor(30, 58, 138);
    doc.rect(8, 8, 194, 28, 'F');

    // Header Logo Icon
    doc.setFillColor(255, 255, 255);
    doc.circle(20, 22, 9, 'F');
    doc.setFontSize(14);
    doc.setTextColor(30, 58, 138);
    doc.setFont('helvetica', 'bold');
    doc.text('Z', 18.5, 26.5);

    // College Name & Subtitle
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    doc.text('ZEAL COLLEGE OF ENGINEERING', 34, 19);

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text('Online Admission System & Student Record', 34, 26);

    // Admission Meta Info Bar
    doc.setFillColor(241, 245, 249);
    doc.rect(8, 36, 194, 10, 'F');
    doc.setFontSize(9);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(30, 58, 138);
    doc.text(`Application ID: #${student.id}`, 12, 42.5);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(71, 85, 105);
    doc.text(`Date of Application: ${student.created_at || new Date().toISOString().slice(0, 10)}`, 130, 42.5);

    // 3. Passport Photo Handling (Top Right Frame)
    let photoLoaded = false;
    if (student.photo) {
        const photoUrl = `/uploads/${student.photo}`;
        const photoDataUrl = await getImageDataUrl(photoUrl);
        if (photoDataUrl) {
            try {
                // Photo Frame Box
                doc.setDrawColor(30, 58, 138);
                doc.setLineWidth(0.5);
                doc.rect(162, 50, 30, 36);
                doc.addImage(photoDataUrl, 'JPEG', 162.5, 50.5, 29, 35);
                photoLoaded = true;
            } catch (e) {
                photoLoaded = false;
            }
        }
    }

    if (!photoLoaded) {
        doc.setDrawColor(148, 163, 184);
        doc.setLineWidth(0.4);
        doc.rect(162, 50, 30, 36);
        doc.setFillColor(248, 250, 252);
        doc.rect(162.5, 50.5, 29, 35, 'F');
        doc.setFontSize(8);
        doc.setTextColor(148, 163, 184);
        doc.setFont('helvetica', 'normal');
        doc.text('PASSPORT', 170, 66);
        doc.text('PHOTO', 173, 71);
    }

    let y = 50;

    // Helper for rendering structured section blocks
    function renderSection(title, data, customWidth = 148) {
        // Section Header
        doc.setFillColor(30, 58, 138);
        doc.rect(10, y, customWidth, 6.5, 'F');
        doc.setFontSize(9);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(255, 255, 255);
        doc.text(title, 13, y + 4.5);

        y += 9.5;
        doc.setFontSize(8.5);
        doc.setTextColor(51, 65, 85);

        for (let i = 0; i < data.length; i += 2) {
            const item1 = data[i];
            const item2 = data[i + 1];

            if (item1) {
                doc.setFont('helvetica', 'bold');
                doc.text(`${item1[0]}:`, 12, y);
                doc.setFont('helvetica', 'normal');
                const val1 = String(item1[1] || '-');
                doc.text(val1, 44, y);
            }

            if (item2) {
                doc.setFont('helvetica', 'bold');
                doc.text(`${item2[0]}:`, 82, y);
                doc.setFont('helvetica', 'normal');
                const val2 = String(item2[1] || '-');
                doc.text(val2, 114, y);
            }
            y += 5.5;
        }
        y += 3;
    }

    // 1. Personal Information Section
    renderSection('1. PERSONAL INFORMATION', [
        ['Full Name', student.fullName],
        ["Father's Name", student.fatherName],
        ["Mother's Name", student.motherName],
        ['Date of Birth', student.dob],
        ['Gender', student.gender],
        ['Blood Group', student.bloodGroup]
    ], 148);

    y = Math.max(y, 90);

    // 2. Contact Information Section
    renderSection('2. CONTACT INFORMATION', [
        ['Mobile Number', student.mobile],
        ['Alt Mobile', student.altMobile || 'N/A'],
        ['Email Address', student.email],
        ['Aadhaar Number', student.aadhaar],
        ['City', student.city],
        ['State', student.state],
        ['Pincode', student.pincode],
        ['Nationality', student.nationality],
        ['Address', student.address],
        ['', '']
    ], 190);

    // 3. Academic Information Section
    renderSection('3. ACADEMIC INFORMATION', [
        ['10th Board', student.board10],
        ['10th Percentage', `${student.percentage10}%`],
        ['12th Board', student.board12],
        ['12th Percentage', `${student.percentage12}%`],
        ['Entrance Exam', student.entranceExam],
        ['Entrance Score', student.entranceScore]
    ], 190);

    // 4. Course Information Section
    renderSection('4. COURSE INFORMATION', [
        ['Department', student.department],
        ['Admission Type', student.admissionType]
    ], 190);

    // 5. Uploaded Documents Checklist Section
    doc.setFillColor(30, 58, 138);
    doc.rect(10, y, 190, 6.5, 'F');
    doc.setFontSize(9);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(255, 255, 255);
    doc.text('5. UPLOADED DOCUMENTS CHECKLIST', 13, y + 4.5);

    y += 9.5;
    doc.setFontSize(8.5);

    const docItems = [
        ['Passport Photo', student.photo],
        ['10th Marksheet', student.marksheet10],
        ['12th Marksheet', student.marksheet12],
        ['Leaving Certificate', student.leavingCertificate]
    ];

    for (let i = 0; i < docItems.length; i += 2) {
        const item1 = docItems[i];
        const item2 = docItems[i + 1];

        if (item1) {
            const status1 = item1[1] ? '[ YES ] Uploaded' : '[ NO ] Not Uploaded';
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(item1[1] ? 5 : 220, item1[1] ? 150 : 38, item1[1] ? 105 : 38);
            doc.text(`${item1[0]}:`, 12, y);
            doc.setFont('helvetica', 'normal');
            doc.text(status1, 48, y);
        }

        if (item2) {
            const status2 = item2[1] ? '[ YES ] Uploaded' : '[ NO ] Not Uploaded';
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(item2[1] ? 5 : 220, item2[1] ? 150 : 38, item2[1] ? 38 : 38);
            doc.text(`${item2[0]}:`, 104, y);
            doc.setFont('helvetica', 'normal');
            doc.text(status2, 140, y);
        }
        y += 5.5;
    }
    y += 4;

    // Declaration Box
    doc.setDrawColor(203, 213, 225);
    doc.setFillColor(248, 250, 252);
    doc.rect(10, y, 190, 15, 'F');
    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(30, 58, 138);
    doc.text('DECLARATION:', 13, y + 4.5);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(71, 85, 105);
    doc.text(
        'I hereby declare that all information provided in this admission form is true, correct, and complete to the best of my knowledge.',
        13, y + 8.5
    );
    doc.text(
        'This official document is generated automatically by the Zeal College Admission Management Portal.',
        13, y + 12.5
    );

    y += 26;

    // Signature Lines
    doc.setDrawColor(71, 85, 105);
    doc.setLineWidth(0.4);
    doc.line(20, y, 75, y);
    doc.line(135, y, 190, y);

    doc.setFontSize(9);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(30, 58, 138);
    doc.text('Student Signature', 32, y + 5);
    doc.text('Admission Officer', 148, y + 5);

    // Page Footer & Numbering
    doc.setFontSize(8);
    doc.setFont('helvetica', 'italic');
    doc.setTextColor(148, 163, 184);
    doc.text('Page 1 of 1', 12, 286);
    doc.text('Zeal College Admission System - Official Record', 105, 286, { align: 'center' });

    // Download PDF
    const safeName = (student.fullName || 'Student').trim().replace(/\s+/g, '_');
    const fileName = `Admission_${safeName}.pdf`;
    doc.save(fileName);

    showToast(`Downloaded ${fileName}`, "success");
}

// Chart.js Instances
let deptChartInstance = null;
let genderChartInstance = null;
let monthlyChartInstance = null;
let admissionTypeChartInstance = null;

/**
 * Update Admin Dashboard cards, Chart.js analytics, and statistics dynamically via /api/dashboard
 */
function updateDashboard() {
    fetch("/api/dashboard")
        .then(res => res.json())
        .then(stats => {
            // Update 6 Top Metric Cards
            if (document.getElementById("totalCount")) document.getElementById("totalCount").textContent = stats.total || 0;
            if (document.getElementById("totalDeptsCount")) document.getElementById("totalDeptsCount").textContent = stats.total_departments || 6;
            if (document.getElementById("todayCount")) document.getElementById("todayCount").textContent = stats.today_admissions || 0;
            if (document.getElementById("monthCount")) document.getElementById("monthCount").textContent = stats.month_admissions || 0;
            if (document.getElementById("maleCount")) document.getElementById("maleCount").textContent = stats.male_count || 0;
            if (document.getElementById("femaleCount")) document.getElementById("femaleCount").textContent = stats.female_count || 0;

            // Update Key Statistics Panel
            if (document.getElementById("highestDept")) document.getElementById("highestDept").textContent = stats.highest_dept || "N/A";
            if (document.getElementById("lowestDept")) document.getElementById("lowestDept").textContent = stats.lowest_dept || "N/A";
            if (document.getElementById("avgScore")) document.getElementById("avgScore").textContent = stats.avg_score || "0.0";
            if (document.getElementById("avgPerc12")) document.getElementById("avgPerc12").textContent = (stats.avg_perc12 || "0.0") + "%";
            if (document.getElementById("latestStudent")) document.getElementById("latestStudent").textContent = stats.latest_student || "N/A";

            // If Chart.js is loaded, render/update analytics charts
            if (window.Chart) {
                renderAnalyticsCharts(stats);
            }
        })
        .catch(err => {
            console.error("Error fetching dashboard analytics:", err);
        });
}

/**
 * Render/Update Chart.js Analytics (Bar, Doughnut, Line, Pie)
 */
function renderAnalyticsCharts(stats) {
    // 1. Department-wise Bar Chart
    const deptCtx = document.getElementById("deptChart");
    if (deptCtx) {
        const deptLabels = Object.keys(stats.dept_stats || {});
        const deptData = Object.values(stats.dept_stats || {});

        if (deptChartInstance) deptChartInstance.destroy();

        deptChartInstance = new Chart(deptCtx, {
            type: 'bar',
            data: {
                labels: deptLabels.length ? deptLabels : ['Computer', 'IT', 'AI & DS', 'Mechanical', 'Civil'],
                datasets: [{
                    label: 'Admissions',
                    data: deptData.length ? deptData : [0, 0, 0, 0, 0],
                    backgroundColor: ['#2563eb', '#0d9488', '#8b5cf6', '#f59e0b', '#ef4444', '#64748b'],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
    }

    // 2. Gender Ratio Doughnut Chart
    const genderCtx = document.getElementById("genderChart");
    if (genderCtx) {
        const gStats = stats.gender_stats || { Male: 0, Female: 0, Other: 0 };
        if (genderChartInstance) genderChartInstance.destroy();

        genderChartInstance = new Chart(genderCtx, {
            type: 'doughnut',
            data: {
                labels: ['Male', 'Female', 'Other'],
                datasets: [{
                    data: [gStats.Male || 0, gStats.Female || 0, gStats.Other || 0],
                    backgroundColor: ['#3b82f6', '#ec4899', '#94a3b8']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    // 3. Monthly Registration Line Chart
    const monthlyCtx = document.getElementById("monthlyChart");
    if (monthlyCtx) {
        const trends = stats.monthly_trends || [];
        const monthLabels = trends.map(t => t.month);
        const monthData = trends.map(t => t.count);

        if (monthlyChartInstance) monthlyChartInstance.destroy();

        monthlyChartInstance = new Chart(monthlyCtx, {
            type: 'line',
            data: {
                labels: monthLabels.length ? monthLabels : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Admissions',
                    data: monthData.length ? monthData : [0, 0, 0, 0, 0, 0],
                    borderColor: '#1e3a8a',
                    backgroundColor: 'rgba(30, 58, 138, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    // 4. Admission Type Pie Chart
    const typeCtx = document.getElementById("admissionTypeChart");
    if (typeCtx) {
        const aTypes = stats.admission_type_stats || { CAP: 0, Management: 0, NRI: 0 };
        if (admissionTypeChartInstance) admissionTypeChartInstance.destroy();

        admissionTypeChartInstance = new Chart(typeCtx, {
            type: 'pie',
            data: {
                labels: ['CAP', 'Management', 'NRI'],
                datasets: [{
                    data: [aTypes.CAP || 0, aTypes.Management || 0, aTypes.NRI || 0],
                    backgroundColor: ['#10b981', '#f59e0b', '#6366f1']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

let pendingDeleteStudentId = null;
const deleteModal = document.getElementById("deleteModal");
const cancelDeleteBtn = document.getElementById("cancelDeleteBtn");
const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
const toastContainer = document.getElementById("toastContainer");

/**
 * Toast Notification System
 * @param {string} message - Message text to display
 * @param {string} type - Notification type ('success' or 'error')
 */
function showToast(message, type = "success") {
    if (!toastContainer) return;
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    const icon = type === "success" ? "✅" : "⚠️";
    toast.innerHTML = `<span>${icon}</span><span>${escapeHtml(message)}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("toast-fade-out");
        setTimeout(() => {
            if (toast.parentElement) toast.parentElement.removeChild(toast);
        }, 300);
    }, 3000);
}

/**
 * Delete student record via DELETE REST API request using custom confirmation modal
 * @param {number} studentId - Database ID of student to delete
 */
function deleteStudent(studentId) {
    const student = students.find(s => s.id === studentId);
    if (!student) return;

    pendingDeleteStudentId = studentId;
    const msgEl = document.getElementById("deleteModalMessage");
    if (msgEl) {
        msgEl.textContent = `Are you sure you want to delete the admission record for "${student.fullName}"?`;
    }
    if (deleteModal) {
        deleteModal.style.display = "flex";
    }
}

function hideDeleteModal() {
    pendingDeleteStudentId = null;
    if (deleteModal) {
        deleteModal.style.display = "none";
    }
}

if (cancelDeleteBtn) {
    cancelDeleteBtn.addEventListener("click", hideDeleteModal);
}

if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener("click", function () {
        if (!pendingDeleteStudentId) return;

        const targetId = pendingDeleteStudentId;
        hideDeleteModal();

        fetch(`/api/students/${targetId}`, {
            method: "DELETE"
        })
        .then(response => {
            if (!response.ok) throw new Error("Unable to delete student");
            return response.json();
        })
        .then(() => {
            showToast("Student deleted successfully.", "success");
            fetchStudents();
        })
        .catch(err => {
            console.error("Delete Error:", err);
            showToast("Unable to delete student.", "error");
        });
    });
}

/**
 * Modal Popup Close Handlers
 */
function hideModal() {
    viewModal.style.display = "none";
}

closeModal.addEventListener("click", hideModal);
closeModalFooter.addEventListener("click", hideModal);

window.addEventListener("click", function (event) {
    if (event.target === viewModal) {
        hideModal();
    }
    if (deleteModal && event.target === deleteModal) {
        hideDeleteModal();
    }
});

window.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
        if (viewModal.style.display === "flex") hideModal();
        if (deleteModal && deleteModal.style.display === "flex") hideDeleteModal();
    }
});

/**
 * Export all student records to Excel (.csv file format with UTF-8 BOM)
 */
function exportToExcel() {
    if (students.length === 0) {
        alert("No student records available to export!");
        return;
    }

    const headers = [
        "Sr No", "Full Name", "Father's Name", "Mother's Name", "DOB", "Gender", "Blood Group",
        "Mobile", "Alt Mobile", "Email", "Aadhaar No", "Address", "City", "State", "Pincode", "Nationality",
        "10th Board", "10th %", "12th Board", "12th %", "Entrance Exam", "Entrance Score", "Department", "Admission Type"
    ];

    let csvContent = "\uFEFF";
    csvContent += headers.map(h => `"${h.replace(/"/g, '""')}"`).join(",") + "\r\n";

    students.forEach((student, index) => {
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
        csvContent += row.map(val => `"${String(val).replace(/"/g, '""')}"`).join(",") + "\r\n";
    });

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `Student_Admission_Records_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Initial API Load
fetchStudents();

/**
 * Admin Logout Handler
 */
function logoutAdmin() {
    fetch("/api/logout", {
        method: "POST"
    })
    .then(res => res.json())
    .then(() => {
        window.location.href = "login.html";
    })
    .catch(err => {
        console.error("Logout error:", err);
        window.location.href = "login.html";
    });
}