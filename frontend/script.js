// API基础URL
const API_BASE = '/api';

// DOM元素
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const loginContainer = document.getElementById('login-form');
const registerContainer = document.getElementById('register-form');
const profileContainer = document.getElementById('user-profile');
const messageDiv = document.getElementById('message');

// 页面加载时检查是否已登录
document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('authToken');
    if (token) {
        loadUserProfile();
    }
});

// 登录表单提交
loginForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(loginForm);
    const loginData = {
        username: formData.get('username'),
        password: formData.get('password')
    };

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(loginData)
        });

        const result = await response.json();

        if (response.ok) {
            // 登录成功
            localStorage.setItem('authToken', result.access_token);
            localStorage.setItem('user', JSON.stringify(result.user));
            showMessage('登录成功！', 'success');
            showProfile(result.user);
        } else {
            // 登录失败
            showMessage(result.detail || '登录失败', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showMessage('网络错误，请稍后重试', 'error');
    }
});

// 注册表单提交
registerForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(registerForm);
    const password = formData.get('password');
    const confirmPassword = formData.get('confirmPassword');

    // 验证密码确认
    if (password !== confirmPassword) {
        showMessage('两次输入的密码不一致', 'error');
        return;
    }

    const registerData = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: password
    };

    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(registerData)
        });

        const result = await response.json();

        if (response.ok) {
            // 注册成功
            localStorage.setItem('authToken', result.access_token);
            localStorage.setItem('user', JSON.stringify(result.user));
            showMessage('注册成功！', 'success');
            showProfile(result.user);
        } else {
            // 注册失败
            showMessage(result.detail || '注册失败', 'error');
        }
    } catch (error) {
        console.error('Register error:', error);
        showMessage('网络错误，请稍后重试', 'error');
    }
});

// 切换到注册表单
function switchToRegister() {
    loginContainer.classList.remove('active');
    registerContainer.classList.add('active');
    profileContainer.classList.remove('active');
    clearForms();
}

// 切换到登录表单
function switchToLogin() {
    registerContainer.classList.remove('active');
    loginContainer.classList.add('active');
    profileContainer.classList.remove('active');
    clearForms();
}

// 显示用户信息页面
function showProfile(user) {
    loginContainer.classList.remove('active');
    registerContainer.classList.remove('active');
    profileContainer.classList.add('active');
    
    const profileInfo = document.getElementById('profileInfo');
    profileInfo.innerHTML = `
        <div class="profile-item">
            <span class="profile-label">用户ID:</span>
            <span class="profile-value">${user.id}</span>
        </div>
        <div class="profile-item">
            <span class="profile-label">用户名:</span>
            <span class="profile-value">${user.username}</span>
        </div>
        <div class="profile-item">
            <span class="profile-label">邮箱:</span>
            <span class="profile-value">${user.email}</span>
        </div>
        <div class="profile-item">
            <span class="profile-label">注册时间:</span>
            <span class="profile-value">${user.created_at ? new Date(user.created_at).toLocaleString('zh-CN') : '未知'}</span>
        </div>
    `;
}

// 加载用户信息
async function loadUserProfile() {
    const token = localStorage.getItem('authToken');
    if (!token) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/profile`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const result = await response.json();
            showProfile(result);
        } else {
            // Token无效，清除本地存储
            localStorage.removeItem('authToken');
            localStorage.removeItem('user');
            switchToLogin();
        }
    } catch (error) {
        console.error('Load profile error:', error);
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        switchToLogin();
    }
}

// 退出登录
function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    showMessage('已退出登录', 'info');
    switchToLogin();
}

// 显示消息
function showMessage(text, type = 'info') {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.classList.add('show');
    
    // 3秒后自动隐藏
    setTimeout(() => {
        messageDiv.classList.remove('show');
    }, 3000);
}

// 清空表单
function clearForms() {
    loginForm.reset();
    registerForm.reset();
}

// 输入验证
document.getElementById('registerPassword').addEventListener('input', function() {
    const password = this.value;
    const confirmPassword = document.getElementById('confirmPassword');
    
    if (password.length < 6) {
        this.setCustomValidity('密码长度至少为6位');
    } else {
        this.setCustomValidity('');
    }
    
    // 检查确认密码
    if (confirmPassword.value && confirmPassword.value !== password) {
        confirmPassword.setCustomValidity('两次输入的密码不一致');
    } else {
        confirmPassword.setCustomValidity('');
    }
});

document.getElementById('confirmPassword').addEventListener('input', function() {
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = this.value;
    
    if (confirmPassword !== password) {
        this.setCustomValidity('两次输入的密码不一致');
    } else {
        this.setCustomValidity('');
    }
});