function changePage(pageNum) {
    const url = new URL(window.location.href);
    url.searchParams.set('page', pageNum);
    window.location.href = url.toString();
}

function openDeleteModal(uuid) {
    const modal = document.getElementById('deleteModal');
    const form = document.getElementById('deleteForm');
    form.action = `/admin/users/delete/${uuid}`;
    modal.style.display = 'block';
}

function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    modal.style.display = 'none';
}

async function checkUsername() {
    const usernameInput = document.getElementById('username');
    const messageSpan = document.getElementById('username-message');
    const username = usernameInput.value.trim();
    if (!username) {
        messageSpan.textContent = '用户名不能为空';
        messageSpan.style.color = 'red';
        return;
    }
    try {
        const response = await fetch(`/admin/users/validate_username?username=${encodeURIComponent(username)}`);
        const data = await response.json();
        if (data.valid) {
            messageSpan.textContent = data.message;
            messageSpan.style.color = 'green';
        } else {
            messageSpan.textContent = data.message;
            messageSpan.style.color = 'red';
        }
    } catch (error) {
        messageSpan.textContent = '验证失败，请稍后重试';
        messageSpan.style.color = 'red';
    }
}

function updateRoleForm() {
    const role = document.getElementById('role-select').value;
    const roleForm = document.getElementById('role-form');
    roleForm.innerHTML = '';
    if (role === 'patient') {
        roleForm.innerHTML = `
            <label for="name">姓名:</label>
            <input type="text" name="name" placeholder="姓名" required>
            <label for="gender">性别:</label>
            <select name="gender" required>
                <option value="">选择性别</option>
                <option value="男">男</option>
                <option value="女">女</option>
            </select>
            <label for="age">年龄:</label>
            <input type="number" name="age" placeholder="年龄" required>
            <label for="contact_number">联系方式:</label>
            <input type="text" name="contact_number" placeholder="联系方式" required>
        `;
    } else if (role === 'worker') {
        roleForm.innerHTML = `
            <label for="name">姓名:</label>
            <input type="text" name="name" placeholder="姓名" required>
            <label for="age">年龄:</label>
            <input type="number" name="age" placeholder="年龄" required>
            <label for="contact_number">联系方式:</label>
            <input type="text" name="contact_number" placeholder="联系方式" required>
        `;
    } else if (role === 'admin') {
        roleForm.innerHTML = `
            <label for="name">姓名:</label>
            <input type="text" name="name" placeholder="姓名" required>
            <label for="contact_number">联系方式:</label>
            <input type="text" name="contact_number" placeholder="联系方式" required>
        `;
    }
}