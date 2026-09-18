/* ==========================================================================
   PERSONAL FINANCE ADVISOR BOT — FRONTEND APPLICATION LOGIC
   ========================================================================== */

let currentUser = null;
let currentMonth = new Date().toISOString().slice(0, 7); // YYYY-MM
let categories = [];
let allTransactions = [];
let cashflowChartInstance = null;
let categoryChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    // Set default month in picker
    const monthPicker = document.getElementById('globalMonthPicker');
    if (monthPicker) {
        monthPicker.value = currentMonth;
        monthPicker.addEventListener('change', (e) => {
            currentMonth = e.target.value;
            reloadActiveTab();
        });
    }

    // Setup Navigation Tabs
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = item.getAttribute('data-tab');
            switchTab(tabName);
        });
    });

    // Setup Auth Listeners
    setupAuthListeners();

    // Setup Forms
    setupFormListeners();

    // Setup Transaction Search and Filter listeners
    document.getElementById('txSearch')?.addEventListener('input', filterTransactions);
    document.getElementById('txTypeFilter')?.addEventListener('change', filterTransactions);

    // Load Categories
    await fetchCategories();

    // Check Login Session
    await checkSession();
}

/* ==================== TAB NAVIGATION ==================== */
function switchTab(tabName) {
    document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
    document.querySelectorAll('.tab-page').forEach(page => page.classList.remove('active'));

    const navLink = document.querySelector(`.nav-item[data-tab="${tabName}"]`);
    const tabPage = document.getElementById(`tab-${tabName}`);

    if (navLink) navLink.classList.add('active');
    if (tabPage) tabPage.classList.add('active');

    // Update Topbar Title & Subtitle
    const titleMap = {
        'overview': 'Dashboard Overview',
        'transactions': 'Income & Expense Logging',
        'budget': 'AI Budget Manager',
        'savings': 'Savings Goals Tracker',
        'reports': 'Monthly Summary Report',
        'ai-insights': 'AI Financial Assistant',
        'household': 'Household Budget Sharing'
    };
    const subMap = {
        'overview': 'Real-time personal cashflow and intelligent budgeting',
        'transactions': 'Log and filter monthly income sources and expenses',
        'budget': 'AI-calculated category spending limits and variances',
        'savings': 'Track financial milestones and progress',
        'reports': 'Printable executive monthly financial summary',
        'ai-insights': 'Automated spending diagnostics and AI financial counselor',
        'household': 'Shared multi-user budget management'
    };
    document.getElementById('pageTitle').textContent = titleMap[tabName] || 'Dashboard';
    const subEl = document.getElementById('pageSubtitle');
    if (subEl) subEl.textContent = subMap[tabName] || '';

    // Reload tab data
    loadTabData(tabName);
}

function reloadActiveTab() {
    const activeNav = document.querySelector('.nav-item.active');
    if (activeNav) {
        const tabName = activeNav.getAttribute('data-tab');
        loadTabData(tabName);
    }
}

function loadTabData(tabName) {
    if (tabName === 'overview') loadOverview();
    else if (tabName === 'transactions') loadTransactions();
    else if (tabName === 'budget') loadBudgetManager();
    else if (tabName === 'savings') loadSavingsGoals();
    else if (tabName === 'reports') loadMonthlyReport();
    else if (tabName === 'ai-insights') loadAIAdvisor();
    else if (tabName === 'household') loadHousehold();
}

/* ==================== CATEGORIES & AUTH ==================== */
async function fetchCategories() {
    try {
        const res = await fetch('/api/categories');
        const data = await res.json();
        categories = data.categories || [];
        populateCategoryDropdowns();
    } catch (err) {
        console.error('Error fetching categories:', err);
    }
}

function populateCategoryDropdowns() {
    const select = document.getElementById('expenseCategory');
    if (!select) return;

    select.innerHTML = '<option value="">Select Category...</option>';
    categories.forEach(cat => {
        const opt = document.createElement('option');
        opt.value = cat.id;
        opt.textContent = `${cat.name} (${cat.type})`;
        select.appendChild(opt);
    });
}

async function checkSession() {
    try {
        const res = await fetch('/api/auth/me');
        const data = await res.json();
        if (data.authenticated && data.user) {
            currentUser = data.user;
            updateUserUI(true);
        } else {
            currentUser = null;
            updateUserUI(false);
            openAuthModal();
        }
        loadOverview();
    } catch (err) {
        console.error('Error checking session:', err);
    }
}

function updateUserUI(isAuth) {
    const nameEl = document.getElementById('userName');
    const badgeEl = document.getElementById('userBadge');
    const avatarEl = document.getElementById('userAvatar');
    const logoutBtn = document.getElementById('logoutBtn');
    const authBtnText = document.getElementById('authBtnText');

    if (isAuth && currentUser) {
        nameEl.textContent = currentUser.name;
        badgeEl.textContent = currentUser.account_type.toUpperCase();
        avatarEl.textContent = currentUser.name.charAt(0).toUpperCase();
        logoutBtn.style.display = 'block';
        authBtnText.textContent = 'Account Profile';
    } else {
        nameEl.textContent = 'Guest User';
        badgeEl.textContent = 'INDIVIDUAL';
        avatarEl.textContent = 'G';
        logoutBtn.style.display = 'none';
        authBtnText.textContent = 'Sign In / Register';
    }
}

function setupAuthListeners() {
    const modal = document.getElementById('authModal');
    const openBtn = document.getElementById('openAuthModalBtn');
    const closeBtn = document.getElementById('closeAuthModalBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const demoSeedBtn = document.getElementById('demoSeedBtn');

    openBtn.addEventListener('click', () => openAuthModal());
    closeBtn.addEventListener('click', () => closeAuthModal());
    logoutBtn.addEventListener('click', () => handleLogout());
    if (demoSeedBtn) demoSeedBtn.addEventListener('click', () => triggerDemoSeed());

    // Login Form Submit
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        try {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();
            if (res.ok) {
                currentUser = data.user;
                updateUserUI(true);
                closeAuthModal();
                loadOverview();
            } else {
                alert(data.error || 'Login failed');
            }
        } catch (err) {
            alert('Error logging in');
        }
    });

    // Signup Form Submit
    document.getElementById('signupForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('signupName').value;
        const email = document.getElementById('signupEmail').value;
        const password = document.getElementById('signupPassword').value;
        const account_type = document.getElementById('accountType').value;
        const invite_code = document.getElementById('signupInviteCode').value;

        try {
            const res = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password, account_type, invite_code })
            });
            const data = await res.json();
            if (res.ok) {
                currentUser = data.user;
                updateUserUI(true);
                closeAuthModal();
                loadOverview();
            } else {
                alert(data.error || 'Signup failed');
            }
        } catch (err) {
            alert('Error creating account');
        }
    });
}

function openAuthModal() {
    document.getElementById('authModal').style.display = 'flex';
}
function closeAuthModal() {
    document.getElementById('authModal').style.display = 'none';
}

function toggleAuthForm(mode) {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const tabLogin = document.getElementById('tabLoginBtn');
    const tabSignup = document.getElementById('tabSignupBtn');

    if (mode === 'login') {
        loginForm.style.display = 'grid';
        signupForm.style.display = 'none';
        tabLogin.classList.add('active');
        tabSignup.classList.remove('active');
    } else {
        loginForm.style.display = 'none';
        signupForm.style.display = 'grid';
        tabLogin.classList.remove('active');
        tabSignup.classList.add('active');
    }
}

async function handleLogout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        currentUser = null;
        updateUserUI(false);
        openAuthModal();
        loadOverview();
    } catch (err) {
        console.error('Logout error:', err);
    }
}

async function triggerDemoSeed() {
    try {
        const res = await fetch('/api/auth/demo-seed', { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
            currentUser = data.user;
            updateUserUI(true);
            closeAuthModal();
            loadOverview();
            alert('⚡ Demo financial data loaded successfully!');
        } else {
            alert('Could not seed demo data');
        }
    } catch (err) {
        alert('Failed to connect to seed endpoint');
    }
}

/* ==================== FORM LISTENERS ==================== */
function setupFormListeners() {
    // Set default dates to today
    const todayStr = new Date().toISOString().split('T')[0];
    if (document.getElementById('incomeDate')) document.getElementById('incomeDate').value = todayStr;
    if (document.getElementById('expenseDate')) document.getElementById('expenseDate').value = todayStr;

    // Income Form Submit
    document.getElementById('incomeForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const source = document.getElementById('incomeSource').value;
        const amount = document.getElementById('incomeAmount').value;
        const date_received = document.getElementById('incomeDate').value;
        const is_recurring = document.getElementById('incomeRecurring').checked;
        const note = document.getElementById('incomeNote').value;

        try {
            const res = await fetch('/api/income', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ source, amount, date_received, is_recurring, note })
            });
            if (res.ok) {
                document.getElementById('incomeForm').reset();
                document.getElementById('incomeDate').value = todayStr;
                loadTransactions();
                alert('Income record saved!');
            }
        } catch (err) {
            alert('Failed to log income');
        }
    });

    // Expense Form Submit
    document.getElementById('expenseForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const category_id = document.getElementById('expenseCategory').value;
        const amount = document.getElementById('expenseAmount').value;
        const date = document.getElementById('expenseDate').value;
        const note = document.getElementById('expenseNote').value;

        try {
            const res = await fetch('/api/expenses', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category_id, amount, date, note })
            });
            if (res.ok) {
                document.getElementById('expenseForm').reset();
                document.getElementById('expenseDate').value = todayStr;
                loadTransactions();
                alert('Expense record saved!');
            }
        } catch (err) {
            alert('Failed to log expense');
        }
    });

    // Generate AI Budget Button
    document.getElementById('generateAiBudgetBtn')?.addEventListener('click', async () => {
        try {
            const res = await fetch('/api/budget/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ month: currentMonth })
            });
            const data = await res.json();
            if (res.ok) {
                loadBudgetManager();
                alert(data.message);
            }
        } catch (err) {
            alert('Failed to generate budget');
        }
    });

    // New Savings Goal Form
    document.getElementById('savingsGoalForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const goal_name = document.getElementById('goalName').value;
        const target_amount = document.getElementById('targetAmount').value;
        const current_amount = document.getElementById('initialDeposit').value;
        const target_date = document.getElementById('targetDate').value;

        try {
            const res = await fetch('/api/savings-goals', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ goal_name, target_amount, current_amount, target_date })
            });
            if (res.ok) {
                document.getElementById('savingsGoalForm').reset();
                loadSavingsGoals();
                alert('Savings goal created!');
            }
        } catch (err) {
            alert('Failed to create savings goal');
        }
    });

    // Deposit Form Submit
    document.getElementById('depositForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const goal_id = document.getElementById('depositGoalId').value;
        const amount = document.getElementById('depositAmount').value;

        try {
            const res = await fetch(`/api/savings-goals/${goal_id}/deposit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount })
            });
            if (res.ok) {
                closeDepositModal();
                loadSavingsGoals();
            }
        } catch (err) {
            alert('Deposit failed');
        }
    });

    // Chat Form Submit
    document.getElementById('chatForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const promptInput = document.getElementById('chatPrompt');
        const prompt = promptInput.value.trim();
        if (!prompt) return;

        appendChatMessage('user', prompt);
        promptInput.value = '';

        try {
            const res = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            });
            const data = await res.json();
            if (res.ok) {
                appendChatMessage('bot', data.reply);
            }
        } catch (err) {
            appendChatMessage('bot', 'Sorry, I encountered an error answering your prompt.');
        }
    });

    // Household Forms
    document.getElementById('createHouseholdForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('newHouseholdName').value;
        try {
            const res = await fetch('/api/household/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            const data = await res.json();
            if (res.ok) {
                loadHousehold();
                alert(data.message);
            }
        } catch (err) {
            alert('Failed to create household');
        }
    });

    document.getElementById('joinHouseholdForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const invite_code = document.getElementById('joinInviteCode').value;
        try {
            const res = await fetch('/api/household/join', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ invite_code })
            });
            const data = await res.json();
            if (res.ok) {
                loadHousehold();
                alert(data.message);
            } else {
                alert(data.error);
            }
        } catch (err) {
            alert('Failed to join household');
        }
    });
}

/* ==================== TAB 1: OVERVIEW DASHBOARD ==================== */
async function loadOverview() {
    try {
        const [incRes, expRes, aiRes] = await Promise.all([
            fetch(`/api/income?month=${currentMonth}`),
            fetch(`/api/expenses?month=${currentMonth}`),
            fetch(`/api/ai/insights?month=${currentMonth}`)
        ]);

        const incData = await incRes.json();
        const expData = await expRes.json();
        const aiData = await aiRes.json();

        const totalInc = incData.total_amount || 0;
        const totalExp = expData.total_amount || 0;
        const netSavings = totalInc - totalExp;
        const savingsRate = totalInc > 0 ? (netSavings / totalInc * 100).toFixed(1) : 0;

        document.getElementById('dashTotalIncome').textContent = `$${totalInc.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
        document.getElementById('dashIncomeCount').textContent = `${incData.incomes ? incData.incomes.length : 0} income entries`;
        document.getElementById('dashTotalExpenses').textContent = `$${totalExp.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
        document.getElementById('dashExpenseCount').textContent = `${expData.expenses ? expData.expenses.length : 0} transactions`;
        document.getElementById('dashNetSavings').textContent = `$${netSavings.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
        document.getElementById('dashSavingsRate').textContent = `${savingsRate}% Savings Rate`;

        // Overspend Status & AI Banner
        const statusEl = document.getElementById('dashBudgetStatus');
        const noticeEl = document.getElementById('dashOverspendNotice');
        const aiBanner = document.getElementById('aiBanner');
        const aiBannerText = document.getElementById('aiBannerText');

        if (aiData.overspend_flags && aiData.overspend_flags.length > 0) {
            const topOver = aiData.overspend_flags[0];
            statusEl.textContent = 'Attention Needed';
            statusEl.className = 'metric-value text-warning';
            noticeEl.textContent = `${topOver.category_name} is ${topOver.overspend_pct}% over budget`;

            if (aiBanner && aiBannerText) {
                aiBannerText.textContent = `⚠️ Overspend Alert: ${topOver.category_name} is ${topOver.overspend_pct}% over budget limit!`;
                aiBanner.style.display = 'flex';
            }
        } else {
            statusEl.textContent = 'On Track';
            statusEl.className = 'metric-value text-success';
            noticeEl.textContent = 'All categories within target limit';

            if (aiBanner && aiBannerText) {
                if (currentUser && currentUser.account_type === 'freelancer' && aiData.insights) {
                    const freeInsight = aiData.insights.find(i => i.title.includes('Freelancer'));
                    if (freeInsight) {
                        aiBannerText.textContent = `💼 ${freeInsight.title}: ${freeInsight.message}`;
                        aiBanner.style.display = 'flex';
                    } else {
                        aiBanner.style.display = 'none';
                    }
                } else {
                    aiBanner.style.display = 'none';
                }
            }
        }

        // Render Overview Insights
        renderOverviewInsights(aiData.insights || []);

        // Render Recent Transactions
        renderOverviewRecentTransactions(expData.expenses || []);

        // Render Charts
        renderCashflowChart(totalInc, totalExp, netSavings);
        renderCategoryChart(expData.expenses || []);

    } catch (err) {
        console.error('Error loading overview:', err);
    }
}

function renderOverviewInsights(insights, targetId = 'overviewInsightsList') {
    const list = document.getElementById(targetId);
    if (!list) return;
    list.innerHTML = '';

    if (!insights || insights.length === 0) {
        list.innerHTML = '<div class="insight-item">No active AI alerts for this period.</div>';
        return;
    }

    insights.slice(0, 5).forEach(item => {
        const div = document.createElement('div');
        div.className = `insight-item ${item.type || 'info'}`;
        div.innerHTML = `
            <div class="insight-title">${item.title}</div>
            <div class="insight-msg">${item.message}</div>
        `;
        list.appendChild(div);
    });
}

function renderOverviewRecentTransactions(expenses) {
    const body = document.getElementById('overviewRecentBody');
    if (!body) return;
    body.innerHTML = '';

    if (!expenses || expenses.length === 0) {
        body.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No transactions logged for this month.</td></tr>';
        return;
    }

    expenses.slice(0, 5).forEach(exp => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${exp.date}</td>
            <td>${exp.note || exp.category_name}</td>
            <td><span class="badge-pill" style="background: ${exp.category_color}25; color: ${exp.category_color}; border-color: ${exp.category_color}50">${exp.category_name}</span></td>
            <td class="text-danger">-$${exp.amount.toFixed(2)}</td>
        `;
        body.appendChild(tr);
    });
}

/* ==================== CHARTS RENDERING ==================== */
function renderCashflowChart(income, expenses, savings) {
    const ctx = document.getElementById('cashflowChart')?.getContext('2d');
    if (!ctx) return;

    if (cashflowChartInstance) cashflowChartInstance.destroy();

    cashflowChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Total Income', 'Total Expenses', 'Net Savings'],
            datasets: [{
                label: 'USD ($)',
                data: [income, expenses, Math.max(0, savings)],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.7)',
                    'rgba(239, 68, 68, 0.7)',
                    'rgba(99, 102, 241, 0.7)'
                ],
                borderColor: [
                    '#10b981',
                    '#ef4444',
                    '#6366f1'
                ],
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}

function renderCategoryChart(expenses) {
    const ctx = document.getElementById('categoryChart')?.getContext('2d');
    if (!ctx) return;

    if (categoryChartInstance) categoryChartInstance.destroy();

    const catTotals = {};
    const catColors = {};

    expenses.forEach(exp => {
        catTotals[exp.category_name] = (catTotals[exp.category_name] || 0) + exp.amount;
        catColors[exp.category_name] = exp.category_color || '#6366f1';
    });

    const labels = Object.keys(catTotals);
    const data = Object.values(catTotals);
    const bgColors = labels.map(l => catColors[l]);

    if (labels.length === 0) {
        labels.push('No Expenses');
        data.push(1);
        bgColors.push('rgba(255, 255, 255, 0.1)');
    }

    categoryChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: bgColors,
                borderWidth: 2,
                borderColor: '#0b0f19'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#94a3b8', font: { size: 11 } }
                }
            },
            cutout: '70%'
        }
    });
}

/* ==================== TAB 2: TRANSACTIONS ==================== */
async function loadTransactions() {
    try {
        const [incRes, expRes] = await Promise.all([
            fetch(`/api/income?month=${currentMonth}`),
            fetch(`/api/expenses?month=${currentMonth}`)
        ]);

        const incData = await incRes.json();
        const expData = await expRes.json();

        const allRecords = [];
        (incData.incomes || []).forEach(i => allRecords.push({ ...i, record_type: 'income' }));
        (expData.expenses || []).forEach(e => allRecords.push({ ...e, record_type: 'expense' }));

        // Sort by date desc
        allRecords.sort((a, b) => new Date(b.date_received || b.date) - new Date(a.date_received || a.date));

        allTransactions = allRecords;
        filterTransactions();
    } catch (err) {
        console.error('Error loading transactions:', err);
    }
}

function filterTransactions() {
    const query = (document.getElementById('txSearch')?.value || '').toLowerCase().trim();
    const typeFilter = document.getElementById('txTypeFilter')?.value || 'all';

    const filtered = allTransactions.filter(r => {
        if (typeFilter !== 'all' && r.record_type !== typeFilter) return false;
        if (!query) return true;
        const desc = (r.source || r.note || r.category_name || '').toLowerCase();
        const cat = (r.category_name || '').toLowerCase();
        const dateVal = (r.date_received || r.date || '').toLowerCase();
        const amt = (r.amount || '').toString();
        return desc.includes(query) || cat.includes(query) || dateVal.includes(query) || amt.includes(query);
    });

    renderTransactionsTable(filtered);
}

function renderTransactionsTable(records) {
    const tbody = document.getElementById('txTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (records.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No income or expense records match your search or filter.</td></tr>';
        return;
    }

    records.forEach(r => {
        const tr = document.createElement('tr');
        const isInc = r.record_type === 'income';
        const typeBadge = isInc ? '<span class="badge-pill" style="background: rgba(16,185,129,0.2); color:#10b981;">Income</span>'
                              : '<span class="badge-pill" style="background: rgba(239,68,68,0.2); color:#ef4444;">Expense</span>';
        
        const dateVal = r.date_received || r.date;
        const descVal = r.source || r.note || r.category_name;
        const catVal = isInc ? (r.is_recurring ? 'Recurring Income' : 'Variable Income') : r.category_name;
        const amtStr = isInc ? `+$${r.amount.toFixed(2)}` : `-$${r.amount.toFixed(2)}`;
        const amtClass = isInc ? 'text-success' : 'text-danger';

        tr.innerHTML = `
            <td>${typeBadge}</td>
            <td>${dateVal}</td>
            <td><strong>${descVal}</strong></td>
            <td>${catVal}</td>
            <td class="${amtClass}"><strong>${amtStr}</strong></td>
            <td>
                <button class="icon-btn" onclick="deleteRecord('${r.record_type}', ${r.id})">
                    <i data-feather="trash-2"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
    feather.replace();
}

async function deleteRecord(type, id) {
    if (!confirm(`Delete this ${type} record?`)) return;
    try {
        const endpoint = type === 'income' ? `/api/income/${id}` : `/api/expenses/${id}`;
        const res = await fetch(endpoint, { method: 'DELETE' });
        if (res.ok) {
            loadTransactions();
        }
    } catch (err) {
        alert('Delete failed');
    }
}

/* ==================== TAB 3: BUDGET MANAGER ==================== */
async function loadBudgetManager() {
    try {
        const res = await fetch(`/api/budget/${currentMonth}`);
        const data = await res.json();

        document.getElementById('budgetTotalTarget').textContent = `$${(data.total_budgeted || 0).toFixed(2)}`;
        document.getElementById('budgetTotalActual').textContent = `$${(data.total_actual || 0).toFixed(2)}`;
        const varAmt = (data.total_budgeted || 0) - (data.total_actual || 0);
        document.getElementById('budgetVariance').textContent = `$${varAmt.toFixed(2)}`;
        document.getElementById('budgetVariance').className = varAmt >= 0 ? 'metric-value text-success' : 'metric-value text-danger';

        // Update Account-Specific Advice
        const advEl = document.getElementById('budgetAccountAdvice');
        const tagEl = document.getElementById('budgetSmoothingTag');
        if (advEl && currentUser) {
            if (currentUser.account_type === 'freelancer') {
                advEl.textContent = "Freelancer Profile Active: Income is auto-smoothed using a 3-month rolling average to absorb low-earning months and maintain stable budget targets.";
            } else if (currentUser.account_type === 'student') {
                advEl.textContent = "Student Profile Active: Allocations prioritize essential housing and course materials (60% Essential, 25% Discretionary, 15% Savings).";
            } else if (currentUser.account_type === 'household') {
                advEl.textContent = "Household Profile Active: Category limits are calculated for joint family spending.";
            } else {
                advEl.textContent = "Individual Profile Active: Built-in 50/30/20 budgeting rule (50% Essential, 30% Discretionary, 20% Savings).";
            }
        }
        if (tagEl) {
            tagEl.textContent = (currentUser && currentUser.account_type === 'freelancer') ? '⚡ 3-Month Rolling Average Smoothing Active' : '';
        }

        renderBudgetCategories(data.budgets || []);
    } catch (err) {
        console.error('Error loading budget:', err);
    }
}

function renderBudgetCategories(budgets) {
    const container = document.getElementById('budgetCategoriesList');
    if (!container) return;
    container.innerHTML = '';

    if (budgets.length === 0) {
        container.innerHTML = '<div class="text-center text-muted padding-20">Click "Auto-Generate AI Monthly Budget" to compute smart category limits.</div>';
        return;
    }

    budgets.forEach(b => {
        const div = document.createElement('div');
        div.className = 'budget-item';

        const barClass = b.is_over ? 'overbudget' : (b.spent_pct > 85 ? 'warning' : '');
        const badge = b.is_over ? `<span class="badge-pill" style="background:rgba(239,68,68,0.2); color:#ef4444;">Over by $${Math.abs(b.remaining_amount).toFixed(2)} (${b.spent_pct}%)</span>`
                                : `<span class="badge-pill">${b.spent_pct}% used ($${b.remaining_amount.toFixed(2)} left)</span>`;

        div.innerHTML = `
            <div class="budget-info">
                <div class="budget-cat-name">
                    <span style="color: ${b.category_color}">■</span> ${b.category_name} (${b.category_type})
                </div>
                <div>
                    <strong>$${b.spent_amount.toFixed(2)}</strong> / $${b.limit_amount.toFixed(2)} ${badge}
                </div>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar-fill ${barClass}" style="width: ${Math.min(100, b.spent_pct)}%; background: ${b.category_color};"></div>
            </div>
        `;
        container.appendChild(div);
    });
}

/* ==================== TAB 4: SAVINGS GOALS ==================== */
async function loadSavingsGoals() {
    try {
        const res = await fetch('/api/savings-goals');
        const data = await res.json();

        document.getElementById('savingsTotalTarget').textContent = `$${(data.total_target || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
        document.getElementById('savingsTotalSaved').textContent = `$${(data.total_saved || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}`;

        const overallPct = data.total_target > 0 ? (data.total_saved / data.total_target * 100).toFixed(1) : 0;
        document.getElementById('savingsOverallBar').style.width = `${Math.min(100, overallPct)}%`;
        document.getElementById('savingsOverallPct').textContent = `${overallPct}% overall goal progress`;

        renderSavingsGoalCards(data.goals || []);
    } catch (err) {
        console.error('Error loading savings goals:', err);
    }
}

function renderSavingsGoalCards(goals) {
    const grid = document.getElementById('goalsGrid');
    if (!grid) return;
    grid.innerHTML = '';

    if (goals.length === 0) {
        grid.innerHTML = '<div class="glass-card text-center text-muted padding-20">No savings goals created yet. Use the form above to set your first goal!</div>';
        return;
    }

    goals.forEach(g => {
        const card = document.createElement('div');
        card.className = 'glass-card goal-card';
        card.innerHTML = `
            <div class="card-header">
                <h3><i data-feather="target" class="text-success"></i> ${g.goal_name}</h3>
                <span class="badge-pill">${g.progress_pct}%</span>
            </div>
            <div>
                <h2>$${g.current_amount.toFixed(2)} <span class="text-muted" style="font-size: 14px;">/ $${g.target_amount.toFixed(2)}</span></h2>
                <div class="progress-bar-container margin-top">
                    <div class="progress-bar-fill success-fill" style="width: ${g.progress_pct}%;"></div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;" class="margin-top">
                <span class="text-muted" style="font-size: 12px;">Target: ${g.target_date || 'Ongoing'}</span>
                <div>
                    <button class="btn btn-outline-glow btn-sm" onclick="openDepositModal(${g.id}, '${g.goal_name}')">
                        <i data-feather="plus"></i> Deposit
                    </button>
                    <button class="icon-btn" onclick="deleteSavingsGoal(${g.id})">
                        <i data-feather="trash-2"></i>
                    </button>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
    feather.replace();
}

function openDepositModal(id, name) {
    document.getElementById('depositGoalId').value = id;
    document.getElementById('depositGoalName').textContent = name;
    document.getElementById('depositModal').style.display = 'flex';
}
function closeDepositModal() {
    document.getElementById('depositModal').style.display = 'none';
}

async function deleteSavingsGoal(id) {
    if (!confirm('Delete this savings goal?')) return;
    try {
        const res = await fetch(`/api/savings-goals/${id}`, { method: 'DELETE' });
        if (res.ok) loadSavingsGoals();
    } catch (err) {
        alert('Delete failed');
    }
}

/* ==================== TAB 5: MONTHLY REPORT ==================== */
async function loadMonthlyReport() {
    try {
        const res = await fetch(`/api/reports/${currentMonth}`);
        const data = await res.json();

        document.getElementById('reportMonthTitle').textContent = `Month: ${data.month}`;
        document.getElementById('reportUserName').textContent = data.user_name;
        document.getElementById('reportAccountType').textContent = (data.account_type || 'individual').toUpperCase();

        document.getElementById('repIncome').textContent = `$${(data.summary.total_income || 0).toFixed(2)}`;
        document.getElementById('repExpenses').textContent = `$${(data.summary.total_expenses || 0).toFixed(2)}`;
        document.getElementById('repSavings').textContent = `$${(data.summary.total_savings || 0).toFixed(2)}`;
        document.getElementById('repSavingsRate').textContent = `${data.summary.savings_rate}%`;

        // Category Breakdown Table
        const catBody = document.getElementById('repCategoryBody');
        catBody.innerHTML = '';
        if (data.category_breakdown && data.category_breakdown.length > 0) {
            data.category_breakdown.forEach(c => {
                const tr = document.createElement('tr');
                const pct = data.summary.total_expenses > 0 ? (c.amount / data.summary.total_expenses * 100).toFixed(1) : 0;
                tr.innerHTML = `
                    <td>${c.name}</td>
                    <td class="text-right">$${c.amount.toFixed(2)}</td>
                    <td class="text-right">${pct}%</td>
                `;
                catBody.appendChild(tr);
            });
        } else {
            catBody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No expenses recorded for this report.</td></tr>';
        }

        // Insights List
        renderOverviewInsights(data.insights || [], 'repInsightsList');
    } catch (err) {
        console.error('Error loading report:', err);
    }
}

/* ==================== TAB 6: AI ASSISTANT ==================== */
async function loadAIAdvisor() {
    try {
        const res = await fetch(`/api/ai/insights?month=${currentMonth}`);
        const data = await res.json();

        const container = document.getElementById('aiDiagnosticsList');
        if (!container) return;
        container.innerHTML = '';

        (data.insights || []).forEach(item => {
            const div = document.createElement('div');
            div.className = `insight-item ${item.type || 'info'}`;
            div.innerHTML = `
                <div class="insight-title">${item.title}</div>
                <div class="insight-msg">${item.message}</div>
            `;
            container.appendChild(div);
        });
    } catch (err) {
        console.error('Error loading AI insights:', err);
    }
}

function sendQuickPrompt(text) {
    document.getElementById('chatPrompt').value = text;
    document.getElementById('chatForm').dispatchEvent(new Event('submit'));
}

function appendChatMessage(sender, text) {
    const box = document.getElementById('chatMessages');
    if (!box) return;

    const div = document.createElement('div');
    div.className = `chat-bubble ${sender === 'user' ? 'user-bubble' : 'bot-bubble'}`;
    const headerIcon = sender === 'user' ? '<i data-feather="user"></i> You' : '<i data-feather="cpu"></i> Advisor Bot';
    
    div.innerHTML = `
        <div class="bubble-header" style="font-weight: 600; font-size: 11px; opacity: 0.8; margin-bottom: 4px;">${headerIcon}</div>
        <div class="bubble-content" style="white-space: pre-wrap;">${text}</div>
    `;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
    feather.replace();
}

/* ==================== TAB 7: HOUSEHOLD ==================== */
async function loadHousehold() {
    try {
        const res = await fetch('/api/household/summary');
        const data = await res.json();

        const joinCreateBox = document.getElementById('householdJoinCreateBox');
        const activeView = document.getElementById('householdActiveView');

        if (!data.has_household) {
            joinCreateBox.style.display = 'block';
            activeView.style.display = 'none';
        } else {
            joinCreateBox.style.display = 'none';
            activeView.style.display = 'block';

            document.getElementById('householdTitle').textContent = data.household_name;
            document.getElementById('householdInviteCodeDisplay').textContent = data.invite_code;

            document.getElementById('hhTotalIncome').textContent = `$${(data.total_income || 0).toFixed(2)}`;
            document.getElementById('hhTotalExpenses').textContent = `$${(data.total_expenses || 0).toFixed(2)}`;
            document.getElementById('hhTotalSavings').textContent = `$${(data.total_savings || 0).toFixed(2)}`;

            const grid = document.getElementById('hhMembersGrid');
            grid.innerHTML = '';

            (data.members || []).forEach(m => {
                const card = document.createElement('div');
                card.className = 'glass-card';
                card.innerHTML = `
                    <h3>${m.name}</h3>
                    <div style="margin-top: 10px;">
                        <p class="text-success">Income: $${m.income.toFixed(2)}</p>
                        <p class="text-danger">Expenses: $${m.expenses.toFixed(2)}</p>
                        <p><strong>Net Savings: $${m.savings.toFixed(2)}</strong></p>
                    </div>
                `;
                grid.appendChild(card);
            });
        }
    } catch (err) {
        console.error('Error loading household:', err);
    }
}
